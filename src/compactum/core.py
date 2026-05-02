"""Cross-platform size-bounded compression for PDFs and images."""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable

import pypdfium2 as pdfium
from PIL import Image, ImageOps


MIN_QUALITY = 5
MAX_QUALITY = 95
MIN_SIDE = 64
NATIVE_QUALITY = 95

ProgressFn = Callable[[dict], None]

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif", ".heic", ".heif"}


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


@dataclass
class ImageResult:
    output_path: Path
    input_size: int = 0
    output_size: int = 0


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_IMAGE_EXTS


def is_pdf_path(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def page_count(pdf_path: Path) -> int:
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        return len(pdf)
    finally:
        pdf.close()


def render_pages(pdf_path: Path, scale: float) -> list[Image.Image]:
    pdf = pdfium.PdfDocument(str(pdf_path))
    images: list[Image.Image] = []
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            images.append(_to_rgb(page.render(scale=scale).to_pil()))
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


def _safe_stem(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "file"


def _encode_jpeg(image: Image.Image, quality: int) -> bytes:
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True, subsampling="4:2:0")
    return buf.getvalue()


def _resize_image(image: Image.Image, ratio: float) -> Image.Image:
    new_w = max(MIN_SIDE, int(round(image.width * ratio)))
    new_h = max(MIN_SIDE, int(round(image.height * ratio)))
    if new_w == image.width and new_h == image.height:
        return image
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _max_ratio_for_image(image: Image.Image, target_bytes: int) -> Image.Image:
    eps = max(MIN_SIDE / image.width, MIN_SIDE / image.height)
    if eps >= 1.0:
        raise RuntimeError("Already at minimum dimensions; cannot fit target size.")

    lo, hi = eps, 1.0
    best: Image.Image | None = None
    for _ in range(14):
        mid = (lo + hi) / 2
        candidate = _resize_image(image, mid)
        if len(_encode_jpeg(candidate, MIN_QUALITY)) <= target_bytes:
            best = candidate
            lo = mid
        else:
            hi = mid

    if best is None:
        candidate = _resize_image(image, eps)
        if len(_encode_jpeg(candidate, MIN_QUALITY)) <= target_bytes:
            return candidate
        raise RuntimeError("Cannot fit target size at any feasible resolution.")
    return best


def _fit_image_to_budget(image: Image.Image, target_bytes: int) -> bytes:
    if len(_encode_jpeg(image, MIN_QUALITY)) > target_bytes:
        image = _max_ratio_for_image(image, target_bytes)

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
        raise RuntimeError("Could not compress within target.")
    return best


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
    return _build_pdf([_encode_jpeg(img, quality) for img in images], resolution=res)


def _resize_all(images: list[Image.Image], ratio: float) -> list[Image.Image]:
    return [_resize_image(im, ratio) for im in images]


def _max_ratio_for_pdf(
    images: list[Image.Image], scale: float, target_bytes: int,
    progress: ProgressFn | None, file_name: str,
) -> tuple[list[Image.Image], float]:
    min_w = min(im.width for im in images)
    min_h = min(im.height for im in images)
    eps = max(MIN_SIDE / min_w, MIN_SIDE / min_h)
    if eps >= 1.0:
        raise RuntimeError("Pages already at minimum dimensions.")

    lo, hi = eps, 1.0
    best: list[Image.Image] | None = None
    best_ratio = 0.0
    for step in range(12):
        mid = (lo + hi) / 2
        candidate = _resize_all(images, mid)
        if len(_build_at_quality(candidate, MIN_QUALITY, scale * mid)) <= target_bytes:
            best = candidate
            best_ratio = mid
            lo = mid
        else:
            hi = mid
        if progress:
            progress({"file": file_name, "msg": f"Searching maximum scale ({step + 1}/12)…", "percent": min(80, 10 + step * 5)})

    if best is None:
        candidate = _resize_all(images, eps)
        if len(_build_at_quality(candidate, MIN_QUALITY, scale * eps)) <= target_bytes:
            return candidate, eps
        raise RuntimeError("Cannot fit PDF in target size at any feasible resolution.")
    return best, best_ratio


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
        progress({"file": pdf_path.name, "msg": "Reading…", "percent": 0})

    images = render_pages(pdf_path, scale)
    total = len(images)
    files: list[Path] = []

    for idx, image in enumerate(images, start=1):
        data = _fit_image_to_budget(image, target_bytes) if compress else _encode_jpeg(image, NATIVE_QUALITY)
        out_path = out_dir / f"{base}_page-{idx:04d}.jpg"
        out_path.write_bytes(data)

        if compress and out_path.stat().st_size > target_bytes:
            raise RuntimeError(f"{out_path.name} exceeded the {target_bytes}-byte hard limit.")
        files.append(out_path)

        if progress:
            progress({
                "file": pdf_path.name,
                "page": idx,
                "total": total,
                "percent": int(idx / total * 100),
                "msg": f"Page {idx}/{total}" + ("" if compress else " (native)"),
            })

    return JpgResult(
        output_dir=out_dir,
        files=files,
        input_size=pdf_path.stat().st_size,
        total_output_size=sum(p.stat().st_size for p in files),
    )


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
        progress({"file": pdf_path.name, "msg": "Reading…", "percent": 0})

    images = render_pages(pdf_path, scale)
    if not images:
        raise RuntimeError("PDF has no pages.")

    if not compress:
        if progress:
            progress({"file": pdf_path.name, "msg": "Building PDF (native)…", "percent": 60})
        out_path.write_bytes(_build_at_quality(images, NATIVE_QUALITY, scale))
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

    if len(_build_at_quality(images, MIN_QUALITY, scale)) > target_bytes:
        current, ratio = _max_ratio_for_pdf(images, scale, target_bytes, progress, pdf_path.name)
        eff_scale = scale * ratio
    else:
        current = images
        eff_scale = scale

    if progress:
        progress({"file": pdf_path.name, "msg": "Tuning quality…", "percent": 85})

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

    out_path.write_bytes(best)
    if out_path.stat().st_size > target_bytes:
        raise RuntimeError(f"Output PDF exceeded the {target_bytes}-byte hard limit.")
    if progress:
        progress({"file": pdf_path.name, "msg": "Done", "percent": 100})
    return PdfResult(
        output_path=out_path,
        input_size=pdf_path.stat().st_size,
        output_size=out_path.stat().st_size,
        effective_scale=eff_scale,
        quality=best_q,
    )


def compress_image(
    image_path: Path,
    target_kb: int,
    compress: bool = True,
    progress: ProgressFn | None = None,
) -> ImageResult:
    image_path = Path(image_path).expanduser().resolve()
    target_bytes = target_kb * 1024
    base = _safe_stem(image_path.stem)
    suffix = f"{target_kb}kb" if compress else "native"
    out_path = image_path.parent / f"{base}_{suffix}.jpg"

    if progress:
        progress({"file": image_path.name, "msg": "Reading…", "percent": 5})

    with Image.open(image_path) as raw:
        raw.load()
        try:
            raw = ImageOps.exif_transpose(raw)
        except Exception:
            pass
        image = _to_rgb(raw)

    if progress:
        progress({"file": image_path.name, "msg": "Compressing…", "percent": 30})

    data = _fit_image_to_budget(image, target_bytes) if compress else _encode_jpeg(image, NATIVE_QUALITY)
    out_path.write_bytes(data)

    if compress and out_path.stat().st_size > target_bytes:
        raise RuntimeError(f"{out_path.name} exceeded the {target_bytes}-byte hard limit.")

    if progress:
        progress({"file": image_path.name, "msg": "Done", "percent": 100})

    return ImageResult(
        output_path=out_path,
        input_size=image_path.stat().st_size,
        output_size=out_path.stat().st_size,
    )
