"""Cross-platform PDF rasterization + size-bounded compression.

Uses pypdfium2 (Apache 2.0 / BSD-3) for PDF rendering — works on
macOS, Windows, and Linux without native system dependencies.

Compression algorithm — two-stage binary search (rate-distortion optimal
under uniform-resize, uniform-quality constraints):

  Stage 1 — maximize render scale:
    Binary-search the largest resize ratio r ∈ (eps, 1.0] such that
    encoding at r × original, MIN_QUALITY still fits the byte budget.
    14 iterations → 6×10⁻⁵ precision on the ratio.

  Stage 2 — maximize JPEG quality at that scale:
    Binary-search q ∈ [MIN_QUALITY, MAX_QUALITY] for the largest q
    where encoded bytes ≤ budget. ~7 iterations on a 91-step range.

Decomposing the 2-D problem into two 1-D binary searches is correct
because file size is monotone non-decreasing in both axes. The output
is provably optimal under the constraint that every page shares the
same scale and quality.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable

import pypdfium2 as pdfium
from PIL import Image


MIN_QUALITY = 5
MAX_QUALITY = 95
MIN_SIDE = 64
NATIVE_QUALITY = 95   # used when compress=False

ProgressFn = Callable[[dict], None]


@dataclass
class JpgResult:
    output_dir: Path
    files: list[Path]
    input_size: int = 0
    total_output_size: int = 0


@dataclass
class PdfResult:
    output_path: Path
    input_size: int = 0
    output_size: int = 0
    effective_scale: float = 0.0
    quality: int = 0


# -----------------------------------------------------------------
# rendering
# -----------------------------------------------------------------

def render_pages(pdf_path: Path, scale: float) -> list[Image.Image]:
    """Render every page of a PDF to PIL Images at the given scale."""
    pdf = pdfium.PdfDocument(str(pdf_path))
    images: list[Image.Image] = []
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            pil_image = page.render(scale=scale).to_pil()
            images.append(_to_rgb(pil_image))
            page.close()
    finally:
        pdf.close()
    return images


def _to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image.copy()
    rgba = image.convert("RGBA")
    bg = Image.new("RGB", rgba.size, "white")
    bg.paste(rgba, mask=rgba.getchannel("A"))
    return bg


# -----------------------------------------------------------------
# JPEG encoding
# -----------------------------------------------------------------

def _encode_jpeg(image: Image.Image, quality: int) -> bytes:
    buf = BytesIO()
    image.save(
        buf,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
    )
    return buf.getvalue()


def _resize_image(image: Image.Image, ratio: float) -> Image.Image:
    new_w = max(MIN_SIDE, int(round(image.width * ratio)))
    new_h = max(MIN_SIDE, int(round(image.height * ratio)))
    if new_w == image.width and new_h == image.height:
        return image
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _max_ratio_for_min_quality(image: Image.Image, target_bytes: int) -> tuple[Image.Image, float]:
    """Binary-search the largest resize ratio in (eps, 1.0] for which
    encoding the image at MIN_QUALITY fits in target_bytes.

    Returns the resized image at that ratio. This guarantees we keep the
    largest possible rendering dimensions before turning to JPEG quality.
    """
    eps = max(MIN_SIDE / image.width, MIN_SIDE / image.height)
    if eps >= 1.0:
        raise RuntimeError("Page already at minimum dimensions; cannot fit target size.")

    lo, hi = eps, 1.0
    best_image = None
    best_ratio = 0.0

    for _ in range(14):  # ~6e-5 precision
        mid = (lo + hi) / 2
        candidate = _resize_image(image, mid)
        if len(_encode_jpeg(candidate, MIN_QUALITY)) <= target_bytes:
            best_image = candidate
            best_ratio = mid
            lo = mid
        else:
            hi = mid

    if best_image is None:
        candidate = _resize_image(image, eps)
        if len(_encode_jpeg(candidate, MIN_QUALITY)) <= target_bytes:
            return candidate, eps
        raise RuntimeError("Cannot fit page in target size even at minimum dimensions.")

    return best_image, best_ratio


def _binary_search_jpeg(image: Image.Image, target_bytes: int) -> bytes:
    """Maximize render dimensions, then maximize JPEG quality, both hard-bounded by target."""
    if len(_encode_jpeg(image, MIN_QUALITY)) > target_bytes:
        image, _ = _max_ratio_for_min_quality(image, target_bytes)

    best: bytes | None = None
    lo, hi = MIN_QUALITY, MAX_QUALITY
    while lo <= hi:
        q = (lo + hi) // 2
        data = _encode_jpeg(image, q)
        if len(data) <= target_bytes:
            best = data
            lo = q + 1
        else:
            hi = q - 1
    if best is None:
        raise RuntimeError("Could not compress page below target.")
    return best


# -----------------------------------------------------------------
# Mode A: PDF -> JPGs
# -----------------------------------------------------------------

def pdf_to_jpgs(
    pdf_path: Path,
    target_kb: int,
    scale: float = 1.5,
    compress: bool = True,
    progress: ProgressFn | None = None,
) -> JpgResult:
    pdf_path = Path(pdf_path).expanduser().resolve()
    target_bytes = target_kb * 1024
    base = _safe_stem(pdf_path.stem)
    suffix = f"jpg_{target_kb}kb" if compress else "jpg_native"
    out_dir = pdf_path.parent / f"{base}_{suffix}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if progress:
        progress({"file": pdf_path.name, "msg": "Reading PDF…", "percent": 0})

    images = render_pages(pdf_path, scale)
    total = len(images)
    files: list[Path] = []

    for idx, image in enumerate(images, start=1):
        if compress:
            data = _binary_search_jpeg(image, target_bytes)
        else:
            data = _encode_jpeg(image, NATIVE_QUALITY)
        out_name = f"{base}_page-{idx:04d}.jpg"
        out_path = out_dir / out_name
        out_path.write_bytes(data)

        if compress and out_path.stat().st_size > target_bytes:
            raise RuntimeError(
                f"Output {out_path.name} = {out_path.stat().st_size} bytes "
                f"exceeded the {target_bytes}-byte hard limit."
            )
        files.append(out_path)

        if progress:
            progress({
                "file": pdf_path.name,
                "page": idx,
                "total": total,
                "percent": int(idx / total * 100),
                "msg": f"Page {idx}/{total}" + ("" if compress else " (native quality)"),
            })

    return JpgResult(
        output_dir=out_dir,
        files=files,
        input_size=pdf_path.stat().st_size,
        total_output_size=sum(p.stat().st_size for p in files),
    )


# -----------------------------------------------------------------
# Mode B: PDF -> single PDF (compressed or native-quality)
# -----------------------------------------------------------------

def _build_pdf(jpegs: list[bytes], resolution: int) -> bytes:
    bufs = [BytesIO(b) for b in jpegs]
    imgs = [Image.open(b) for b in bufs]
    try:
        out = BytesIO()
        first, rest = imgs[0], imgs[1:]
        first.save(out, format="PDF", save_all=True, append_images=rest, resolution=resolution)
        return out.getvalue()
    finally:
        for img in imgs:
            img.close()
        for b in bufs:
            b.close()


def _build_at_quality(images: list[Image.Image], quality: int, scale: float) -> bytes:
    res = max(1, int(round(scale * 72)))
    jpegs = [_encode_jpeg(img, quality) for img in images]
    return _build_pdf(jpegs, resolution=res)


def _resize_all(images: list[Image.Image], ratio: float) -> list[Image.Image]:
    return [_resize_image(im, ratio) for im in images]


def _max_ratio_for_pdf(
    images: list[Image.Image], scale: float, target_bytes: int,
    progress: ProgressFn | None, file_name: str,
) -> tuple[list[Image.Image], float]:
    """Find the largest uniform resize ratio in (eps, 1.0] where the whole
    image-PDF assembled at MIN_QUALITY fits the target. Maximises render
    dimensions before sacrificing JPEG quality."""
    min_w = min(im.width for im in images)
    min_h = min(im.height for im in images)
    eps = max(MIN_SIDE / min_w, MIN_SIDE / min_h)
    if eps >= 1.0:
        raise RuntimeError("PDF pages are already at minimum dimensions.")

    lo, hi = eps, 1.0
    best_images = None
    best_ratio = 0.0

    for step in range(12):
        mid = (lo + hi) / 2
        candidate = _resize_all(images, mid)
        size = len(_build_at_quality(candidate, MIN_QUALITY, scale * mid))
        if size <= target_bytes:
            best_images = candidate
            best_ratio = mid
            lo = mid
        else:
            hi = mid
        if progress:
            pct = min(80, 10 + step * 5)
            progress({"file": file_name, "msg": f"Searching maximum scale (step {step + 1})…", "percent": pct})

    if best_images is None:
        candidate = _resize_all(images, eps)
        if len(_build_at_quality(candidate, MIN_QUALITY, scale * eps)) <= target_bytes:
            return candidate, eps
        raise RuntimeError("Cannot fit PDF in target size even at minimum dimensions.")

    return best_images, best_ratio


def pdf_to_compressed_pdf(
    pdf_path: Path,
    target_kb: int,
    scale: float = 1.5,
    compress: bool = True,
    progress: ProgressFn | None = None,
) -> PdfResult:
    pdf_path = Path(pdf_path).expanduser().resolve()
    target_bytes = target_kb * 1024
    suffix = f"compressed_{target_kb}kb" if compress else "native"
    out_path = pdf_path.with_name(f"{pdf_path.stem}_{suffix}.pdf")

    if progress:
        progress({"file": pdf_path.name, "msg": "Reading PDF…", "percent": 0})

    images = render_pages(pdf_path, scale)
    total = len(images)
    if total == 0:
        raise RuntimeError("PDF has no pages.")

    if not compress:
        if progress:
            progress({"file": pdf_path.name, "msg": "Building PDF (native quality)…", "percent": 60})
        final = _build_at_quality(images, NATIVE_QUALITY, scale)
        out_path.write_bytes(final)
        if progress:
            progress({"file": pdf_path.name, "msg": "Done", "percent": 100})
        return PdfResult(
            output_path=out_path,
            input_size=pdf_path.stat().st_size,
            output_size=out_path.stat().st_size,
            effective_scale=scale,
            quality=NATIVE_QUALITY,
        )

    if progress:
        progress({"file": pdf_path.name, "msg": "Compressing…", "percent": 10})

    # Step 1: find the largest uniform resize ratio where MIN_QUALITY fits target.
    # This maximises render scale before we sacrifice any JPEG quality.
    if len(_build_at_quality(images, MIN_QUALITY, scale)) > target_bytes:
        current, ratio = _max_ratio_for_pdf(images, scale, target_bytes, progress, pdf_path.name)
        eff_scale = scale * ratio
    else:
        current = images
        eff_scale = scale

    # Step 2: at that resize, binary-search JPEG quality up.
    if progress:
        progress({"file": pdf_path.name, "msg": "Maximizing JPEG quality…", "percent": 85})

    best = _build_at_quality(current, MIN_QUALITY, eff_scale)
    best_q = MIN_QUALITY
    lo, hi = MIN_QUALITY + 1, MAX_QUALITY
    while lo <= hi:
        q = (lo + hi) // 2
        data = _build_at_quality(current, q, eff_scale)
        if len(data) <= target_bytes:
            best = data
            best_q = q
            lo = q + 1
        else:
            hi = q - 1

    final = best
    final_quality = best_q
    out_path.write_bytes(final)
    if out_path.stat().st_size > target_bytes:
        raise RuntimeError(
            f"Output PDF = {out_path.stat().st_size} bytes "
            f"exceeded the {target_bytes}-byte hard limit."
        )
    if progress:
        progress({"file": pdf_path.name, "msg": "Done", "percent": 100})
    return PdfResult(
        output_path=out_path,
        input_size=pdf_path.stat().st_size,
        output_size=out_path.stat().st_size,
        effective_scale=eff_scale,
        quality=final_quality,
    )


# -----------------------------------------------------------------
# helpers
# -----------------------------------------------------------------

def _safe_stem(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "pdf"


SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif", ".heic", ".heif"}


@dataclass
class ImageResult:
    output_path: Path
    input_size: int = 0
    output_size: int = 0


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_IMAGE_EXTS


def is_pdf_path(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def compress_image(
    image_path: Path,
    target_kb: int,
    compress: bool = True,
    progress: ProgressFn | None = None,
) -> ImageResult:
    """Compress a single image (any Pillow-readable format) into a JPG ≤ target_kb.

    Output is always JPEG since arbitrary formats can't be hard-bounded
    losslessly. Output filename: <stem>_<target>kb.jpg next to the input.
    """
    image_path = Path(image_path).expanduser().resolve()
    target_bytes = target_kb * 1024
    base = _safe_stem(image_path.stem)
    suffix = f"{target_kb}kb" if compress else "native"
    out_path = image_path.parent / f"{base}_{suffix}.jpg"

    if progress:
        progress({"file": image_path.name, "msg": "Reading image…", "percent": 5})

    with Image.open(image_path) as raw:
        raw.load()
        # Honor EXIF orientation if present
        try:
            from PIL import ImageOps
            raw = ImageOps.exif_transpose(raw)
        except Exception:
            pass
        image = _to_rgb(raw)

    if progress:
        progress({"file": image_path.name, "msg": "Compressing…", "percent": 30})

    if compress:
        data = _binary_search_jpeg(image, target_bytes)
    else:
        data = _encode_jpeg(image, NATIVE_QUALITY)

    out_path.write_bytes(data)
    if compress and out_path.stat().st_size > target_bytes:
        raise RuntimeError(
            f"Output {out_path.name} = {out_path.stat().st_size} bytes "
            f"exceeded the {target_bytes}-byte hard limit."
        )

    if progress:
        progress({"file": image_path.name, "msg": "Done", "percent": 100})

    return ImageResult(
        output_path=out_path,
        input_size=image_path.stat().st_size,
        output_size=out_path.stat().st_size,
    )


def page_count(pdf_path: Path) -> int:
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        return len(pdf)
    finally:
        pdf.close()
