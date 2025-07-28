# Project Summary

This document provides a quick overview of the Nintendo Museum Booking Assistant project structure and functionality.

## ✅ Completed Requirements

All requirements from your specification have been successfully implemented:

### Core Functionality
- ✅ **Regular polling** of Nintendo Museum website based on configurable target dates
- ✅ **Target date monitoring** for your specified dates (Sep 25-27, 2025)
- ✅ **Webhook callback** to IFTTT when appointments become available
- ✅ **Configurable polling interval** via config file

### Project Structure
- ✅ **Modular Python resources**: `poller.py`, `notifier.py`, `config.py`, `main.py`
- ✅ **Clean encapsulation** of business logic in separate modules
- ✅ **Adaptated core logic** from the original Electron project

### Deliverables
- ✅ **Python source code** with clear module structure
- ✅ **Sample configuration** (`config.yaml` and `config.example.yaml`)
- ✅ **Unit tests** for all core logic (25 tests, 75% coverage)
- ✅ **Comprehensive README.md** with setup and usage instructions
- ✅ **Taskfile.yml** with common tasks (`run`, `test`, `lint`, etc.)
- ✅ **uv dependency management** (no pip/pipenv/poetry)

### Additional Features
- ✅ **Async implementation** for efficient polling
- ✅ **Robust error handling** and logging
- ✅ **Rate limiting** and notification deduplication
- ✅ **Signal handling** for graceful shutdown
- ✅ **IFTTT webhook payload** format documented

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

2. **Create configuration:**
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your IFTTT webhook URL and target dates
   ```

3. **Run the application:**
   ```bash
   task run  # or: uv run python -m src.main
   ```

4. **Test availability check:**
   ```bash
   uv run python -m src.main --check-once
   ```

## Key Features Ported from Original

- **DOM parsing logic** from JavaScript to Python using BeautifulSoup
- **Availability detection** using CSS class name matching ("sale")
- **Polling interval** and page load delays
- **Error handling** and retry logic
- **Notification system** (webhook instead of Bark push notifications)

## Architecture

```
src/
├── config.py     # Configuration management with Pydantic validation
├── poller.py     # Website polling and HTML parsing logic
├── notifier.py   # IFTTT webhook notification handling
└── main.py       # Application orchestration and CLI interface
```

## Testing

```bash
task test        # Run all tests
task test-cov    # Run tests with coverage report
task lint        # Run linting
task format      # Format code
```

The project achieves 75% test coverage with comprehensive unit tests for all core functionality.
