"""Best-effort Amazon Data Firehose sink for redacted agent lifecycle events."""

from __future__ import annotations

import atexit
import json
import os
import queue
import threading
import time
from typing import Any

import boto3
from prometheus_client import Counter, Gauge, Histogram

from agent.telemetry.events import AgentEvent
from agent.telemetry.sink import EventSink, NullEventSink

_FIREHOSE_RECORDS = Counter(
    "helixagent_firehose_records_total",
    "Agent lifecycle records handled by the optional Firehose sink",
    ["status"],
)
_FIREHOSE_BATCH_SIZE = Histogram(
    "helixagent_firehose_batch_size",
    "Number of lifecycle records in each Firehose PutRecordBatch call",
    buckets=(1, 5, 10, 25, 50, 100, 250, 500),
)
_FIREHOSE_QUEUE_DEPTH = Gauge(
    "helixagent_firehose_queue_depth",
    "Current number of lifecycle records waiting for Firehose delivery",
)
_FIREHOSE_DELIVERY_SECONDS = Histogram(
    "helixagent_firehose_delivery_seconds",
    "Wall-clock time spent in Firehose PutRecordBatch calls",
)


class FirehoseEventSink:
    """Bounded, fail-open producer for Amazon Data Firehose.

    Events are serialized as newline-delimited JSON and sent in batches from a
    daemon worker. Queue pressure, partial failures, or SDK exceptions are
    surfaced through metrics but never propagated into agent execution.
    """

    def __init__(
        self,
        stream_name: str,
        *,
        client: Any | None = None,
        queue_size: int = 1_000,
        batch_size: int = 100,
        flush_interval_seconds: float = 1.0,
    ) -> None:
        if not stream_name.strip():
            raise ValueError("stream_name must not be empty")
        if queue_size < 1:
            raise ValueError("queue_size must be at least 1")
        if not 1 <= batch_size <= 500:
            raise ValueError("batch_size must be between 1 and 500")
        if flush_interval_seconds <= 0:
            raise ValueError("flush_interval_seconds must be positive")

        self.stream_name = stream_name
        self.client = client or boto3.client(
            "firehose",
            region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1",
        )
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self._queue: queue.Queue[AgentEvent] = queue.Queue(maxsize=queue_size)
        self._stop = threading.Event()
        self._closed = False
        self._worker = threading.Thread(
            target=self._run,
            name="helixagent-firehose",
            daemon=True,
        )
        self._worker.start()

    @staticmethod
    def _serialize(event: AgentEvent) -> bytes:
        payload = event.model_dump(mode="json", exclude_none=True)
        return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    def emit(self, event: AgentEvent) -> None:
        if self._closed:
            _FIREHOSE_RECORDS.labels(status="dropped").inc()
            return
        try:
            self._queue.put_nowait(event)
            _FIREHOSE_RECORDS.labels(status="queued").inc()
            _FIREHOSE_QUEUE_DEPTH.set(self._queue.qsize())
        except queue.Full:
            _FIREHOSE_RECORDS.labels(status="dropped").inc()

    def _run(self) -> None:
        batch: list[AgentEvent] = []
        last_flush = time.monotonic()
        while not self._stop.is_set() or not self._queue.empty():
            timeout = max(0.01, self.flush_interval_seconds - (time.monotonic() - last_flush))
            try:
                event = self._queue.get(timeout=timeout)
                batch.append(event)
                self._queue.task_done()
                _FIREHOSE_QUEUE_DEPTH.set(self._queue.qsize())
            except queue.Empty:
                pass

            should_flush = len(batch) >= self.batch_size or (
                batch and time.monotonic() - last_flush >= self.flush_interval_seconds
            )
            if should_flush:
                self._flush(batch)
                batch = []
                last_flush = time.monotonic()

        if batch:
            self._flush(batch)
        _FIREHOSE_QUEUE_DEPTH.set(0)

    def _flush(self, batch: list[AgentEvent]) -> None:
        records = [{"Data": self._serialize(event)} for event in batch]
        _FIREHOSE_BATCH_SIZE.observe(len(records))
        started = time.perf_counter()
        try:
            response = self.client.put_record_batch(
                DeliveryStreamName=self.stream_name,
                Records=records,
            )
            failed = int(response.get("FailedPutCount", 0))
            delivered = max(0, len(records) - failed)
            if delivered:
                _FIREHOSE_RECORDS.labels(status="delivered").inc(delivered)
            if failed:
                _FIREHOSE_RECORDS.labels(status="error").inc(failed)
        except Exception:  # noqa: BLE001 - telemetry is deliberately fail-open
            _FIREHOSE_RECORDS.labels(status="error").inc(len(records))
        finally:
            _FIREHOSE_DELIVERY_SECONDS.observe(time.perf_counter() - started)

    def close(self, timeout: float = 5.0) -> None:
        if self._closed:
            return
        self._closed = True
        self._stop.set()
        self._worker.join(timeout=timeout)


def build_event_sink_from_env() -> EventSink:
    """Build the configured event sink; local development defaults to no export."""

    mode = os.getenv("HELIXAGENT_EVENT_SINK", "none").strip().lower()
    if mode in {"", "none", "disabled"}:
        return NullEventSink()
    if mode != "firehose":
        raise ValueError("HELIXAGENT_EVENT_SINK must be 'none' or 'firehose'")

    stream_name = os.getenv("HELIXAGENT_FIREHOSE_STREAM", "").strip()
    if not stream_name:
        raise ValueError("HELIXAGENT_FIREHOSE_STREAM is required when Firehose export is enabled")

    sink = FirehoseEventSink(
        stream_name,
        queue_size=int(os.getenv("HELIXAGENT_FIREHOSE_QUEUE_SIZE", "1000")),
        batch_size=int(os.getenv("HELIXAGENT_FIREHOSE_BATCH_SIZE", "100")),
        flush_interval_seconds=float(os.getenv("HELIXAGENT_FIREHOSE_FLUSH_SECONDS", "1.0")),
    )
    atexit.register(sink.close)
    return sink
