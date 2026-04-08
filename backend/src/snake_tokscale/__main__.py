"""Allow ``python -m snake_tokscale`` to invoke the CLI."""

from __future__ import annotations

import sys

from snake_tokscale.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
