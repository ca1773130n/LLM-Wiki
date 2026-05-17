"""Module entry point so ``python -m tesserae ...`` works.

The package ships a ``tesserae`` console script via ``pyproject.toml``,
but environments without that script on PATH (CI containers, embedded
interpreters, ``uv run`` invocations) need the ``-m`` form. This file
keeps both surfaces in sync — both call ``tesserae.cli:main``.
"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
