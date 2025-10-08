# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Docket** (`pydocket` on PyPI) is a distributed background task system for Python functions with Redis-backed persistence. It enables scheduling both immediate and future work with comprehensive dependency injection, retry mechanisms, and fault tolerance.

**Key Requirements**: Python 3.12+, Redis 6.2+ or Valkey 8.0+

## Development Commands

### Testing

```bash
# Run full test suite with coverage and parallel execution
pytest

# Run specific test
pytest tests/test_docket.py::test_specific_function

```

The project REQUIRES 100% test coverage

### Code Quality

```bash
# Lint and format code
ruff check
ruff format

# Type checking
pyright
pyright tests

# Run all pre-commit hooks
pre-commit run --all-files
```

### Development Setup

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
pre-commit install
```

### Git Workflow

- This project uses Github for issue tracking
- This project can use git worktrees under .worktrees/

## Core Architecture

### Key Classes

- **`Docket`** (`src/docket/docket.py`): Central task registry and scheduler

  - `add()`: Schedule tasks for execution
  - `replace()`: Replace existing scheduled tasks
  - `cancel()`: Cancel pending tasks
  - `strike()`/`restore()`: Conditionally block/unblock tasks
  - `snapshot()`: Get current state for observability

- **`Worker`** (`src/docket/worker.py`): Task execution engine

  - `run_forever()`/`run_until_finished()`: Main execution loops
  - Handles concurrency, retries, and dependency injection
  - Maintains heartbeat for liveness tracking

- **`Execution`** (`src/docket/execution.py`): Task execution context with metadata

### Dependencies System (`src/docket/dependencies.py`)

Rich dependency injection supporting:

- Context access: `CurrentDocket`, `CurrentWorker`, `CurrentExecution`
- Retry strategies: `Retry`, `ExponentialRetry`
- Special behaviors: `Perpetual` (self-rescheduling), `Timeout`
- Custom injection: `Depends()`
- Contextual logging: `TaskLogger`

### Redis Data Model

- **Streams**: `{docket}:stream` (ready tasks), `{docket}:strikes` (commands)
- **Sorted Sets**: `{docket}:queue` (scheduled tasks), `{docket}:workers` (heartbeats)
- **Hashes**: `{docket}:{key}` (parked task data)
- **Sets**: `{docket}:worker-tasks:{worker}` (worker capabilities)

### Task Lifecycle

1. Registration with `Docket.register()` or `@docket.task`
2. Scheduling: immediate → Redis stream, future → Redis sorted set
3. Worker processing: scheduler moves due tasks, workers consume via consumer groups
4. Execution: dependency injection, retry logic, acknowledgment

## Project Structure

### Source Code

- `src/docket/` - Main package
  - `__init__.py` - Public API exports
  - `docket.py` - Core Docket class
  - `worker.py` - Worker implementation
  - `execution.py` - Task execution context
  - `dependencies.py` - Dependency injection system
  - `tasks.py` - Built-in utility tasks
  - `cli.py` - Command-line interface

### Testing and Examples

- `tests/` - Comprehensive test suite
- `examples/` - Usage examples
- `chaos/` - Chaos testing framework

## CLI Usage

```bash
# Run a worker
docket worker --url redis://localhost:6379/0 --tasks your.module --concurrency 4

# See all commands
docket --help
```
