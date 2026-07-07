"""Lightweight helper to validate configured backends at runtime.

This script is safe to call from Jenkins or locally (requires
`QISKIT_IBM_TOKEN` in the environment). It exits with code 0 when at
least one configured backend is active, and non-zero otherwise.
"""
import sys

from src.config import resolve_cfg_backends


def main():
    try:
        active = resolve_cfg_backends()
    except Exception as e:
        print("ERROR: failed to resolve configured backends:", e, file=sys.stderr)
        sys.exit(2)

    print("Resolved active backends:", active)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
