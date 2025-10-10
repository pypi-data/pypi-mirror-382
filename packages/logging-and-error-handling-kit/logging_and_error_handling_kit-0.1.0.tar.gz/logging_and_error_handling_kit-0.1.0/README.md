Here’s a clean, copy-pasteable `README.md` you can tailor. It matches the two-file package you’ve built (`logger_config.py` + `error_handler.py`) with env-aware stdout control.

---

# my-logging-kit

Env-aware logging with **per-call stdout control** and a friendly **ErrorHandler**.

* File outputs: `logs/service.log`, `logs/errors.log` (and optional `logs/debug.log`)
* Stdout: controlled by `display_on_stdout` per log call + `APP_ENV`

## Features

* ✅ Per-message toggle: `logger.info("...", display_on_stdout=False)`
* ✅ Environment defaults: dev → show on stdout, prod → hide unless you opt-in
* ✅ Structured error handling: `ErrorHandler.handle_error(...)`
* ✅ Rotating file logs

## Install

```bash
pip install python-dotenv
pip install my-logging-kit   # or: pip install -e .
```

## Quickstart

```python
from my_logging_kit import setup_logger, get_logger, ErrorHandler, ErrorType

setup_logger()                       # init once, early in your app

logger = get_logger(__name__)
logger.info("hello!")                # -> service.log (stdout in dev; hidden in prod)
logger.error("boom", display_on_stdout=True)  # -> errors.log (+ stdout)

try:
    raise RuntimeError("test failure")
except Exception as exc:
    ErrorHandler(__name__).handle_error(
        error=exc,
        error_type=ErrorType.PROCESSING_ERROR,
        context={"svc": "api", "op": "startup"},
        user_message="Startup failed"
    )
```

## Environment variables

Create a `.env` (loaded via `python-dotenv`):

```
APP_ENV=dev          # dev | prod   (prod hides stdout by default)
CONSOLE_LOG_LEVEL=INFO
DEBUG=false          # if true -> logs/debug.log (DEBUG level)
```

## Where logs go

**Files (rotating):**

* `service.log`: INFO, WARNING, ERROR, CRITICAL
* `errors.log`:  ERROR, CRITICAL
* `debug.log` (when `DEBUG=true`): DEBUG

**Stdout:**

* Default behavior depends on `APP_ENV`

  * `dev`: shown unless `display_on_stdout=False`
  * `prod`: hidden unless `display_on_stdout=True`
* You can always force printing:
  `logger.error("show this", display_on_stdout=True)`

## API

### `setup_logger()`

Initializes handlers (files + console) and formats. Call once, early.

### `get_logger(name: str) -> logging.Logger`

Returns an `AppLogger` that accepts `display_on_stdout` kwarg on all methods:

* `.debug/info/warning/error/critical/exception(msg, ..., display_on_stdout: bool = default)`

### `ErrorHandler`

```python
handle_error(
  error: Exception,
  error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
  context: dict | None = None,
  user_message: str | None = None,
) -> ServiceError
```

Logs with level based on `error_type`, includes traceback in context, and returns a structured `ServiceError`.

### `ErrorType`

`VALIDATION_ERROR, API_ERROR, PROCESSING_ERROR, CONFIGURATION_ERROR, NETWORK_ERROR, UNKNOWN_ERROR`

## Examples

**Quiet on stdout (file-only)**

```python
logger.info("stored but not printed", display_on_stdout=False)
```

**Force stdout in prod**

```python
logger.error("must be visible now", display_on_stdout=True)
```

**gRPC example (health check)**

```python
try:
    raise RuntimeError("Health check failed")
except Exception as exc:
    msg = f"Health check failed: {exc}"
    ErrorHandler(__name__).handle_error(
        error=exc,
        error_type=ErrorType.PROCESSING_ERROR,
        context={"service": "HealthService", "method": "HealthCheck"},
        user_message=msg
    )
```

## Troubleshooting

* **Nothing prints in prod:** ensure `logging.setLoggerClass(AppLogger)` runs at import time (it does in this package) and call `setup_logger()` early. If a framework reconfigures logging after startup, call `setup_logger()` again.
* **`.env` not applied:** uninstall `dotenv`, install `python-dotenv`, ensure `load_dotenv()` runs before reading env vars.
* **Too much stdout noise:** pass `display_on_stdout=False` where needed, or set `APP_ENV=prod`.

## Project layout

```
src/my_logging_kit/
  __init__.py
  logger_config.py
  error_handler.py
```

## License

## License
MIT © 2025 Omar
See the [LICENSE](./LICENSE) file for details.

