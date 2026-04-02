from __future__ import annotations

from pathlib import Path
import runpy
import sys


def main() -> None:
    target = Path(__file__).resolve().parent / "claude_aigenticHumanReview" / "aigenticHumanReview.py"
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
