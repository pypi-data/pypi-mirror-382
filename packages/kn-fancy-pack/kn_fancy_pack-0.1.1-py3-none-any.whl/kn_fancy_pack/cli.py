"""CLI for kn_fancy_pack"""
import argparse
from .game import startguesssing


def main(argv=None):
    parser = argparse.ArgumentParser(prog="startguess")
    parser.add_argument("--start", type=int, default=1, help="lower bound (inclusive)")
    parser.add_argument("--end", type=int, default=100, help="upper bound (inclusive)")
    args = parser.parse_args(argv)

    try:
        result = startguesssing(args.start, args.end)
        return 0 if result is not None else 1
    except Exception as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
