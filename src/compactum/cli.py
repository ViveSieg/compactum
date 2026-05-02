"""CLI entry points for Compactum."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from . import core


def _print_progress(info: dict) -> None:
    msg = info.get("msg", "")
    pct = info.get("percent")
    if pct is not None:
        print(f"  [{pct:3d}%] {msg}")
    else:
        print(f"  {msg}")


def jpg_main() -> int:
    parser = argparse.ArgumentParser(
        prog="compactum-jpg",
        description="Convert each PDF page to a JPG, every file ≤ target size.",
    )
    parser.add_argument("pdf", help="Path to input PDF.")
    parser.add_argument("--max-kb", type=int, default=500, help="Per-file size limit in KB (default: 500).")
    parser.add_argument("--scale", type=float, default=2.0, help="Initial render scale (default: 2.0).")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"Error: file not found — {pdf_path}", file=sys.stderr)
        return 2

    try:
        result = core.pdf_to_jpgs(pdf_path, args.max_kb, scale=args.scale, progress=_print_progress)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"\nDone. {len(result.files)} files written to:")
    print(f"  {result.output_dir}")
    return 0


def pdf_main() -> int:
    parser = argparse.ArgumentParser(
        prog="compactum-pdf",
        description="Compress a PDF to a single image-based PDF ≤ target size.",
    )
    parser.add_argument("pdf", help="Path to input PDF.")
    parser.add_argument("--max-kb", type=int, default=500, help="Final PDF size limit in KB (default: 500).")
    parser.add_argument("--scale", type=float, default=2.0, help="Initial render scale (default: 2.0).")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"Error: file not found — {pdf_path}", file=sys.stderr)
        return 2

    try:
        result = core.pdf_to_compressed_pdf(pdf_path, args.max_kb, scale=args.scale, progress=_print_progress)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    final_kb = result.output_path.stat().st_size / 1024
    print(f"\nDone. {final_kb:.1f} KB written to:")
    print(f"  {result.output_path}")
    return 0


def img_main() -> int:
    parser = argparse.ArgumentParser(
        prog="compactum-img",
        description="Compress a single image to a JPG ≤ target size.",
    )
    parser.add_argument("image", help="Path to input image (JPG / PNG / WebP / BMP / TIFF / GIF).")
    parser.add_argument("--max-kb", type=int, default=500, help="Output size limit in KB (default: 500).")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        print(f"Error: file not found — {image_path}", file=sys.stderr)
        return 2

    try:
        result = core.compress_image(image_path, args.max_kb, progress=_print_progress)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    final_kb = result.output_size / 1024
    print(f"\nDone. {final_kb:.1f} KB written to:")
    print(f"  {result.output_path}")
    return 0


def gui_main() -> int:
    from .gui import launch
    return launch()
