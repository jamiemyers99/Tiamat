import sys
import traceback

from tiamat.game import main


def run() -> int:
    exit_code = 0
    try:
        main()
    except Exception:
        exit_code = 1
        traceback.print_exc()
    finally:
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(run())
