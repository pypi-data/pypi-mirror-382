# ======================================================================
# (A) FILE PATH & IMPORT PATH
# depths/core/views.py  →  import path: depths.core.views
# ======================================================================

"""
(B) FILE OVERVIEW (concept & significance in v0.1.2)

This module introduces two *sidecar* runtime views for Depths:

1) StatsRollup
   A background worker that maintains minute-wise, UTC-grounded snapshot rows
   for the three OTel signal families (traces, logs, metrics). Each flush
   appends snapshot rows to a single local Delta table at:
       <instance_root>/stats/otel_minute
   partitioned by (project_id → event_date). It computes:
     • event_count for all signals
     • duration_ms min/max/avg/std for spans
     • value min/max/avg/std for metric points
     • severity_counts_json for logs
   Every N flushes (optimize_frequency), it compacts touched partitions via
   delta.optimize(...) to reduce small files.

2) RealtimeTap
   An in-memory, bounded FIFO read path that stores *raw dicts as-is* for
   immediate “tail”/stream views. It exposes a pull reader and a simple
   Server-Sent Events (SSE) iterator for FastAPI endpoints.

Design goals:
- Non-blocking ingestion tee: enqueue and return; never stall hot path.
- Append-only snapshots with snapshot_ts + bucket_key (no MERGE).
- UTC minute boundaries with allowed_lateness_s to stabilize windows.
- Zero coupling to shipper/S3; stats are local-only in v0.1.2.

"""

from __future__ import annotations

import json
import math
import threading
import time
import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple

import polars as pl
import datetime as dt

from depths.io.delta import create_delta, insert_delta, optimize
from depths.core.config import StatsRollupConfig, RealtimeReadConfig


# ======================================================================
# StatsRollup
# ======================================================================

class StatsRollup:
    """
    Minute-wise derived store for spans/logs/metrics.

    Overview:
        Maintains per-minute, per-project snapshots derived from all incoming
        rows, and appends them into a single local Delta table partitioned by
        (project_id → event_date). Flushes occur continuously; any bucket older
        than `allowed_lateness_s` seconds relative to current UTC is finalized.
        Every `optimize_frequency` flushes, the table is compacted via OPTIMIZE.

    Args:
        instance_root: Absolute path to the Depths instance root.
        cfg: Mapping containing:
             • enabled: bool (unused here; the owner toggles instantiation)
             • bucket_seconds: int (default 60; must remain 60 in v0.1.2)
             • allowed_lateness_s: int (default 15)
             • optimize_frequency: int (default 10)

    Public methods:
        start()  → Start the background flusher thread.
        stop(flush_remaining: bool = True) → Stop and optionally flush.
        enqueue(signal: str, row: Mapping[str, Any]) → Non-blocking tee.
        lazy_read(...) → pl.LazyFrame over the stats table.

    Developer notes:
    - Bucketing uses UTC minute keys: minute_ts = floor(event_ts_ms/60000).
    - Snapshots are append-only with (snapshot_ts, bucket_key). Readers can
      pick the latest snapshot per key if multiple snapshots exist.
    - We compact on a configurable cadence (optimize_frequency) without
      altering delta.optimize() (gating happens inside _flush_ready_buckets).
    - Logs store a compact severity histogram as JSON; numeric measures are
      None for non-numeric signals (e.g., span_events, links, metric hist).
    """

    def __init__(self, instance_root: Path | str, config: StatsRollupConfig) -> None:
        """
        Initialize StatsRollup with a typed config and a concrete instance root.

        Overview (pattern parity):
            Mirrors LogProducer/LogAggregator by accepting a typed config object and
            caching it on `self._cfg`. The constructor normalizes paths under the
            instance root, seeds per-minute aggregation state, and ensures the
            backing Delta table exists.

        Args:
            instance_root: Filesystem root directory for the Depths instance.
            config:        StatsRollupConfig carrying bucket size, lateness, and
                        OPTIMIZE cadence.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - `_cfg` holds the immutable config object; do not mutate it at runtime.
        # - Minute boundaries remain UTC-grounded; `allowed_lateness_s` defaults to 15.
        # - OPTIMIZE cadence is gated in `_flush_ready_buckets()` using `optimize_frequency`.
        # - Constructor side-effects are limited to idempotent table creation.

        self._cfg = config

        self._root = Path(instance_root)
        self._stats_dir = self._root / "stats"
        self._table_path = str(self._stats_dir / "otel_minute")

        self._bucket_seconds = int(config.bucket_seconds)
        self._allowed_lateness_s = int(config.allowed_lateness_s)
        self._optimize_frequency = max(1, int(config.optimize_frequency))

        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._buckets: Dict[
            Tuple[str, str, int, str, str, Optional[str], Optional[str], Optional[str]],
            Dict[str, Any],
        ] = {}

        self._flush_counter = 0

        self._ensure_table()

    # ------------------------------- schema helpers -------------------------------

    @staticmethod
    def _schema() -> Dict[str, pl.DataType]:
        """
        Describe the Polars schema of the stats Delta table.

        Returns:
            Mapping of column names to Polars dtypes for persisted rollup rows.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Keep this in sync with _flush_ready_buckets() and _ensure_table().
        # - Explicit dtypes avoid inference drift when columns are empty.

        return {
            "project_id": pl.Utf8,
            "event_date": pl.Utf8,
            "minute_ts": pl.Int64,
            "signal": pl.Utf8,
            "service_name": pl.Utf8,
            "name": pl.Utf8,
            "status_or_severity": pl.Utf8,
            "kind": pl.Utf8,
            "event_count": pl.Int64,
            "value_min": pl.Float64,
            "value_max": pl.Float64,
            "value_avg": pl.Float64,
            "value_std": pl.Float64,
            "severity_counts_json": pl.Utf8,
            "snapshot_ts": pl.Int64,
            "bucket_key": pl.Utf8,
        }

    def _ensure_table(self) -> None:
        """
        Idempotently create the backing Delta table for rollup snapshots.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Uses an empty DataFrame to stamp schema and partitions without writes.
        # - mode="ignore" keeps repeated constructors from erroring.
        # - Directory creation lives here so tests can point at temp roots.

        self._stats_dir.mkdir(parents=True, exist_ok=True)
        empty_cols = {k: pl.Series(name=k, values=[], dtype=dtp) for k, dtp in self._schema().items()}
        empty_df = pl.DataFrame(empty_cols)  # schema-only create
        create_delta(
            table_path=self._table_path,
            data=empty_df,
            mode="ignore",
            partition_by=["project_id", "event_date"],
        )

    # -------------------------------- lifecycle -----------------------------------

    def start(self) -> None:
        """
        Launch the background flush thread if it is not already running.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Thread is marked daemon so shutdown is not blocked if stop() is skipped.
        # - Caller (DepthsLogger) should treat start() as idempotent.

        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="StatsRollup", daemon=True)
        self._thread.start()

    def stop(self, flush_remaining: bool = True) -> None:
        """
        Request shutdown of the flush thread and optionally drain remaining buckets.

        Args:
            flush_remaining: When True, flushes any in-memory aggregates after
                the thread stops.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - join(timeout=5) prevents shutdown hangs if the thread misbehaves.
        # - Final flush uses the same path as normal cycles, ensuring parity.
        # - Safe to call even if start() was never invoked.

        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        if flush_remaining:
            self._flush_ready_buckets(final=True)

    # -------------------------------- ingestion -----------------------------------

    def enqueue(self, signal: str, row: Mapping[str, Any]) -> None:
        """
        Incorporate a raw telemetry row into the appropriate minute bucket.

        Args:
            signal: OTel table name (spans, logs, metrics_points, etc.).
            row: Mapping representing the normalized producer output.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Exceptions while extracting are swallowed; ingestion should never block.
        # - Buckets are keyed by (project_id, date, minute, signal, service, name, status, kind).
        # - Numeric aggregates track count/sum/sumsq to derive mean & std on flush.

        try:
            fam, dims, measures = self._extract(signal, row)
        except Exception:
            return
        if fam is None:
            return

        key = (
            dims["project_id"],
            dims["event_date"],
            dims["minute_ts"],
            fam,
            dims["service_name"],
            dims.get("name"),
            dims.get("status_or_severity"),
            dims.get("kind"),
        )

        with self._lock:
            st = self._buckets.get(key)
            if st is None:
                st = {
                    "project_id": dims["project_id"],
                    "event_date": dims["event_date"],
                    "minute_ts": dims["minute_ts"],
                    "signal": fam,
                    "service_name": dims["service_name"],
                    "name": dims.get("name") or "",
                    "status_or_severity": dims.get("status_or_severity") or "",
                    "kind": dims.get("kind") or "",
                    "count": 0,
                    "min": math.inf,
                    "max": -math.inf,
                    "sum": 0.0,
                    "sumsq": 0.0,
                    "severity_counts": defaultdict(int),
                }
                self._buckets[key] = st

            st["count"] += 1

            val = measures.get("value")
            if val is not None:
                if val < st["min"]:
                    st["min"] = val
                if val > st["max"]:
                    st["max"] = val
                st["sum"] += val
                st["sumsq"] += val * val

            sev = measures.get("severity_number")
            if sev is not None:
                st["severity_counts"][int(sev)] += 1

    # --------------------------------- flushing -----------------------------------

    def _run(self) -> None:
        """
        Background loop that periodically finalizes ready buckets.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Runs inside the dedicated StatsRollup thread created by start().
        # - Uses a minute boundary check to avoid redundant scans.
        # - wait(timeout=1.0) lets stop() wake the loop promptly.

        last_check_min = None
        while not self._stop.is_set():
            now_ms = int(dt.datetime.now(dt.UTC).timestamp() * 1000)
            cur_min = now_ms // 60000
            if last_check_min != cur_min:
                self._flush_ready_buckets()
                last_check_min = cur_min
            self._stop.wait(timeout=1.0)

    def _flush_ready_buckets(self, final: bool = False) -> None:
        """
        Persist buckets whose minute window is finalized and run compaction.

        Args:
            final: If True, flushes all buckets regardless of allowed lateness.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Builds DataFrame rows outside the lock to keep enqueue() fast.
        # - touched_dates drives selective OPTIMIZE calls to reduce small files.
        # - final=True is used during shutdown to avoid data loss.

        now_ms = int(dt.datetime.now(dt.UTC).timestamp() * 1000)
        safe_minute = ((now_ms // 1000) - self._allowed_lateness_s) // 60

        rows: List[Dict[str, Any]] = []
        touched_dates: set[str] = set()

        with self._lock:
            to_pop: List[Tuple] = []
            for key, st in self._buckets.items():
                minute_ts = st["minute_ts"]
                if final or minute_ts <= safe_minute:
                    cnt = int(st["count"])
                    if cnt <= 0:
                        to_pop.append(key)
                        continue

                    if math.isfinite(st["min"]) and math.isfinite(st["max"]):
                        avg = st["sum"] / cnt
                        var = max(st["sumsq"] / cnt - avg * avg, 0.0)
                        std = math.sqrt(var)
                        vmin, vmax = float(st["min"]), float(st["max"])
                    else:
                        avg = std = vmin = vmax = None

                    sev_json = None
                    if st["severity_counts"]:
                        sev_json = json.dumps(st["severity_counts"], separators=(",", ":"))

                    snap_ts = now_ms
                    bkey_src = (
                        st["project_id"],
                        st["event_date"],
                        st["minute_ts"],
                        st["signal"],
                        st["service_name"],
                        st["name"],
                        st["status_or_severity"],
                        st["kind"],
                        snap_ts,
                    )
                    bucket_key = hashlib.sha1("|".join(map(str, bkey_src)).encode("utf-8")).hexdigest()

                    rows.append(
                        {
                            "project_id": st["project_id"],
                            "event_date": st["event_date"],
                            "minute_ts": int(st["minute_ts"]),
                            "signal": st["signal"],
                            "service_name": st["service_name"],
                            "name": st["name"],
                            "status_or_severity": st["status_or_severity"],
                            "kind": st["kind"],
                            "event_count": cnt,
                            "value_min": vmin,
                            "value_max": vmax,
                            "value_avg": avg,
                            "value_std": std,
                            "severity_counts_json": sev_json or "",
                            "snapshot_ts": snap_ts,
                            "bucket_key": bucket_key,
                        }
                    )
                    touched_dates.add(st["event_date"])
                    to_pop.append(key)

            for key in to_pop:
                self._buckets.pop(key, None)

        if not rows:
            return

        df = pl.DataFrame(rows, schema=self._schema())
        insert_delta(
            table_path=self._table_path,
            data=df,
        )

        self._flush_counter += 1
        if self._flush_counter % self._optimize_frequency == 0 and touched_dates:
            for d in sorted(touched_dates):
                try:
                    optimize(self._table_path, partition_filters=[("event_date", "=", d)])
                except Exception:
                    pass

    # ----------------------------------- read -------------------------------------

    def lazy_read(
        self,
        *,
        project_id: Optional[str] = None,
        signal: Optional[str] = None,
        service_name: Optional[str] = None,
        name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        minute_ts_from: Optional[int] = None,
        minute_ts_to: Optional[int] = None,
        latest_only: bool = True,
    ) -> pl.LazyFrame:
        """
        Build a Polars LazyFrame over the minute rollup with optional filters.

        Args:
            project_id: Filter to a single project id.
            signal: Restrict to a signal family (spans/logs/metrics).
            service_name: Restrict by service.
            name: Filter by logical name/instrument.
            date_from: Inclusive lower bound on event_date (YYYY-MM-DD).
            date_to: Inclusive upper bound on event_date (YYYY-MM-DD).
            minute_ts_from: Inclusive lower bound on minute_ts epoch bucket.
            minute_ts_to: Inclusive upper bound on minute_ts epoch bucket.
            latest_only: When True, keep only the newest snapshot per dimension set.

        Returns:
            pl.LazyFrame that callers can further chain or collect.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Uses scan_delta to keep operations lazy and pushdown-friendly.
        # - tail(1) with sort(snapshot_ts) collapses duplicates but preserves filters.
        # - Callers are expected to collect/with_columns as needed.

        lf = pl.scan_delta(self._table_path)
        if project_id:
            lf = lf.filter(pl.col("project_id") == project_id)
        if signal:
            lf = lf.filter(pl.col("signal") == signal)
        if service_name:
            lf = lf.filter(pl.col("service_name") == service_name)
        if name:
            lf = lf.filter(pl.col("name") == name)
        if date_from:
            lf = lf.filter(pl.col("event_date") >= date_from)
        if date_to:
            lf = lf.filter(pl.col("event_date") <= date_to)
        if minute_ts_from is not None:
            lf = lf.filter(pl.col("minute_ts") >= int(minute_ts_from))
        if minute_ts_to is not None:
            lf = lf.filter(pl.col("minute_ts") <= int(minute_ts_to))

        if latest_only:
            w = [pl.col(c) for c in ("project_id", "event_date", "minute_ts", "signal", "service_name", "name", "status_or_severity", "kind")]
            lf = lf.sort("snapshot_ts").group_by(w).tail(1)

        return lf

    # ------------------------------ per-row extraction ----------------------------

    @staticmethod
    def _family_for(signal: str) -> Optional[str]:
        """
        Normalize an OTel table name to a StatsRollup family key.

        Args:
            signal: Input signal hint from producers/aggregators.

        Returns:
            Family string ("spans", "logs", or "metrics") or None when unsupported.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Keep mapping in sync with enqueue() and RealtimeTap._fam().
        # - Accepts common singular/plural forms to stay lenient.

        s = signal.lower()
        if s in {"spans", "span", "span_events", "span_links"}:
            return "spans"
        if s in {"logs", "log"}:
            return "logs"
        if s in {"metrics", "metric", "metrics_points", "metrics_point", "metrics_hist", "metrics_histogram"}:
            return "metrics"
        return None

    @staticmethod
    def _resolve_event_ts_ms(signal: str, row: Mapping[str, Any]) -> int:
        """
        Resolve an event timestamp in **milliseconds** from a mapped row.

        Overview:
            Accepts pre-aggregator, mapped OTLP row shapes and derives a stable
            millisecond timestamp using a priority order across common fields:
              1) `event_ts` (already in ms, if present)
              2) nanosecond fields (ns → ms) in this order:
                 `time_unix_nano`, `start_time_unix_nano`,
                 `observed_time_unix_nano`, `end_time_unix_nano`
              3) fallback to current UTC time (ms)

        Args:
            signal: Original signal hint (spans/logs/metrics_points/...).
            row:    Mapped row dict from the OTLP mapper.

        Returns:
            Epoch milliseconds suitable for minute bucketing.

        Developer notes:
        - Keep this helper tolerant; producer/aggregator add `event_ts`, but the
          sidecar sees pre-aggregator rows and must not depend on it.
        - Resolution is intentionally signal-agnostic; the ordered key scan works
          for logs, spans, and metrics without special cases.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Avoid per-signal branching; the ordered scan covers typical fields.
        # - int(...) is safe here; upstream mapping uses ints for *_nano.

        evt_ms = row.get("event_ts")
        if isinstance(evt_ms, int) and evt_ms > 0:
            return evt_ms

        for k in (
            "time_unix_nano",
            "start_time_unix_nano",
            "observed_time_unix_nano",
            "end_time_unix_nano",
        ):
            ns = row.get(k)
            if isinstance(ns, int) and ns > 0:
                return ns // 1_000_000

        now_ms = int(dt.datetime.now(dt.UTC).timestamp() * 1000)
        return now_ms

    @staticmethod
    def _extract(signal: str, row: Mapping[str, Any]) -> Tuple[Optional[str], Dict[str, Any], Dict[str, Any]]:
        """
        Compute rollup dimensions and measures from a raw row.

        Args:
            signal: Source signal/table name.
            row: Mapping of normalized fields emitted by producers.

        Returns:
            Tuple of (family, dimension dict, measure dict). Family is None for
            unsupported signals.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Uses `_resolve_event_ts_ms` to robustly derive event time in ms.
        # - If `event_date` is missing, derive from the resolved timestamp.
        # - Other logic unchanged (severity histogram, metrics value, etc.).

        fam = StatsRollup._family_for(signal)
        if fam is None:
            return None, {}, {}

        project_id = str(row.get("project_id", "default"))
        service_name = str(row.get("service_name", "unknown") or "unknown")
        event_ts = StatsRollup._resolve_event_ts_ms(signal, row)
        event_date = str(row.get("event_date", "")) or StatsRollup._date_from_ms(event_ts)
        minute_ts = int(event_ts // 60000)

        name: Optional[str] = None
        status_or_severity: Optional[str] = None
        kind: Optional[str] = None
        value: Optional[float] = None
        severity_number: Optional[int] = None

        s = signal.lower()
        if fam == "spans":
            if s == "spans":
                name = str(row.get("name", "") or "")
                status_or_severity = str(row.get("status_code", "") or "")
                kind = str(row.get("kind", "") or "")
                dur = row.get("duration_ms", None)
                value = float(dur) if dur is not None else None
            elif s == "span_events":
                name = "(span_event)"
            elif s == "span_links":
                name = "(span_link)"
        elif fam == "logs":
            severity_number = row.get("severity_number", None)
            status_or_severity = str(severity_number) if severity_number is not None else ""
            name = ""
        elif fam == "metrics":
            if s in {"metrics_points", "metrics_point"}:
                name = str(row.get("instrument_name", "") or "")
                value = float(row.get("value", None)) if row.get("value", None) is not None else None
            else:
                name = "(metric_hist)"

        dims = {
            "project_id": project_id,
            "event_date": event_date,
            "minute_ts": minute_ts,
            "service_name": service_name,
            "name": name,
            "status_or_severity": status_or_severity,
            "kind": kind,
        }
        measures = {"value": value, "severity_number": severity_number}
        return fam, dims, measures
    
    @staticmethod
    def _date_from_ms(ms: int) -> str:
        """
        Convert an event timestamp in milliseconds to a YYYY-MM-DD date string.

        Args:
            ms: Epoch timestamp in milliseconds (may be zero/negative).

        Returns:
            UTC date string used for event_date.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Negative/zero timestamps fall back to current UTC day.
        # - Keep format aligned with bucket partitioning and shipper expectations.

        if ms <= 0:
            return dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
        return dt.datetime.fromtimestamp(ms / 1000.0, tz=dt.UTC).strftime("%Y-%m-%d")


# ======================================================================
# RealtimeTap
# ======================================================================

class RealtimeTap:
    """
    In-memory, bounded FIFO view of raw dicts for real-time reads.

    Overview:
        Stores raw telemetry dicts as-is in three independent deques for the
        three signal families: traces (spans/events/links), logs, and metrics
        (points/hist). Provides simple pull reads and an SSE iterator that
        yields JSON lines with periodic heartbeats.

    Args:
        cfg: Mapping with:
             • enabled: bool (unused here; owner toggles instantiation)
             • max_traces / max_logs / max_metrics: int caps for each deque
             • drop_policy: Literal["drop_old"] (fixed in v0.1.2)

    Public methods:
        push(signal: str, raw: Mapping[str, Any]) → None
        read(signal: str, n: int = 100, project_id: Optional[str] = None) → list[dict]
        sse_iter(signal: str, *, project_id: Optional[str] = None,
                 heartbeat_s: int = 10, poll_interval_s: float = 1.0) → Iterator[bytes]

    Developer notes:
    - No backpressure: oldest items are dropped when caps are exceeded.
    - Family mapping: spans/span_events/span_links → "traces"; logs → "logs";
      metrics_points/metrics_hist → "metrics".
    - SSE framing uses "data: <json>\\n\\n" and comment heartbeats to keep
      intermediaries/glue happy.
    """

    def __init__(self, config: RealtimeReadConfig) -> None:
        """
        Initialize capped deques and locks using a typed realtime config.

        Overview (pattern parity):
            Mirrors LogProducer/LogAggregator by accepting a typed config object and
            caching it on `self._cfg`. Constructs per-family bounded FIFOs with
            drop_old semantics and per-family locks.

        Args:
            config: RealtimeReadConfig with per-family caps and drop policy.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Policy is fixed to drop_old in v0.1.2; no backpressure/acks.
        # - Caps default to 2k per family; adjust via config for heavier tails.
        # - Keep raw dicts as-is to minimize hot-path serialization.

        self._cfg = config

        self._caps = {
            "traces": int(config.max_traces),
            "logs": int(config.max_logs),
            "metrics": int(config.max_metrics),
        }
        self._qs: Dict[str, Deque[dict]] = {
            "traces": deque(maxlen=self._caps["traces"]),
            "logs": deque(maxlen=self._caps["logs"]),
            "metrics": deque(maxlen=self._caps["metrics"]),
        }
        self._locks = {
            "traces": threading.Lock(),
            "logs": threading.Lock(),
            "metrics": threading.Lock(),
        }

    @staticmethod
    def _fam(signal: str) -> Optional[str]:
        """
        Map an OTLP table name to the internal realtime family grouping.

        Args:
            signal: Input signal string from the caller.

        Returns:
            One of "traces", "logs", "metrics" or None if unsupported.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Shared contracts with StatsRollup._family_for(); keep aligned.
        # - Accepts singular/plural spellings to stay forgiving.

        s = signal.lower()
        if s in {"spans", "span", "span_events", "span_links"}:
            return "traces"
        if s in {"logs", "log"}:
            return "logs"
        if s in {"metrics", "metric", "metrics_points", "metrics_point", "metrics_hist", "metrics_histogram"}:
            return "metrics"
        return None

    def push(self, signal: str, raw: Mapping[str, Any]) -> None:
        """
        Append a raw telemetry dict to the appropriate realtime queue.

        Args:
            signal: Signal hint (spans/logs/metrics_points/etc.).
            raw: Mapping representing the event to store.

        Returns:
            None
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Unknown signals are ignored silently to avoid noisy errors.
        # - Copy the mapping to detach from caller mutations.
        # - Lock per-family to keep operations thread-safe.

        fam = self._fam(signal)
        if fam is None:
            return
        q = self._qs[fam]
        with self._locks[fam]:
            q.append(dict(raw))

    def read(self, signal: str, n: int = 100, project_id: Optional[str] = None) -> List[dict]:
        """
        Return the newest items from a realtime queue, optionally filtered.

        Args:
            signal: Signal family selector.
            n: Maximum number of items to include (tail semantics).
            project_id: Optional filter on project_id field.

        Returns:
            List of dicts in chronological order (oldest → newest).
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Copies deque contents under the family lock to produce a stable view.
        # - Filtering by project happens post-copy to avoid holding the lock longer.
        # - Negative n clamps to zero via max(0, n).

        fam = self._fam(signal)
        if fam is None:
            return []
        q = self._qs[fam]
        with self._locks[fam]:
            items = list(q)[-int(max(0, n)) :]
        if project_id:
            items = [r for r in items if str(r.get("project_id", "")) == project_id]
        return items

    def sse_iter(
        self,
        signal: str,
        *,
        project_id: Optional[str] = None,
        heartbeat_s: int = 10,
        poll_interval_s: float = 1.0,
    ) -> Iterator[bytes]:
        """
        Yield a Server-Sent Events stream for a realtime family.

        Args:
            signal: Signal name to stream.
            project_id: Optional filter limiting rows to a project.
            heartbeat_s: Interval for comment heartbeats.
            poll_interval_s: Sleep interval between queue polls.

        Returns:
            Iterator yielding already-framed SSE bytes.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Initial snapshot replays existing items before tailing.
        # - Heartbeats keep proxies/load balancers from timing out idle streams.
        # - last_len tracks how many items have been yielded without scanning history.

        fam = self._fam(signal)
        if fam is None:
            def _it() -> Iterator[bytes]:
                """
                Emit a single SSE comment indicating the signal is unsupported.

                Returns:
                    Iterator yielding one SSE comment frame.
                """
                # --- DEVELOPER NOTES -------------------------------------------------
                # - Keep payload short; FastAPI streams this verbatim to clients.

                yield b": unsupported signal\n\n"
            return _it()

        last_len = 0
        t0 = time.monotonic()
        initial = self.read(signal, n=self._caps[fam], project_id=project_id)
        for r in initial:
            payload = json.dumps(r, separators=(",", ":")).encode("utf-8")
            yield b"data: " + payload + b"\n\n"
        while True:
            now = time.monotonic()
            if now - t0 >= heartbeat_s:
                yield b": heartbeat\n\n"
                t0 = now
            time.sleep(max(0.0, poll_interval_s))
            with self._locks[fam]:
                cur = list(self._qs[fam])
                new = cur[last_len:]
                last_len = len(cur)
            if project_id:
                new = [r for r in new if str(r.get("project_id", "")) == project_id]
            for r in new:
                payload = json.dumps(r, separators=(",", ":")).encode("utf-8")
                yield b"data: " + payload + b"\n\n"
