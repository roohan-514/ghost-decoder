#!/usr/bin/env python3
"""Ghost Font Decoder — decode anti-AI videos using motion accumulation."""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Ghost Font Decoder — reveal messages hidden in motion-based anti-AI videos.",
    )
    parser.add_argument("video", nargs="?", help="Path to Ghost Font video file")
    parser.add_argument("-o", "--output", help="Save decoded image to file")
    parser.add_argument("-t", "--threshold", type=int, default=5, help="Motion sensitivity (default: 5)")
    parser.add_argument("-b", "--blur", type=int, default=1, help="Gaussian blur kernel (default: 1)")
    parser.add_argument("-m", "--method", choices=["raw", "binary"], default="raw", help="Detection method")
    parser.add_argument("--ocr", action="store_true", help="Attempt OCR on the result")
    parser.add_argument("--no-show", action="store_true", help="Don't show the result window")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI (default if no video arg)")

    args = parser.parse_args()

    if args.gui or not args.video:
        from gui import GhostDecoderGUI
        GhostDecoderGUI().run()
    else:
        from cli import main as cli_main
        sys.argv = [sys.argv[0], args.video]
        if args.output:
            sys.argv += ["-o", args.output]
        if args.threshold != 5:
            sys.argv += ["-t", str(args.threshold)]
        if args.blur != 1:
            sys.argv += ["-b", str(args.blur)]
        if args.method != "raw":
            sys.argv += ["-m", args.method]
        if args.ocr:
            sys.argv.append("--ocr")
        if args.no_show:
            sys.argv.append("--no-show")
        cli_main()


if __name__ == "__main__":
    main()
