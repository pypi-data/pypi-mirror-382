# ======================================================================
# (A) FILE PATH & IMPORT PATH
# depths/cli/cli.py  →  import path: depths.cli.cli
# ======================================================================

# ======================================================================
# (B) FILE OVERVIEW (concept & significance in v0.1.2)
# Typer-based command-line interface to manage the OTLP/HTTP server:
#   • init   → create a new instance layout and baseline configs
#   • start  → run uvicorn serving depths.cli.app:app (foreground/background)
#   • stop   → terminate a background server via stored PID
#
# The CLI is the operational companion to the service: it standardizes
# instance paths, boot flags, and safe shutdown across platforms.
# ======================================================================

# ======================================================================
# (C) IMPORTS & GLOBALS (what & why)
# typer                         → ergonomic CLI commands/options
# os, sys, subprocess, signal   → process control & environment
# Path                          → instance directories & pid/log files
#
# Globals:
#   app                 → Typer root application
#   DEFAULT_HOST/PORT   → sensible defaults for OTLP/HTTP binding
# Helper:
#   _instance_paths()   → canonical layout of per-instance paths
# ======================================================================

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from contextlib import contextmanager
import sys
import multiprocessing as mp

from depths.core.config import S3Config, DepthsLoggerOptions
from depths.core.logger import DepthsLogger

import polars as pl
import typer
import httpx
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


app = typer.Typer(help="depths CLI")

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 4318 


def _instance_paths(instance_id: str, instance_dir: Path) -> dict:
    """
    Compute canonical paths for an instance (root, config dir, pid file, log file).

    Overview (v0.1.2 role):
        Normalizes how the CLI and server agree on where to read/write artifacts.
        Ensures the configs directory exists.

    Args:
        instance_id: Logical instance identifier.
        instance_dir: Base directory containing all instances.

    Returns:
        Dict with keys: {'root', 'cfg', 'pid', 'log'}.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Keep names stable; app.py reads DEPTHS_INSTANCE_* env vars set by 'start'.

    inst_root = instance_dir / instance_id
    cfg_dir = inst_root / "configs"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    pid_file = cfg_dir / "server.pid"
    log_file = inst_root / "server.log"
    return {"root": inst_root, "cfg": cfg_dir, "pid": pid_file, "log": log_file}

@contextmanager
def _status(msg: str="Please wait..."):
    """
    Lightweight spinner using Rich if available; falls back to plain text.
    """
    # - Displays a loading spinner from Rich.
    from rich.console import Console  
    try:
        
        with Console().status(msg, spinner="dots"):
            yield
    except Exception:
        typer.echo(msg)
        yield

def _init_process(
    instance_id: str = typer.Option("default", "--instance-id", "-I", help="Unique ID for this depths instance"),
    instance_dir: Path = typer.Option(Path("./depths_data"), "--dir", "-D", help="Root directory to store local data"),
):
    """
    Run the heavy bootstrap in a clean child process so the parent CLI
    can keep a spinner and return immediately after success.
    """
    # - Leverages the init_early_terminate parameter in DepthsLoggerOptions for faster `depths init` experience

    
    s3 = None
    try:
        s3 = S3Config.from_env()
    except Exception:
        s3 = None
    DepthsLogger(instance_id=instance_id, instance_dir=str(instance_dir), s3=s3, options=DepthsLoggerOptions(init_early_terminate=True))

@app.command("init")
def init(
    instance_id: str = typer.Option("default", "--instance-id", "-I", help="Unique ID for this depths instance"),
    instance_dir: Path = typer.Option(Path("./depths_data"), "--dir", "-D", help="Root directory to store local data"),
):
    """
    Initialize a new Depths instance on disk.

    Overview (v0.1.2 role):
        Creates the directory skeleton and baseline configs by instantiating a
        DepthsLogger once (which lays out configs/ and index/). S3 config is
        optional; local-only is supported.

    Args:
        instance_id: Name for the instance root folder.
        instance_dir: Parent directory under which the instance folder is created.

    Returns:
        None (prints status and tips; exits with non-zero on pre-existence).
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Mirrors DepthsLogger's on-disk structure; does not start the server.
    # - S3Config.from_env() may fail; we swallow to allow local bootstrap.
    # - Attempted context manager for loading type context.
    
    if (instance_dir / instance_id).exists():
        typer.echo(f"Instance '{instance_id}' already exists at {(instance_dir / instance_id)}", err=True)
        raise typer.Exit(code=1)
    
    _instance_paths(instance_id, instance_dir)
    ctx=mp.get_context("spawn")
    proc=ctx.Process(
        target=_init_process,
        args=(instance_id, str(instance_dir)),
        name="depths-init",
        daemon=False
    )  

    with _status("Creating instance layout and baseline configs..."):
        proc.start()
        proc.join()
    
    if proc.exitcode!=0:
        typer.echo(
+            f"Initialization failed (exit code {proc.exitcode}). "
            f"Check logs under {(instance_dir / instance_id)}.",
            err=True,
        )
        raise typer.Exit(code=proc.exitcode or 1)
        
    typer.echo(f"Initialized depths instance '{instance_id}' at {(instance_dir / instance_id)}")
    typer.echo("Tip: set your S3 env vars if you want S3 persistence.")
    try:
        sys.stdout.flush()
    except Exception:
        pass

@app.command("start")
def start(
    instance_id: str = typer.Option("default", "--instance-id","-I", help="Instance to start"),
    instance_dir: Path = typer.Option(Path("./depths_data"), "--dir","-D", help="Root directory for instance data"),
    host: str = typer.Option(DEFAULT_HOST, "--host","-H", help="Bind host for OTLP/HTTP"),
    port: int = typer.Option(DEFAULT_PORT, "--port","-P", help="Bind port for OTLP/HTTP (4318 by spec)"),
    reload: bool = typer.Option(False, "--reload", "-R", help="Auto-reload server on code changes"),
    foreground: bool = typer.Option(False, "--foreground", "-F", help="Run in foreground and show Uvicorn TUI logs"),
):
    """
    Start the OTLP/HTTP server (depths.cli.app:app) via uvicorn.

    Overview (v0.1.2 role):
        Offers two modes:
          • Foreground: run uvicorn in-process (best signals; interactive logs).
          • Background: daemonize uvicorn, write pidfile, and append logs.

    Args:
        instance_id: Instance to serve.
        instance_dir: Parent directory containing the instance folder.
        host: Bind address (default 0.0.0.0).
        port: Bind port (OTLP/HTTP default 4318).
        reload: Enable code reload (only supported with --foreground).
        foreground: Do not daemonize; run in the current terminal.

    Returns:
        None (prints process info and where logs live).

    Raises:
        typer.Exit: On invalid state (missing instance, existing pidfile, bad flags).
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - For background mode, we write DEPTHS_INSTANCE_* env so the app module
    #   can discover the intended instance from within the uvicorn process.
    # - We attempt to pick the serving PID (child) when possible (psutil).
    # - Reload spawns children; in background it confuses PID tracking—hence disallowed.
    # - PID selection logic: Most recent child is typically the server

    instance_dir = instance_dir.resolve()

    if not (instance_dir / instance_id).exists():
        typer.echo(
            f"Instance '{instance_id}' does not exist at {(instance_dir / instance_id)}. "
            f"Run 'depths init -I {instance_id}' first.",
            err=True,
        )
        raise typer.Exit(code=1)

    paths = _instance_paths(instance_id, instance_dir)

    os.environ["DEPTHS_INSTANCE_ID"] = instance_id
    os.environ["DEPTHS_INSTANCE_DIR"] = str(instance_dir)

    if foreground:
        import uvicorn
        typer.echo(f"Starting depths server for '{instance_id}' on http://{host}:{port} (foreground)...")
        uvicorn.run(
            "depths.cli.app:app",
            host=host,
            port=port,
            log_level="info",
            reload=reload,
        )
        return

    if reload:
        typer.echo("`--reload` is only supported with `--foreground` to ensure correct PID handling.", err=True)
        raise typer.Exit(code=2)

    if paths["pid"].exists():
        typer.echo(f"Server already running (pid file {paths['pid']}).", err=True)
        raise typer.Exit(code=1)

    env = os.environ.copy()
    cmd = [
        sys.executable, "-m", "uvicorn", "depths.cli.app:app",
        "--host", host, "--port", str(port),
        "--log-level", "info",
    ]

    logf = open(paths["log"], "a", encoding="utf-8")
    proc = subprocess.Popen(cmd, env=env, stdout=logf, stderr=logf, close_fds=True)

    serving_pid = proc.pid
    try:
        import time
        time.sleep(0.35)  
        try:
            import psutil  
            p = psutil.Process(proc.pid)
            kids = p.children(recursive=True)
            if kids:
                serving_pid = kids[-1].pid  
        except Exception:
            pass
    finally:
        paths["pid"].write_text(str(serving_pid))

    typer.echo(f"Started depths server for '{instance_id}' on http://{host}:{port} (pid={serving_pid}). Logs: {paths['log']}")

@app.command("view")
def view(
    instance_id: str = typer.Option("default", "--instance-id", "-I", help="Instance to read from"),
    instance_dir: Path = typer.Option(Path("./depths_data"), "--dir", "-D", help="Root directory for instance data"),
    storage: str = typer.Option("auto", "--storage", "-S", help="Storage backend to read from: auto | local | s3"),
    rows: int = typer.Option(10, "--rows", "-n", min=1, help="Show the latest N rows by event_ts (default: 10)"),
    table: str | None = typer.Option(None, "--table", "-t", help="One of: spans | span_events | span_links | logs | metrics_points | metrics_hist"),
    select: list[str] | None = typer.Option(None, "--select", "-s", help="Column to include (repeatable). Example: -s trace_id -s span_id"),
    date_from: str | None = typer.Option(None, "--date-from", help="Start UTC date YYYY-MM-DD (inclusive)"),
    date_to: str | None = typer.Option(None, "--date-to", help="End UTC date YYYY-MM-DD (inclusive)"),
):
    """
    View the latest N persisted rows from an OTel table (pretty-printed).

    Overview (v0.1.1 role):
        Reads from the chosen table via the logger's lazy readers, sorts by
        `event_ts` descending, limits to N, and materializes to a Polars
        DataFrame for terminal display. Supports local or S3 reads based on
        environment and the --storage flag.

    Args:
        instance_id: Logical instance name under --dir.
        instance_dir: Base directory that contains the instance folder.
        storage: 'auto' | 'local' | 's3' source selection.
        rows: Number of latest rows to display (sorted by event_ts desc).
        table: Table name; if omitted an interactive selection is shown.
        select: Optional list of columns to include (repeat --select).
        date_from/date_to: Optional day range (YYYY-MM-DD).

    Returns:
        None. Prints a table or a friendly message if no rows found.

    Raises:
        typer.Exit: On invalid instance, bad table selection, or read errors.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Uses the generic *_lazy() readers to keep this command decoupled from
    #   per-table named predicate APIs. Sorting/limit is applied BEFORE any
    #   projection so it works even if 'select' omits event_ts.
    # - We avoid starting background threads by disabling auto_start and shipper.
    # - Multiple --select values are supported by declaring the option as a
    #   list[str] (Typer delegates to Click to collect multiple occurrences).
    # - For S3 reads, the logger must have S3Config; we try S3Config.from_env()
    #   and fall back gracefully if env is incomplete.

    allowed = {
        "1": "spans",
        "2": "span_events",
        "3": "span_links",
        "4": "logs",
        "5": "metrics_points",
        "6": "metrics_hist",
        "spans": "spans",
        "span_events": "span_events",
        "span_links": "span_links",
        "logs": "logs",
        "metrics_points": "metrics_points",
        "metrics_hist": "metrics_hist",
    }
    pretty_names = {
        "spans": "Spans",
        "span_events": "Span Events",
        "span_links": "Span Links",
        "logs": "Logs",
        "metrics_points": "Metric Points",
        "metrics_hist": "Metric Histograms",
    }

    inst_root = instance_dir / instance_id
    if not inst_root.exists():
        typer.echo(f"Instance '{instance_id}' not found at {inst_root}", err=True)
        raise typer.Exit(code=1)

    if table:
        key = table.strip().lower()
        sel = allowed.get(key)
        if not sel:
            typer.echo("Invalid --table. Choose one of: spans | span_events | span_links | logs | metrics_points | metrics_hist", err=True)
            raise typer.Exit(code=2)
        table_name = sel
    else:
        typer.echo("Select OTel table to view:")
        for i, key in enumerate(["spans","span_events","span_links","logs","metrics_points","metrics_hist"], start=1):
            typer.echo(f"  {i}. {pretty_names[key]}")
        choice = typer.prompt("Enter a number (1-6)", default=1)
        sel = allowed.get(str(choice).strip())
        if not sel:
            typer.echo("Invalid selection.", err=True)
            raise typer.Exit(code=2)
        table_name = sel

    with _status("Fetching telemetry rows..."):
        try:
            s3 = None
            try:
                s3 = S3Config.from_env()
            except Exception:
                s3 = None
            opts = DepthsLoggerOptions(
                auto_start=False,
                install_signal_handlers=False,
                lazy_start_on_first_log=False,
                atexit_hook=False,
                shipper_enabled=False,
            )
            logger = DepthsLogger(instance_id=instance_id, instance_dir=str(instance_dir), s3=s3, options=opts)
        except Exception as e:
            typer.echo(f"Failed to construct DepthsLogger: {e}", err=True)
            raise typer.Exit(code=3)

        try:
            
            lf = getattr(logger, f"{table_name}_lazy")(date_from=date_from, date_to=date_to, storage=storage)
            lf = lf.sort("event_ts", descending=True).limit(int(rows))
            if select:
                lf = lf.select([pl.col(c) for c in select])
            df = lf.collect()
        except Exception as e:
            typer.echo(f"Failed to read {table_name}: {e}", err=True)
            raise typer.Exit(code=4)

    if df.height == 0:
        typer.echo(f"No rows found in {pretty_names[table_name]} for the selected range.")
        raise typer.Exit(code=0)

    typer.echo(f"{pretty_names[table_name]} · latest {min(rows, df.height)} rows (event_ts desc)")
    typer.echo(str(df))

@app.command("status")
def status(
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="Host of the running depths server"),
    port: int = typer.Option(4318, "--port", "-P", help="Port of the running depths server"),
    timeout: float = typer.Option(5.0, "--timeout", "-T", help="HTTP timeout in seconds"),
):
    """
    Show a colorized health snapshot of the running depths server.

    Overview (v0.1.1):
        Calls FastAPI `/healthz`, then renders producer & aggregator metrics
        with Rich. Green for healthy indicators; red for problematic.

    Args:
        host: Host used by `depths start`.
        port: Port used by `depths start`.
        timeout: HTTP timeout for `/healthz`.

    Returns:
        None. Prints a formatted view; exits non-zero on failure.

    Raises:
        typer.Exit: On connection/parse errors or non-200 responses.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Uses httpx for HTTP with explicit timeout and .raise_for_status().
    #   Request-time issues raise httpx.RequestError; non-2xx raises
    #   httpx.HTTPStatusError via raise_for_status(); timeouts raise
    #   httpx.TimeoutException (a RequestError subclass). 
    # - Rich Panel/Table are used for clean terminal UI; border_style/title
    #   and add_column/add_row are the idiomatic APIs. 
    # - HTTP is wrapped with _status for clean loading status

    

    url = f"http://{host}:{port}/healthz"
    console = Console()


    with _status("Fetching live health stats..."):
        try:
            resp = httpx.get(url, timeout=timeout)
            resp.raise_for_status()  
        except httpx.TimeoutException as e:
            console.print(f"[bold red]Timed out[/bold red] connecting to {url} after {timeout}s: {e}")
            raise typer.Exit(code=3)
        except httpx.RequestError as e:
            console.print(f"[bold red]Request error[/bold red] contacting {url}: {e}")
            raise typer.Exit(code=3)
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]HTTP {e.response.status_code}[/bold red] from {url}")
            raise typer.Exit(code=3)

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            console.print(f"[bold red]Invalid JSON[/bold red] from {url}: {e}")
            raise typer.Exit(code=3)

        ok = bool(data.get("ok"))
        logger = data.get("logger") or {}

        started = bool(logger.get("started", False))
        overall_ok = started
        for _name, m in (logger.get("aggregators") or {}).items():
            if not m.get("delta_init_ok", False) or m.get("delta_last_error"):
                overall_ok = False
                break

        inst = logger.get("instance_id", "unknown")
        day = logger.get("current_day_utc", "unknown")
        header = Text.assemble(
            ("Depths ", "bold"),
            ("status  ", "dim"),
            (f"http://{host}:{port}", "cyan"),
            "\n",
            ("instance: ", "dim"), (str(inst), "bold"),
            ("   day: ", "dim"), (str(day), "bold"),
            ("   started: ", "dim"), (str(bool(started)), "bold green" if started else "bold red"),
        )
    
    
    console.print(Panel(header, title="[bold]Health[/bold]", border_style="green" if overall_ok else "red"))

    prod = logger.get("producers") or {}
    if isinstance(prod, dict) and prod:
        t = Table(title="Producers", expand=True)
        t.add_column("Table", style="bold")
        t.add_column("Accepted", justify="right")
        t.add_column("Schema↓", justify="right")
        t.add_column("Payload↓", justify="right")
        t.add_column("Date↓", justify="right")
        t.add_column("Dropped", justify="right")
        t.add_column("Queue", justify="right")
        t.add_column("Oldest Age (s)", justify="right")
        for name, m in sorted(prod.items()):
            qsize = int(m.get("queue_size") or 0)
            dropped = int(m.get("dropped_capacity") or 0)
            q_style = "red" if qsize > 0 else "green"
            d_style = "red" if dropped > 0 else "green"
            t.add_row(
                name,
                str(m.get("accepted", 0)),
                str(m.get("rejected_schema", 0)),
                str(m.get("rejected_payload_json", 0)),
                str(m.get("rejected_date_mismatch", 0)),
                f"[{d_style}]{dropped}[/{d_style}]",
                f"[{q_style}]{qsize}[/{q_style}]",
                f"{m.get('oldest_age_seconds', '0')}",
            )
        console.print(t)
    else:
        console.print("[yellow]No producer metrics available[/yellow]")

    aggs = logger.get("aggregators") or {}
    if isinstance(aggs, dict) and aggs:
        t = Table(title="Aggregators", expand=True)
        t.add_column("Table", style="bold")
        t.add_column("Flushes", justify="right")
        t.add_column("Sched Total", justify="right")
        t.add_column("Persisted", justify="right")
        t.add_column("Last Flush Rows", justify="right")
        t.add_column("Last Commit (s)", justify="right")
        t.add_column("Writer Q", justify="right")
        t.add_column("Delta OK", justify="center")
        t.add_column("Last Error", justify="left")
        t.add_column("Table Path", overflow="fold")

        for name, m in sorted(aggs.items()):
            wq = int(m.get("writer_queue_size") or 0)
            ok_flag = bool(m.get("delta_init_ok"))
            err = m.get("delta_last_error")
            wq_style = "red" if wq > 0 else "green"
            ok_style = "green" if ok_flag else "red"
            err_cell = f"[red]{err}[/red]" if err else "[green]-[/green]"
            t.add_row(
                name,
                str(m.get("flushes", 0)),
                str(m.get("rows_scheduled_total", 0)),
                str(m.get("rows_persisted_total", 0)),
                str(m.get("rows_last_flush", 0)),
                str(m.get("last_commit_seconds", "")),
                f"[{wq_style}]{wq}[/{wq_style}]",
                f"[{ok_style}]{ok_flag}[/{ok_style}]",
                err_cell,
                str(m.get("table_path", "")),
            )
        console.print(t)
    else:
        console.print("[yellow]No aggregator metrics available[/yellow]")

    if not overall_ok:
        raise typer.Exit(code=4)

@app.command("stop")
def stop(
    instance_id: str = typer.Option("default", "--instance-id", "-I", help="Instance to stop"),
    instance_dir: Path = typer.Option(Path("./depths_data"), "--dir", "-D", help="Root directory for instance data"),
    force: bool = typer.Option(False, "--force", "-F", help="Force kill if graceful stop fails"),
):
    """
    Stop a background server using the stored PID (and children when possible).

    Overview (v0.1.2 role):
        Reads the pidfile emitted by 'start', sends terminate/kill as needed,
        and cleans up the pidfile.

    Args:
        instance_id: Instance whose server should be stopped.
        instance_dir: Parent directory containing the instance.
        force: Escalate to SIGKILL (where available) on failure.

    Returns:
        None (prints result; exits non-zero on failures).

    Raises:
        typer.Exit: On missing/invalid pidfile or kill errors.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Prefers psutil to terminate the whole process tree (children before parent).
    # - Falls back to os.kill when psutil isn't available (best-effort).
    # - Always attempt to unlink the pidfile at the end.

    instance_dir = instance_dir.resolve()
    paths = _instance_paths(instance_id, instance_dir)

    if not paths["pid"].exists():
        typer.echo("No pid file found; server not running?", err=True)
        raise typer.Exit(code=1)

    try:
        pid = int(paths["pid"].read_text().strip())
    except Exception:
        typer.echo("Invalid pid file.", err=True)
        raise typer.Exit(code=1)

    try:
        try:
            import psutil
            procs = []
            try:
                p = psutil.Process(pid)
                procs.append(p)
                procs.extend(p.children(recursive=True))
            except psutil.NoSuchProcess:
                typer.echo("Process not found; cleaning up pid file.")
            else:
                for pr in reversed(procs): 
                    try:
                        pr.terminate()
                    except psutil.NoSuchProcess:
                        pass
                gone, alive = psutil.wait_procs(procs, timeout=3.0)
                if alive:
                    for pr in alive:
                        try:
                            pr.kill()
                        except psutil.NoSuchProcess:
                            pass
        except ImportError:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                typer.echo("Process not found; cleaning up pid file.")
            except Exception as e:
                if force:
                    try:
                        os.kill(pid, signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM)
                    except Exception as e2:
                        typer.echo(f"Force kill failed: {e2}", err=True)
                        raise typer.Exit(code=1)
                else:
                    typer.echo(f"Failed to stop process: {e}", err=True)
                    raise typer.Exit(code=1)
    finally:
        try:
            paths["pid"].unlink(missing_ok=True)
        except Exception:
            pass

    typer.echo(f"Stopped depths server for '{instance_id}'.")


if __name__ == "__main__":
    app()
