#!/usr/bin/env python3
"""Ghost Font Decoder — launch GUI or CLI."""

import sys
import io
import argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def main():
    parser = argparse.ArgumentParser(
        description="Ghost Font Decoder — reveal messages hidden in anti-AI motion videos.",
    )
    parser.add_argument("video", nargs="?", help="Path to Ghost Font video file")
    parser.add_argument("--gui", action="store_true", help="Launch GUI (default if no video)")
    args = parser.parse_args()

    if args.gui or not args.video:
        from gui import GhostDecoderGUI
        GhostDecoderGUI().run()
    else:
        from cli import main as cli_main
        sys.argv = [sys.argv[0], args.video] + sys.argv[2:]
        cli_main()


if __name__ == "__main__":
    main()
