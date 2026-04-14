"""
Taller de Lógica

Punto de entrada para Python.
"""

from __future__ import annotations

import sys


def main() -> None:
    """Punto de entrada principal."""
    if "--test" in sys.argv:
        import subprocess

        sys.exit(
            subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
            ).returncode
        )

    from src.tui import ClueTUI

    try:
        ClueTUI().run()
    except KeyboardInterrupt:
        print("\n\n  Caso cerrado. Hasta la proxima, detective.\n")


if __name__ == "__main__":
    main()
