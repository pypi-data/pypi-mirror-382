# networking-utils

Small utilities for networking-related scripts. Current focus: a simple `Timestamp` helper.

## What’s included
- `Timestamp` class for generating current time in two formats:
	- `timestamp`: `YYYY_MM_DD_HH_MM_SS` (good for filenames)
	- `time_str`: `YYYY-MM-DD HH:MM:SS` (good for logs/UI)

Source: `src/networking_utils/timestamp.py`

## Installation
```bash
pip install networking-utils
```

Install from TestPyPI (optional):
```powershell
# Windows PowerShell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple networking-utils
```

## Usage
```python
from networking_utils.timestamp import Timestamp

ts = Timestamp()
ts.get_timestamp()  # populates fields with the current time

print(ts.timestamp)  # e.g., '2025_10_09_14_23_45'
print(ts.time_str)   # e.g., '2025-10-09 14:23:45'
```

### Practical examples
- Unique filenames
```python
from pathlib import Path
from networking_utils.timestamp import Timestamp

ts = Timestamp(); ts.get_timestamp()
path = Path(f"backup_{ts.timestamp}.zip")
```

- Log lines
```python
from networking_utils.timestamp import Timestamp

ts = Timestamp(); ts.get_timestamp()
print(f"[{ts.time_str}] job started")
```

## Development
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

Build locally:
```powershell
python -m pip install --upgrade pip setuptools wheel build
python -m build
```

## Versioning
Semantic versioning (MAJOR.MINOR.PATCH).

## License
MIT
