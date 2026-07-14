"""CLI entry point for Ghost Font decoder."""

import argparse
import sys
from pathlib import Path
from decoder import decode, try_ocr, save_result, open_result


def main():
    parser = argparse.ArgumentParser(
        prog="ghost-decode",
        description="Decode Ghost Font videos using motion-difference accumulation.",
    )
    parser.add_argument("video", help="Path to Ghost Font video file")
    parser.add_argument("-o", "--output", help="Save decoded image to file")
    parser.add_argument("-t", "--threshold", type=int, default=5,
                        help="Motion sensitivity threshold (default: 5, lower=more sensitive)")
    parser.add_argument("-b", "--blur", type=int, default=1,
                        help="Gaussian blur kernel size, 0 to skip (default: 1)")
    parser.add_argument("-m", "--method", choices=["raw", "binary"], default="raw",
                        help="Detection method: 'raw' accumulates unscaled differences (best), 'binary' thresholds each frame")
    parser.add_argument("--ocr", action="store_true", help="Attempt OCR on the result")
    parser.add_argument("--no-show", action="store_true", help="Don't show the result window")

    args = parser.parse_args()

    if not Path(args.video).exists():
        print(f"Error: file not found — {args.video}", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Processing {args.video} (method={args.method}, threshold={args.threshold}, blur={args.blur}) ...")
    try:
        result = decode(args.video, threshold=args.threshold, blur=args.blur, method=args.method)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Decoded {result.shape[1]}x{result.shape[0]} image ({result.sum() > 0} motion detected)")

    if args.output:
        save_result(result, args.output)
        print(f"[+] Saved to {args.output}")

    if args.ocr:
        text = try_ocr(result)
        print(f"[OCR] {text}")

    if not args.no_show:
        open_result(result)


if __name__ == "__main__":
    main()
