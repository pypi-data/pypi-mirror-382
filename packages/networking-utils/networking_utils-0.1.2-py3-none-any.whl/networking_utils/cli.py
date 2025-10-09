"""Command line entry point for networking_utils.

Installed as the console script `networking-utils-add`.
"""
from __future__ import annotations

import argparse
from typing import Iterable, Optional
from .math_utils import add_two_number

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Add two numbers and print the result.")
    p.add_argument("a", type=float, help="First number")
    p.add_argument("b", type=float, help="Second number")
    return p

def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = add_two_number(args.a, args.b)
    print(result)
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
