# networking-utils

A tiny demonstration Python package showing project structure for PyPI publishing. Provides a simple `add_two_number` function (placeholder for more networking-focused utilities you might add later).

## Features
- `add_two_number(a, b)`: adds two numbers with type hints.
- Ready-to-publish project scaffold using PEP 621 metadata in `pyproject.toml`.

## Installation
```bash
pip install networking-utils
```

## Usage
```python
from networking_utils import add_two_number
print(add_two_number(2, 3))  # 5
```

CLI entry point (after installation):
```bash
networking-utils-add 2 3
```

## Development
```bash
python -m venv .venv
. .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e .[dev]
```

## Versioning
Semantic versioning (MAJOR.MINOR.PATCH).

## License
MIT
