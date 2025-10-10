# logging-and-error-handling-kit

Env-aware logging with per-call stdout control and rotating file handlers.
Designed for services that need clean console logs in dev and quiet consoles in prod—without losing file logs.

[![PyPI](https://img.shields.io/pypi/v/logging-and-error-handling-kit.svg)](https://pypi.org/project/logging-and-error-handling-kit/)
[![Python](https://img.shields.io/pypi/pyversions/logging-and-error-handling-kit.svg)](https://pypi.org/project/logging-and-error-handling-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Features

* **Per-call stdout control**: `logger.info("...", display_on_stdout=False)`
* **Env-aware default**: console shows logs in local/staging, stays quiet in prod (`APP_ENV=prod`)
* **Rotating files**: `service.log`, `errors.log`, optional `debug.log`
* **One-liner setup** with `setup_logger()` and `get_logger(__name__)`
* Compatible with standard `logging` API; no vendor lock-in.

## Install

```bash
pip install logging-and-error-handling-kit
```

## Quickstart

```python
from logging_and_error_handling_kit import setup_logger, get_logger

setup_logger()  # once at app startup
log = get_logger(__name__)

log.info("Hello!")                                  # prints in non-prod, always goes to files
log.info("Silent on console", display_on_stdout=False)  # still goes to files
log.error("Oops", display_on_stdout=True)           # force to console (subject to handler level)
```

## How it decides what hits stdout

* `APP_ENV` controls the **default**:

  * `APP_ENV=prod` → default `display_on_stdout=False`
  * any other (or unset) → default `True`
* You can override per call: `display_on_stdout=True/False`
* Console level via `CONSOLE_LOG_LEVEL` (default `INFO`)

## Environment variables

| Name                           | Default | Purpose                                                 |
| ------------------------------ | ------- | ------------------------------------------------------- |
| `APP_ENV`                      | `local` | Env profile: `local`, `staging`, `prod`…                |
| `CONSOLE_LOG_LEVEL`            | `INFO`  | Console verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEBUG`                        | `False` | If `true`, also writes detailed `debug.log`             |
| `LOGS_DIR` *(if you add this)* | `logs`  | Directory for log files                                 |

> Tip: Add a `.env` and use `python-dotenv` (already in dependencies) to load these at startup.

## File outputs (rotating)

* `logs/service.log` → `INFO+`
* `logs/errors.log`  → `ERROR+`
* `logs/debug.log`   → `DEBUG+` (only if `DEBUG=true`)

## API

```python
setup_logger() -> None
    # Initializes handlers/formatters/filters on the root logger.

get_logger(name: str) -> logging.Logger
    # Standard logger retrieval.

# Log methods (standard logging API) accept:
logger.info(msg, *args, display_on_stdout: bool = <env default>, **kwargs)
logger.debug(...)
logger.warning(...)
logger.error(...)
logger.critical(...)
logger.exception(msg, *args, display_on_stdout=<env default>, **kwargs)
    # .exception sets exc_info=True automatically
```

## Examples

**Service-style bootstrap**

```python
import os
from logging_and_error_handling_kit import setup_logger, get_logger
from dotenv import load_dotenv

load_dotenv()        # loads APP_ENV, CONSOLE_LOG_LEVEL, etc.
setup_logger()

log = get_logger("my.service")

log.info("Service starting…")
try:
    1 / 0
except Exception:
    log.exception("Calculation failed", display_on_stdout=True)
```

**Quiet console in prod, verbose locally**

```bash
# local
export APP_ENV=local
python app.py  # console shows logs

# prod
export APP_ENV=prod
python app.py  # console minimal unless you force display_on_stdout=True
```

## Project structure (suggested)

```
src/
  logging_and_error_handling_kit/
    __init__.py
    error_handler.py
    logger_config.py
README.md
LICENSE
pyproject.toml
```

## Versioning & releases

1. Bump `version` in `pyproject.toml`
2. Build: `python -m build`
3. Upload: `python -m twine upload dist/*`
4. Install: `pip install logging-and-error-handling-kit`

## Contributing

Issues and PRs welcome. Please add tests and keep public API stable.

## License

MIT – see [LICENSE](LICENSE).

---

### How to publish the README changes to PyPI

* Edit `README.md`
* Ensure `pyproject.toml` has `readme = "README.md"`
* Rebuild & upload a **new version**:

  ```bash
  # bump version in pyproject.toml (e.g., 0.1.2)
  python -m build
  python -m twine upload dist/*
  ```
