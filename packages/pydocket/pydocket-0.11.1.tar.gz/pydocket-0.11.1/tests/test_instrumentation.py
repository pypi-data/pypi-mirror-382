import asyncio
import http.client
import socket
from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from opentelemetry import trace
from opentelemetry.metrics import Counter, Histogram, UpDownCounter
from opentelemetry.metrics import _Gauge as Gauge
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.trace import StatusCode

from docket import Docket, Worker
from docket.dependencies import Perpetual, Retry
from docket.instrumentation import (
    healthcheck_server,
    message_getter,
    message_setter,
    metrics_server,
)

tracer = trace.get_tracer(__name__)


@pytest.fixture(scope="module", autouse=True)
def tracer_provider() -> TracerProvider:
    """Sets up a "real" TracerProvider so that spans are recorded for the tests"""
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    return provider


async def test_executing_a_task_is_wrapped_in_a_span(docket: Docket, worker: Worker):
    captured: list[Span] = []

    async def the_task():
        span = trace.get_current_span()
        assert isinstance(span, Span)
        captured.append(span)

    execution = await docket.add(the_task)()

    await worker.run_until_finished()

    assert len(captured) == 1
    (task_span,) = captured
    assert task_span is not None
    assert isinstance(task_span, Span)

    assert task_span.name == "the_task"
    assert task_span.kind == trace.SpanKind.CONSUMER
    assert task_span.attributes

    print(task_span.attributes)

    assert task_span.attributes["docket.name"] == docket.name
    assert task_span.attributes["docket.task"] == "the_task"
    assert task_span.attributes["docket.key"] == execution.key
    assert task_span.attributes["docket.when"] == execution.when.isoformat()
    assert task_span.attributes["docket.attempt"] == 1
    assert task_span.attributes["code.function.name"] == "the_task"


async def test_task_spans_are_linked_to_the_originating_span(
    docket: Docket, worker: Worker
):
    captured: list[Span] = []

    async def the_task():
        span = trace.get_current_span()
        assert isinstance(span, Span)
        captured.append(span)

    with tracer.start_as_current_span("originating_span") as originating_span:
        await docket.add(the_task)()

    assert isinstance(originating_span, Span)
    assert originating_span.context

    await worker.run_until_finished()

    assert len(captured) == 1
    (task_span,) = captured

    assert isinstance(task_span, Span)
    assert task_span.context

    assert task_span.context.trace_id != originating_span.context.trace_id

    assert not originating_span.links

    assert task_span.links
    assert len(task_span.links) == 1
    (link,) = task_span.links

    assert link.context.trace_id == originating_span.context.trace_id
    assert link.context.span_id == originating_span.context.span_id


async def test_failed_task_span_has_error_status(docket: Docket, worker: Worker):
    """When a task fails, its span should have ERROR status."""
    captured: list[Span] = []

    async def the_failing_task():
        span = trace.get_current_span()
        assert isinstance(span, Span)
        captured.append(span)
        raise ValueError("Task failed")

    await docket.add(the_failing_task)()
    await worker.run_until_finished()

    assert len(captured) == 1
    (task_span,) = captured

    assert isinstance(task_span, Span)
    assert task_span.status is not None
    assert task_span.status.status_code == StatusCode.ERROR
    assert task_span.status.description is not None
    assert "Task failed" in task_span.status.description


async def test_retried_task_spans_have_error_status(docket: Docket, worker: Worker):
    """When a task fails and is retried, each failed attempt's span should have ERROR status."""
    captured: list[Span] = []
    attempt_count = 0

    async def the_retrying_task(retry: Retry = Retry(attempts=3)):
        nonlocal attempt_count
        attempt_count += 1
        span = trace.get_current_span()
        assert isinstance(span, Span)
        captured.append(span)

        if attempt_count < 3:
            raise ValueError(f"Attempt {attempt_count} failed")
        # Third attempt succeeds

    await docket.add(the_retrying_task)()
    await worker.run_until_finished()

    assert len(captured) == 3

    # First two attempts should have ERROR status
    for i in range(2):
        span = captured[i]
        assert isinstance(span, Span)
        assert span.status is not None
        assert span.status.status_code == StatusCode.ERROR
        assert span.status.description is not None
        assert f"Attempt {i + 1} failed" in span.status.description

    # Third attempt should have OK status (or no status set, which is treated as OK)
    success_span = captured[2]
    assert isinstance(success_span, Span)
    assert (
        success_span.status is None or success_span.status.status_code == StatusCode.OK
    )


async def test_infinitely_retrying_task_spans_have_error_status(
    docket: Docket, worker: Worker
):
    """When a task with infinite retries fails, each attempt's span should have ERROR status."""
    captured: list[Span] = []
    attempt_count = 0

    async def the_infinite_retry_task(retry: Retry = Retry(attempts=None)):
        nonlocal attempt_count
        attempt_count += 1
        span = trace.get_current_span()
        assert isinstance(span, Span)
        captured.append(span)
        raise ValueError(f"Attempt {attempt_count} failed")

    execution = await docket.add(the_infinite_retry_task)()

    # Run worker for only 3 task executions of this specific task
    await worker.run_at_most({execution.key: 3})

    # All captured spans should have ERROR status
    assert len(captured) == 3
    for i, span in enumerate(captured):
        assert isinstance(span, Span)
        assert span.status is not None
        assert span.status.status_code == StatusCode.ERROR
        assert span.status.description is not None
        assert f"Attempt {i + 1} failed" in span.status.description


async def test_message_getter_returns_none_for_missing_key():
    """Should return None when a key is not present in the message."""

    message = {b"existing_key": b"value"}
    result = message_getter.get(message, "missing_key")

    assert result is None


async def test_message_getter_returns_decoded_value():
    """Should return a list with the decoded value when a key is present."""

    message = {b"key": b"value"}
    result = message_getter.get(message, "key")

    assert result == ["value"]


async def test_message_getter_keys_returns_decoded_keys():
    """Should return a list of all keys in the message as decoded strings."""

    message = {b"key1": b"value1", b"key2": b"value2"}
    result = message_getter.keys(message)

    assert sorted(result) == ["key1", "key2"]


async def test_message_setter_encodes_key_and_value():
    """Should encode both key and value when setting a value in the message."""

    message: dict[bytes, bytes] = {}
    message_setter.set(message, "key", "value")

    assert message == {b"key": b"value"}


async def test_message_setter_overwrites_existing_value():
    """Should overwrite an existing value when setting a value for an existing key."""

    message = {b"key": b"old_value"}
    message_setter.set(message, "key", "new_value")

    assert message == {b"key": b"new_value"}


@pytest.fixture
def task_labels(docket: Docket, the_task: AsyncMock) -> dict[str, str]:
    """Create labels dictionary for the task-side metrics."""
    return {"docket.name": docket.name, "docket.task": the_task.__name__}


@pytest.fixture
def TASKS_ADDED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_ADDED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_ADDED.add", mock)
    return mock


@pytest.fixture
def TASKS_REPLACED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_REPLACED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_REPLACED.add", mock)
    return mock


@pytest.fixture
def TASKS_SCHEDULED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_SCHEDULED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_SCHEDULED.add", mock)
    return mock


async def test_adding_a_task_increments_counter(
    docket: Docket,
    the_task: AsyncMock,
    task_labels: dict[str, str],
    TASKS_ADDED: Mock,
    TASKS_REPLACED: Mock,
    TASKS_SCHEDULED: Mock,
):
    """Should increment the appropriate counters when adding a task."""
    await docket.add(the_task)()

    TASKS_ADDED.assert_called_once_with(1, task_labels)
    TASKS_REPLACED.assert_not_called()
    TASKS_SCHEDULED.assert_called_once_with(1, task_labels)


async def test_replacing_a_task_increments_counter(
    docket: Docket,
    the_task: AsyncMock,
    task_labels: dict[str, str],
    TASKS_ADDED: Mock,
    TASKS_REPLACED: Mock,
    TASKS_SCHEDULED: Mock,
):
    """Should increment the appropriate counters when replacing a task."""
    when = datetime.now(timezone.utc) + timedelta(minutes=5)
    key = "test-replace-key"

    await docket.replace(the_task, when, key)()

    TASKS_ADDED.assert_not_called()
    TASKS_REPLACED.assert_called_once_with(1, task_labels)
    TASKS_SCHEDULED.assert_called_once_with(1, task_labels)


@pytest.fixture
def TASKS_CANCELLED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_CANCELLED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_CANCELLED.add", mock)
    return mock


async def test_cancelling_a_task_increments_counter(
    docket: Docket,
    the_task: AsyncMock,
    task_labels: dict[str, str],
    TASKS_CANCELLED: Mock,
):
    """Should increment the TASKS_CANCELLED counter when cancelling a task."""
    when = datetime.now(timezone.utc) + timedelta(minutes=5)
    key = "test-cancel-key"
    await docket.add(the_task, when=when, key=key)()

    await docket.cancel(key)

    TASKS_CANCELLED.assert_called_once_with(1, {"docket.name": docket.name})


@pytest.fixture
def worker_labels(
    docket: Docket, worker: Worker, the_task: AsyncMock
) -> dict[str, str]:
    """Create labels dictionary for worker-side metrics."""
    return {
        "docket.name": docket.name,
        "docket.worker": worker.name,
        "docket.task": the_task.__name__,
    }


@pytest.fixture
def TASKS_STARTED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_STARTED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_STARTED.add", mock)
    return mock


@pytest.fixture
def TASKS_COMPLETED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_COMPLETED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_COMPLETED.add", mock)
    return mock


@pytest.fixture
def TASKS_SUCCEEDED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_SUCCEEDED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_SUCCEEDED.add", mock)
    return mock


@pytest.fixture
def TASKS_FAILED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_FAILED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_FAILED.add", mock)
    return mock


@pytest.fixture
def TASKS_RETRIED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_RETRIED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_RETRIED.add", mock)
    return mock


@pytest.fixture
def TASKS_PERPETUATED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_PERPETUATED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_PERPETUATED.add", mock)
    return mock


@pytest.fixture
def TASKS_REDELIVERED(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_REDELIVERED counter."""
    mock = Mock(spec=Counter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_REDELIVERED.add", mock)
    return mock


async def test_worker_execution_increments_task_counters(
    docket: Docket,
    worker: Worker,
    the_task: AsyncMock,
    worker_labels: dict[str, str],
    TASKS_STARTED: Mock,
    TASKS_COMPLETED: Mock,
    TASKS_SUCCEEDED: Mock,
    TASKS_FAILED: Mock,
    TASKS_RETRIED: Mock,
    TASKS_REDELIVERED: Mock,
):
    """Should increment the appropriate task counters when a worker executes a task."""
    await docket.add(the_task)()

    await worker.run_until_finished()

    TASKS_STARTED.assert_called_once_with(1, worker_labels)
    TASKS_COMPLETED.assert_called_once_with(1, worker_labels)
    TASKS_SUCCEEDED.assert_called_once_with(1, worker_labels)
    TASKS_FAILED.assert_not_called()
    TASKS_RETRIED.assert_not_called()
    TASKS_REDELIVERED.assert_not_called()


async def test_failed_task_increments_failure_counter(
    docket: Docket,
    worker: Worker,
    the_task: AsyncMock,
    worker_labels: dict[str, str],
    TASKS_STARTED: Mock,
    TASKS_COMPLETED: Mock,
    TASKS_SUCCEEDED: Mock,
    TASKS_FAILED: Mock,
    TASKS_RETRIED: Mock,
    TASKS_REDELIVERED: Mock,
):
    """Should increment the TASKS_FAILED counter when a task fails."""
    the_task.side_effect = ValueError("Womp")

    await docket.add(the_task)()

    await worker.run_until_finished()

    TASKS_STARTED.assert_called_once_with(1, worker_labels)
    TASKS_COMPLETED.assert_called_once_with(1, worker_labels)
    TASKS_FAILED.assert_called_once_with(1, worker_labels)
    TASKS_SUCCEEDED.assert_not_called()
    TASKS_RETRIED.assert_not_called()
    TASKS_REDELIVERED.assert_not_called()


async def test_retried_task_increments_retry_counter(
    docket: Docket,
    worker: Worker,
    worker_labels: dict[str, str],
    TASKS_STARTED: Mock,
    TASKS_COMPLETED: Mock,
    TASKS_SUCCEEDED: Mock,
    TASKS_FAILED: Mock,
    TASKS_RETRIED: Mock,
    TASKS_REDELIVERED: Mock,
):
    """Should increment the TASKS_RETRIED counter when a task is retried."""

    async def the_task(retry: Retry = Retry(attempts=2)):
        raise ValueError("First attempt fails")

    await docket.add(the_task)()

    await worker.run_until_finished()

    assert TASKS_STARTED.call_count == 2
    assert TASKS_COMPLETED.call_count == 2
    assert TASKS_FAILED.call_count == 2
    assert TASKS_RETRIED.call_count == 1
    TASKS_SUCCEEDED.assert_not_called()
    TASKS_REDELIVERED.assert_not_called()


async def test_exhausted_retried_task_increments_retry_counter(
    docket: Docket,
    worker: Worker,
    worker_labels: dict[str, str],
    TASKS_STARTED: Mock,
    TASKS_COMPLETED: Mock,
    TASKS_SUCCEEDED: Mock,
    TASKS_FAILED: Mock,
    TASKS_RETRIED: Mock,
    TASKS_REDELIVERED: Mock,
):
    """Should increment the appropriate counters when retries are exhausted."""

    async def the_task(retry: Retry = Retry(attempts=1)):
        raise ValueError("First attempt fails")

    await docket.add(the_task)()

    await worker.run_until_finished()

    TASKS_STARTED.assert_called_once_with(1, worker_labels)
    TASKS_COMPLETED.assert_called_once_with(1, worker_labels)
    TASKS_FAILED.assert_called_once_with(1, worker_labels)
    TASKS_RETRIED.assert_not_called()
    TASKS_SUCCEEDED.assert_not_called()
    TASKS_REDELIVERED.assert_not_called()


async def test_retried_task_metric_uses_bounded_labels(
    docket: Docket,
    worker: Worker,
    worker_labels: dict[str, str],
    TASKS_RETRIED: Mock,
):
    """TASKS_RETRIED should only use bounded-cardinality labels (not task keys)."""

    async def the_task(retry: Retry = Retry(attempts=2)):
        raise ValueError("Always fails")

    await docket.add(the_task)()
    await worker.run_until_finished()

    assert TASKS_RETRIED.call_count == 1
    call_labels = TASKS_RETRIED.call_args.args[1]

    assert "docket.name" in call_labels
    assert "docket.worker" in call_labels
    assert "docket.task" in call_labels
    assert "docket.key" not in call_labels
    assert "docket.when" not in call_labels
    assert "docket.attempt" not in call_labels


async def test_perpetuated_task_metric_uses_bounded_labels(
    docket: Docket,
    worker: Worker,
    worker_labels: dict[str, str],
    TASKS_PERPETUATED: Mock,
):
    """TASKS_PERPETUATED should only use bounded-cardinality labels (not task keys)."""

    async def the_task(
        perpetual: Perpetual = Perpetual(every=timedelta(milliseconds=50)),
    ):
        pass

    execution = await docket.add(the_task)()
    await worker.run_at_most({execution.key: 2})

    assert TASKS_PERPETUATED.call_count >= 1
    call_labels = TASKS_PERPETUATED.call_args.args[1]

    assert "docket.name" in call_labels
    assert "docket.worker" in call_labels
    assert "docket.task" in call_labels
    assert "docket.key" not in call_labels
    assert "docket.when" not in call_labels
    assert "docket.attempt" not in call_labels


async def test_redelivered_tasks_increment_redelivered_counter(
    docket: Docket,
    worker_labels: dict[str, str],
    TASKS_STARTED: Mock,
    TASKS_COMPLETED: Mock,
    TASKS_SUCCEEDED: Mock,
    TASKS_FAILED: Mock,
    TASKS_RETRIED: Mock,
    TASKS_REDELIVERED: Mock,
):
    """Should increment the TASKS_REDELIVERED counter for redelivered tasks."""

    async def test_task():
        await asyncio.sleep(0.01)

    await docket.add(test_task)()

    worker = Worker(docket, redelivery_timeout=timedelta(milliseconds=50))

    async with worker:
        worker._execute = AsyncMock(side_effect=Exception("Simulated worker failure"))  # type: ignore[assignment]

        with pytest.raises(Exception, match="Simulated worker failure"):
            await worker.run_until_finished()

    await asyncio.sleep(0.075)

    worker2 = Worker(docket, redelivery_timeout=timedelta(milliseconds=100))
    async with worker2:
        await worker2.run_until_finished()

    assert TASKS_REDELIVERED.call_count >= 1


@pytest.fixture
def TASK_DURATION(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASK_DURATION histogram."""
    mock = Mock(spec=Histogram.record)
    monkeypatch.setattr("docket.instrumentation.TASK_DURATION.record", mock)
    return mock


async def test_task_duration_is_measured(
    docket: Docket, worker: Worker, worker_labels: dict[str, str], TASK_DURATION: Mock
):
    """Should record the duration of task execution in the TASK_DURATION histogram."""

    async def the_task():
        await asyncio.sleep(0.1)

    await docket.add(the_task)()
    await worker.run_until_finished()

    # We can't check the exact value since it depends on actual execution time
    TASK_DURATION.assert_called_once_with(mock.ANY, worker_labels)
    duration: float = TASK_DURATION.call_args.args[0]
    assert isinstance(duration, float)
    assert 0.1 <= duration <= 0.2


@pytest.fixture
def TASK_PUNCTUALITY(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASK_PUNCTUALITY histogram."""
    mock = Mock(spec=Histogram.record)
    monkeypatch.setattr("docket.instrumentation.TASK_PUNCTUALITY.record", mock)
    return mock


async def test_task_punctuality_is_measured(
    docket: Docket,
    worker: Worker,
    the_task: AsyncMock,
    worker_labels: dict[str, str],
    TASK_PUNCTUALITY: Mock,
):
    """Should record TASK_PUNCTUALITY values for scheduled tasks."""
    when = datetime.now(timezone.utc) + timedelta(seconds=0.1)
    await docket.add(the_task, when=when)()
    await asyncio.sleep(0.4)
    await worker.run_until_finished()

    # We can't check the exact value since it depends on actual timing
    TASK_PUNCTUALITY.assert_called_once_with(mock.ANY, worker_labels)
    punctuality: float = TASK_PUNCTUALITY.call_args.args[0]
    assert isinstance(punctuality, float)
    assert 0.3 <= punctuality <= 0.5


@pytest.fixture
def TASKS_RUNNING(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the TASKS_RUNNING up-down counter."""
    mock = Mock(spec=UpDownCounter.add)
    monkeypatch.setattr("docket.instrumentation.TASKS_RUNNING.add", mock)
    return mock


async def test_task_running_gauge_is_incremented(
    docket: Docket, worker: Worker, worker_labels: dict[str, str], TASKS_RUNNING: Mock
):
    """Should increment and decrement the TASKS_RUNNING gauge appropriately."""
    inside_task = False

    async def the_task():
        nonlocal inside_task
        inside_task = True

        TASKS_RUNNING.assert_called_once_with(1, worker_labels)

    await docket.add(the_task)()

    await worker.run_until_finished()

    assert inside_task is True

    TASKS_RUNNING.assert_has_calls(
        [
            mock.call(1, worker_labels),
            mock.call(-1, worker_labels),
        ]
    )


@pytest.fixture
def metrics_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


async def test_exports_metrics_as_prometheus_metrics(
    docket: Docket,
    worker: Worker,
    the_task: AsyncMock,
    metrics_port: int,
):
    """Should export metrics as Prometheus metrics, translating dots in labels to
    underscores for Prometheus."""

    with metrics_server(port=metrics_port):
        await docket.add(the_task)()
        await worker.run_until_finished()

        await asyncio.sleep(0.1)

        def read_metrics(port: int) -> tuple[http.client.HTTPResponse, str]:
            conn = http.client.HTTPConnection(f"localhost:{port}")
            conn.request("GET", "/")
            response = conn.getresponse()
            return response, response.read().decode()

        response, body = await asyncio.get_running_loop().run_in_executor(
            None,
            read_metrics,
            metrics_port,
        )

        assert response.status == 200, body

        assert (
            response.headers["Content-Type"]
            == "text/plain; version=0.0.4; charset=utf-8"
        )

        assert "docket_tasks_added" in body
        assert "docket_tasks_completed" in body

        assert f'docket_name="{docket.name}"' in body
        assert 'docket_task="the_task"' in body
        assert f'docket_worker="{worker.name}"' in body


@pytest.fixture
def QUEUE_DEPTH(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the QUEUE_DEPTH counter."""
    mock = Mock(spec=Gauge.set)
    monkeypatch.setattr("docket.instrumentation.QUEUE_DEPTH.set", mock)
    return mock


@pytest.fixture
def SCHEDULE_DEPTH(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock for the SCHEDULE_DEPTH counter."""
    mock = Mock(spec=Gauge.set)
    monkeypatch.setattr("docket.instrumentation.SCHEDULE_DEPTH.set", mock)
    return mock


@pytest.fixture
def docket_labels(docket: Docket) -> dict[str, str]:
    """Create labels dictionary for the Docket client-side metrics."""
    return {"docket.name": docket.name}


async def test_worker_publishes_depth_gauges(
    docket: Docket,
    docket_labels: dict[str, str],
    the_task: AsyncMock,
    QUEUE_DEPTH: Mock,
    SCHEDULE_DEPTH: Mock,
):
    """Should publish depth gauges for due and scheduled tasks."""
    await docket.add(the_task)()
    await docket.add(the_task)()

    future = datetime.now(timezone.utc) + timedelta(seconds=60)
    await docket.add(the_task, when=future)()
    await docket.add(the_task, when=future)()
    await docket.add(the_task, when=future)()

    docket.heartbeat_interval = timedelta(seconds=0.1)
    async with Worker(docket):
        await asyncio.sleep(0.2)  # enough for a heartbeat to be published

    QUEUE_DEPTH.assert_called_once_with(2, docket_labels)
    SCHEDULE_DEPTH.assert_called_once_with(3, docket_labels)


@pytest.fixture
def healthcheck_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def test_healthcheck_server_returns_ok(healthcheck_port: int):
    """Should return 200 and OK body from the liveness endpoint."""
    with healthcheck_server(port=healthcheck_port):
        conn = http.client.HTTPConnection(f"localhost:{healthcheck_port}")
        conn.request("GET", "/")
        response = conn.getresponse()

        assert response.status == 200
        assert response.headers["Content-Type"] == "text/plain"
        assert response.read().decode() == "OK"
