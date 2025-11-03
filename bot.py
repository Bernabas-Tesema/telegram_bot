"""Compatibility entrypoint: `python bot.py`.

This small wrapper ensures users who run `python bot.py` (singular)
will call the actual bot implementation in `bots.py`.
"""

import sys

try:
    import bots
except Exception as e:
    print(f"Failed to import 'bots' module: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
    # Delegate to bots.main()
    bots.main()
