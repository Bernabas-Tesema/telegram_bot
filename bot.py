"""Compatibility entrypoint: `python bot.py`.

This file simply imports the existing `bots.py` module and calls its
`main()` function so users that run `python bot.py` (singular) won't
hit the file-not-found error if the project file is named `bots.py`.
"""

import sys

try:
    import bots
except Exception as e:
    # Print a friendly error if import fails (helps debugging import path issues)
    print(f"Failed to import 'bots' module: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
    # Forward to the real entrypoint in bots.py
    bots.main()
