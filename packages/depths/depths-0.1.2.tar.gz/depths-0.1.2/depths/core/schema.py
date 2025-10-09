# ======================================================================
# (A) FILE PATH & IMPORT PATH
# depths/core/schema.py  →  import path: depths.core.schema
# ======================================================================

# ======================================================================
# (B) FILE OVERVIEW (concept & significance in v0.1.2)
# Canonical, typed schemas for the six OTel tables that Depths v0.1.2
# persists as Delta Lake tables. This module provides:
#   • EventSchema         → declarative table contract used by Producer/Aggregator
#   • RESOURCE_SCOPE_BASE → normalized columns shared by all six tables
#   • SPAN_SCHEMA, SPAN_EVENT_SCHEMA, SPAN_LINK_SCHEMA
#   • LOG_SCHEMA, METRIC_POINT_SCHEMA, METRIC_HIST_SCHEMA
#
# These schemas anchor:
#   - Validation & normalization in depths.core.producer.LogProducer
#   - DataFrame construction & Delta writes in depths.core.aggregator.LogAggregator
#   - OTLP JSON → row mapping in depths.core.otlp_mapper.OTLPMapper
#   - Reader projections in depths.core.logger.DepthsLogger
#
# Design goals: OTel-first column names, UTC event day alignment, safe
# JSON encoding of attribute blobs, and stable partitions (notably
# project_id, service_name, schema_version).
# ======================================================================

# ======================================================================
# (C) IMPORTS & GLOBALS (what & why)
# dataclasses, typing  → immutable schema descriptor with rich metadata
# polars as pl        → column dtypes used for validation & DF typing
# datetime            → helper for timestamp→date coercions
#
# Globals defined:
#   - RESOURCE_SCOPE_BASE: shared columns (resource/scope + event_ts/date)
#   - <SCHEMA> constants: SPAN_SCHEMA, SPAN_EVENT_SCHEMA, SPAN_LINK_SCHEMA,
#     LOG_SCHEMA, METRIC_POINT_SCHEMA, METRIC_HIST_SCHEMA
#     (each is an EventSchema instance consumed by Producer/Aggregator/Logger).
# ======================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Set, Tuple, Literal, Optional
import polars as pl
import datetime as _dt

@dataclass(frozen=True)
class EventSchema:
    """
    Declarative contract for a concrete Delta table.

    Overview (v0.1.2 role):
        EventSchema is the single source of truth for table shape & behavior
        across the ingestion path. LogProducer uses it to validate/normalize
        rows; LogAggregator uses `polars_schema()` to type DataFrames and create
        Delta tables; OTLPMapper aligns its output to the required/default/
        computed fields. DepthsLogger wires the six OTel tables by attaching
        the corresponding EventSchema to producer/aggregator configs.

    Fields:
        fields:  Polars dtype mapping for all columns (column name → pl.DataType).
        required: Set of required columns after defaults/computed are applied.
        defaults: Column → default value (applied if not present on input).
        computed: Column → callable(row_dict) producing derived values.
        extra_policy: How to treat unexpected keys ('error' | 'strip' | 'keep').
        autocoerce: Allow Producer to cast simple types (e.g., "1" → 1).
        json_fields: Columns that must be JSON-encoded strings on disk.
        enforce_date_from_ts: Optional (ts_ms_field, date_str_field) to
                              enforce UTC day coherence (e.g., event_ts → event_date).
        schema_version: Logical version for downstream partitioning/evolution.

    Returns:
        (N/A — dataclass)

    Notes:
        - All JSON-like columns are modeled as pl.Utf8; Producer serializes to JSON.
        - event_ts is epoch milliseconds; event_date is 'YYYY-MM-DD' (UTC).
        - service_name defaults to 'unknown' to keep partitions non-empty.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Frozen for safety: treat schemas as constants.
    # - Keep column names aligned with OTLP terminology for intuitive queries.
    # - Adding columns: extend `fields` + defaults and (optionally) required.
    # - Renames/removals are backward-incompatible: plan migrations if needed.

    fields: Dict[str, pl.DataType]
    required: Set[str] = field(default_factory=set)
    defaults: Dict[str, Any] = field(default_factory=dict)
    computed: Dict[str, Callable[[Mapping[str, Any]], Any]] = field(default_factory=dict)
    extra_policy: Literal["error", "strip", "keep"] = "strip"
    autocoerce: bool = True
    json_fields: Set[str] = field(default_factory=set)
    enforce_date_from_ts: Tuple[str, str] | None = None  
    schema_version: int = 1

    def polars_schema(self) -> Dict[str, pl.DataType]:
        """
        Return the Polars schema mapping for this table.

        Overview (v0.1.2 role):
            Used by the Aggregator when creating schema-only Delta tables and when
            constructing typed DataFrames for append writes.

        Returns:
            Mapping of column name → pl.DataType.
        """
        # --- DEVELOPER NOTES -------------------------------------------------
        # - Intentionally returns the `fields` dict verbatim.
        # - Keep dtypes stable; changes ripple into persisted Delta metadata.

        return self.fields

def _ns_to_ms(ns: int) -> int:
    """
    Convert UNIX epoch nanoseconds → milliseconds (floor division).

    Overview (v0.1.2 role):
        Normalizes OTLP's nanosecond timestamps to the millisecond epoch used
        in event_ts across all tables.

    Args:
        ns: UNIX timestamp in nanoseconds.

    Returns:
        Milliseconds since epoch as int.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - Keep arithmetic integer-only to avoid float rounding artifacts.
    # - Used by computed fields in multiple schemas; must remain deterministic.

    return int(ns // 1_000_000)

def _ms_to_date(ms: int) -> str:
    """
    Convert epoch milliseconds → UTC date string ('YYYY-MM-DD').

    Overview (v0.1.2 role):
        Provides the canonical UTC day used for event_date partitions
        and date coherence checks in the Producer.

    Args:
        ms: Milliseconds since epoch.

    Returns:
        UTC date in ISO format YYYY-MM-DD.
    """
    # --- DEVELOPER NOTES -------------------------------------------------
    # - UTC only (no timezone offsets). Aligns with S3/day layout and readers.
    # - Keep format stable; many call sites depend on exact 'YYYY-MM-DD'.

    return _dt.datetime.fromtimestamp(ms / 1000, tz=_dt.timezone.utc).strftime("%Y-%m-%d")

# Doc:
# Shared columns across all six OTel tables: project/service identity,
# resource/scope JSON blobs, and the canonical event time & UTC day.
# Ensures consistent partitioning and query predicates across tables.

# --- DEVELOPER NOTES -----------------------------------------------------
# - event_ts is epoch ms; event_date is derived UTC 'YYYY-MM-DD'.
# - JSON-bearing columns are pl.Utf8; Producer handles JSON serialization.

RESOURCE_SCOPE_BASE: Dict[str, pl.DataType] = {
    "project_id": pl.Utf8,
    "schema_version": pl.Int64,

    "service_name": pl.Utf8,
    "service_namespace": pl.Utf8,
    "service_instance_id": pl.Utf8,
    "service_version": pl.Utf8,
    "deployment_env": pl.Utf8,
    "resource_attrs_json": pl.Utf8,

    "scope_name": pl.Utf8,
    "scope_version": pl.Utf8,
    "scope_attrs_json": pl.Utf8,
    
    "event_ts": pl.Int64,    
    "event_date": pl.Utf8, 
}

# Doc:
# Spans table: each row is a span with start/end times, status, and attributes.
# event_ts/event_date come from start_time_unix_nano; duration_ms is computed.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Required includes event_ts/event_date for partition alignment.
# - service_name is set to "unknown" when NULL, to suitably handle delta partitioning.
# - Defaults set status_code='UNSET', kind='INTERNAL', empty JSONs to '{}'.
# - Keep trace_id/span_id lowercase hex; Producer can enforce lengths.
# - v0.1.2: Added session and user identity context

SPAN_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "parent_span_id": pl.Utf8,
        "name": pl.Utf8,
        "kind": pl.Utf8,
        "start_time_unix_nano": pl.Int64,
        "end_time_unix_nano": pl.Int64,
        "duration_ms": pl.Float64,
        "status_code": pl.Utf8,
        "status_message": pl.Utf8,
        "dropped_events_count": pl.Int64,
        "dropped_links_count": pl.Int64,
        "span_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={
        "project_id","schema_version","trace_id","span_id","name",
        "start_time_unix_nano","end_time_unix_nano","event_ts","event_date",
    },
    defaults={
        "schema_version": 1,
        "dropped_events_count": 0, "dropped_links_count": 0,
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",
        "status_code":"UNSET", "status_message":"", "kind":"INTERNAL",
        "parent_span_id":"", "span_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("start_time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("start_time_unix_nano", 0)))),
        "duration_ms": lambda d: max(
            0.0, (int(d.get("end_time_unix_nano", 0)) - int(d.get("start_time_unix_nano", 0))) / 1_000_000.0
        ),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","span_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# Span events table: one row per Span.Event. Timestamps taken from time_unix_nano.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Keep event_attrs_json compact (Producer serializes with separators=(',',':')).
# - Maintain alignment with OTLP LogRecord shape for body/attrs symmetry.
# - v0.1.2: Added session and user identity context

SPAN_EVENT_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "time_unix_nano": pl.Int64,
        "name": pl.Utf8,
        "event_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","trace_id","span_id","time_unix_nano","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "name":"", "event_attrs_json":"{}",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","event_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)


# Doc:
# Links between spans. event_ts/event_date are supplied by the Mapper based on
# the *parent span's* start time for stable timeline placement.

# --- DEVELOPER NOTES -----------------------------------------------------
# - No computed fields here by design; Mapper sets event_ts/event_date.
# - linked_trace_id/linked_span_id are lowercase hex strings.
# - v0.1.2: Added session and user identity context

SPAN_LINK_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,
        "linked_trace_id": pl.Utf8,
        "linked_span_id": pl.Utf8,
        "link_attrs_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","trace_id","span_id","linked_trace_id","linked_span_id","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "link_attrs_json":"{}",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={},  # as in v0.1.2 (no implicit time derivation here)
    json_fields={"resource_attrs_json","scope_attrs_json","link_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# OTel logs table. event_ts/event_date derive from time_unix_nano.
# trace_id/span_id may be empty (uncorrelated records are allowed).

# --- DEVELOPER NOTES -----------------------------------------------------
# - body is a string: AnyValue is stringified deterministically by Mapper.
# - severity_number is Int32 for compactness; adjust only with migration.
# - v0.1.2: Added session and user identity context

LOG_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "time_unix_nano": pl.Int64,
        "observed_time_unix_nano": pl.Int64,
        "severity_text": pl.Utf8,
        "severity_number": pl.Int32,
        "body": pl.Utf8,
        "log_attrs_json": pl.Utf8,
        "trace_id": pl.Utf8,
        "span_id": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "observed_time_unix_nano": 0, "severity_text":"", "severity_number":0,
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",
        "log_attrs_json":"{}", "trace_id":"", "span_id":"",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","log_attrs_json"},
    enforce_date_from_ts=("event_ts", "event_date"),
    schema_version=1,
)

# Doc:
# Gauge/Sum points. Carries temporality/monotonicity and a single numeric value.
# event_ts/event_date derive from time_unix_nano.

# --- DEVELOPER NOTES -----------------------------------------------------
# - value coerces to Float64 for uniformity across numeric types.
# - Exemplars/attrs stored as JSON strings for flexibility.
# - Aggregation temporality can be CUMULATIVE|DELTA|UNSPECIFIED
# - v0.1.2: Added session and user identity context

METRIC_POINT_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "instrument_name": pl.Utf8,
        "instrument_type": pl.Utf8,
        "unit": pl.Utf8,                            
        "aggregation_temporality": pl.Utf8,
        "is_monotonic": pl.Boolean,
        "time_unix_nano": pl.Int64,
        "start_time_unix_nano": pl.Int64,
        "value": pl.Float64,
        "point_attrs_json": pl.Utf8,
        "exemplars_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","instrument_name","instrument_type","time_unix_nano","value","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "unit":"", "aggregation_temporality":"UNSPECIFIED", "is_monotonic": False,
        "start_time_unix_nano": 0, "point_attrs_json":"{}", "exemplars_json":"[]",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json": "{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={"resource_attrs_json","scope_attrs_json","point_attrs_json","exemplars_json"},
    enforce_date_from_ts=("event_ts","event_date"),
    schema_version=1,
)


# Doc:
# Instrument type: Histogram / ExpHistogram / Summary family in a single wide table.
# Buckets/bounds/quantiles captured as JSON text fields.

# --- DEVELOPER NOTES -----------------------------------------------------
# - Use Float64 for sum/min/max; counts are Int64; exp_* metadata as ints.
# - event_ts/event_date derive from time_unix_nano; keep UTC semantics stable.
# - v0.1.2: Added session and user identity context

METRIC_HIST_SCHEMA = EventSchema(
    fields={
        **RESOURCE_SCOPE_BASE,
        "instrument_name": pl.Utf8,
        "instrument_type": pl.Utf8,
        "unit": pl.Utf8,
        "aggregation_temporality": pl.Utf8,
        "time_unix_nano": pl.Int64,
        "start_time_unix_nano": pl.Int64,
        "count": pl.Int64,
        "sum": pl.Float64,
        "min": pl.Float64,
        "max": pl.Float64,
        "bounds_json": pl.Utf8,
        "counts_json": pl.Utf8,
        "exp_zero_count": pl.Int64,
        "exp_scale": pl.Int32,
        "exp_positive_json": pl.Utf8,
        "exp_negative_json": pl.Utf8,
        "quantiles_json": pl.Utf8,
        "point_attrs_json": pl.Utf8,
        "exemplars_json": pl.Utf8,

        # === Identity (v0.1.2) ===
        "session_id": pl.Utf8,
        "session_previous_id": pl.Utf8,
        "user_id": pl.Utf8,
        "user_name": pl.Utf8,
        "user_roles_json": pl.Utf8,
    },
    required={"project_id","schema_version","instrument_name","instrument_type","time_unix_nano","count","event_ts","event_date"},
    defaults={
        "schema_version": 1,
        "unit":"", "aggregation_temporality":"UNSPECIFIED",
        "start_time_unix_nano": 0, "sum": 0.0, "min": 0.0, "max": 0.0,
        "bounds_json":"[]", "counts_json":"[]",
        "exp_zero_count":0, "exp_scale":0,
        "exp_positive_json":"{}", "exp_negative_json":"{}",
        "quantiles_json":"[]", "point_attrs_json":"{}", "exemplars_json":"[]",
        "service_name": "unknown",
        "service_namespace":"", "service_instance_id":"", "service_version":"", "deployment_env":"",
        "scope_name":"", "scope_version":"", "resource_attrs_json":"{}", "scope_attrs_json":"{}",

        # === Identity defaults ===
        "session_id": "",
        "session_previous_id": "",
        "user_id": "",
        "user_name": "",
        "user_roles_json": "[]",
    },
    computed={
        "event_ts": lambda d: _ns_to_ms(int(d.get("time_unix_nano", 0))),
        "event_date": lambda d: _ms_to_date(_ns_to_ms(int(d.get("time_unix_nano", 0)))),
    },
    json_fields={
        "resource_attrs_json","scope_attrs_json","bounds_json","counts_json",
        "exp_positive_json","exp_negative_json","quantiles_json","point_attrs_json","exemplars_json"
    },
    enforce_date_from_ts=("event_ts","event_date"),
    schema_version=1,
)

