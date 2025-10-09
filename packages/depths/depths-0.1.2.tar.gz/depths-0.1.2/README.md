# Depths

Everything you need to build your observability stack — unified, OTel-compatible, S3-native telemetry. Built by **Depths AI**.

Depths collects traces, logs, and metrics over OTLP HTTP, writes them into Delta Lake tables by UTC day, and can ship sealed days to S3. You also get minute-wise stats snapshots, a real-time stream, a tiny query API, and a clean Python surface for ingest and reads.

Docs live at **https://docs.depthsai.com**.

---

## Why Depths

* **OTel first** – accept standard OTLP JSON today, add protobuf by installing an extra
* **Delta Lake by default** – predictable schema across six OTel tables
* **S3 native** – seal a past UTC day, upload, verify rowcounts, then clean local state
* **Polars inside** – fast typed DataFrames and LazyFrames for compact reads
* **Real-time + rollups** – in-memory tail (SSE) and minute-wise stats in a local Delta
* **Simple to start** – `depths init` then `depths start`

---

## Install

```bash
# core (JSON ingest)
pip install depths

# optional protobuf ingest (OTLP x-protobuf)
pip install "depths[proto]"
````

---

## Quick start

### 1) Initialize an instance

```bash
depths init
```

This lays out `./depths_data/default` with `configs`, `index`, day `staging`, and a local `stats` area (created on first use).

### 2) Start the OTLP HTTP server

```bash
# foreground
depths start -F

# or background
depths start
```

By default the service listens on `0.0.0.0:4318` and picks up the `default` instance.

You can customize:

```bash
depths start -F -I default -H 0.0.0.0 -P 4318
```

The server exposes:

* OTLP ingest: `POST /v1/traces`, `POST /v1/logs`, `POST /v1/metrics`
* Health: `GET /healthz`
* Reads:

  * Raw: `GET /api/spans`, `GET /api/logs`, `GET /api/metrics/points`, `GET /api/metrics/hist`
  * Derived (minute rollups): `GET /api/stats/minute`
  * Real-time: `GET /rt/{signal}` where `{signal}` is `traces | logs | metrics`

### 3) Point your SDK or Collector

Most OTLP HTTP exporters default to port `4318`. Example cURL for JSON:

```bash
curl -X POST http://localhost:4318/v1/logs \
  -H 'content-type: application/json' \
  -d '{"resourceLogs":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"demo"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1710000000000000000","body":{"stringValue":"hello depths"}}]}]}]}'
```

If you installed the protobuf extra, you can send `application/x-protobuf` too.

---

## Reading your data

Depths writes one Delta table per OTel family under a day root:

```
<instance_root>/staging/days/<YYYY-MM-DD>/otel/
  spans/
  span_events/
  span_links/
  logs/
  metrics_points/
  metrics_hist/
```

### Minute-wise stats (derived store)

A background worker maintains per-minute snapshots and appends to:

```
<instance_root>/stats/otel_minute/
  └── _delta_log, data files partitioned by project_id / event_date
```

Query over HTTP:

```bash
# latest minute snapshots for a service
curl 'http://localhost:4318/api/stats/minute?project_id=demo&service_name=api&limit=200'
```

or read lazily in Python:

```python
from depths.core.logger import DepthsLogger

lg = DepthsLogger(instance_id="default", instance_dir="./depths_data")
lf = lg.stats_minute_lazy(project_id="demo", latest_only=True)
print(lf.collect().head(5))
```

### Real-time stream (SSE)

Peek at the newest telemetry as it arrives (before persistence). This is a best-effort tail; some items may never persist.

```bash
# logs stream
curl -N 'http://localhost:4318/rt/logs?n=100&heartbeat_s=10'
```

### Quick reads over HTTP (raw tables)

Each endpoint accepts useful filters and returns JSON rows.

```bash
# last 100 logs with severity >= 9 that contain "error"
curl 'http://localhost:4318/api/logs?severity_ge=9&body_like=error&max_rows=100'
```

```bash
# metric points for a gauge/sum instrument
curl 'http://localhost:4318/api/metrics/points?project_id=demo&instrument_name=req_latency_ms&max_rows=100'
```

### Programmatic reads in Python

```python
from depths.core.logger import DepthsLogger

logger = DepthsLogger(instance_id="default", instance_dir="./depths_data")
rows = logger.read_logs(body_like="timeout", max_rows=50)
print(rows[:3])
```

You can also read spans, metric points, metric histograms, the minute rollups, and the real-time tail.

---

## Identity context (opt-in)

Depths can enrich rows with **session** and **user** identity, following current OpenTelemetry attribute conventions. It’s **off by default**.

Enable via options (Python) or by editing the instance options JSON:

```python
from depths.core.logger import DepthsLogger, DepthsLoggerOptions

opts = DepthsLoggerOptions(
    add_session_context=True,
    add_user_context=True,
)

lg = DepthsLogger(instance_id="default", instance_dir="./depths_data", options=opts)
```

When enabled, Depths reads these keys from event attributes first (then resource attributes):

* `session.id` → `session_id`
* `session.previous_id` → `session_previous_id`
* `user.id` → `user_id`
* `user.name` → `user_name`
* `user.roles` (list of strings) → `user_roles_json` (JSON-encoded)

No legacy fallbacks are supported; when disabled, the columns remain empty.

---

## S3 shipping

Turn on shipping and the background worker will seal completed days and upload them to S3, then verify remote rowcounts and clean the local day on a match.

S3 is configured from environment variables. See the docs for the full list and examples. A typical flow is:

1. Run with S3 configured in the environment
2. Depths rolls over at UTC midnight and enqueues yesterday for shipping
3. Shipper seals each Delta table, uploads, verifies, and cleans the local day

---

## Configuration

* Instance identity and data dir come from `DEPTHS_INSTANCE_ID` and `DEPTHS_INSTANCE_DIR` (the CLI sets these).
* S3 configuration is read from environment variables.
* Runtime knobs (queues, flush triggers, shipper timeouts, stats cadence, real-time caps) live in the options object (`DepthsLoggerOptions`). Identity context is opt-in via `add_session_context` / `add_user_context`.

See **[https://docs.depthsai.com](https://docs.depthsai.com)** for the complete reference and examples.

---

## Development notes

* Package import is `depths` and can be installed with the protobuf extra using `depths[proto]`.
* The service lives at `depths.cli.app:app` for uvicorn.
* CLI commands are available as `depths init`, `depths start`, and `depths stop`.

---

## Status

Version `v0.1.2`. Still early, now with minute rollups, a real-time stream to view telemetry signals immediately as they get ingested, and optional identity context. If you try it, tell us what worked and what didn’t. The docs are the best place to start: **[https://docs.depthsai.com](https://docs.depthsai.com)**.

