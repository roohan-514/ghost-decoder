"""CLI entry point for Ghost Font decoder."""

import argparse
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from decoder import decode, save_result, export_pdf, export_text, open_result


def main():
    parser = argparse.ArgumentParser(
        prog="ghost-decode",
        description="Decode Ghost Font videos — reveal messages hidden in motion.",
    )
    parser.add_argument("video", help="Path to Ghost Font video file")
    parser.add_argument("-o", "--output", help="Save decoded image (PNG) to file")
    parser.add_argument("--pdf", help="Export result as PDF")
    parser.add_argument("--txt", help="Export decoded text as TXT")
    parser.add_argument("-t", "--threshold", type=int, default=99)
    parser.add_argument("-b", "--blur", type=int, default=5)
    parser.add_argument("-m", "--method", choices=["transition", "dark", "raw"], default="transition")
    parser.add_argument("--no-show", action="store_true", help="Don't show the result window")

    args = parser.parse_args()

    if not Path(args.video).exists():
        print(f"Error: file not found — {args.video}", file=sys.stderr)
        sys.exit(1)

    def progress(pct, msg):
        bar = "#" * (pct // 5) + "." * (20 - pct // 5)
        sys.stdout.write(f"\r  [{bar}] {pct}%  {msg}")
        sys.stdout.flush()

    print(f"  Processing: {Path(args.video).name}")
    try:
        img, text = decode(args.video, threshold=args.threshold,
                           blur=args.blur, method=args.method,
                           progress_callback=progress)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n  Size: {img.shape[1]}x{img.shape[0]}")
    print(f"  Motion detected: {img.sum() > 0}")
    print(f"  Decoded text: {text or '(none)'}")

    if args.output:
        save_result(img, args.output)
        print(f"  Image saved: {args.output}")

    if args.pdf:
        export_pdf(text, img, args.pdf)
        print(f"  PDF saved: {args.pdf}")

    if args.txt:
        export_text(text, args.txt)
        print(f"  Text saved: {args.txt}")

    if not args.no_show:
        open_result(img)


if __name__ == "__main__":
    main()
