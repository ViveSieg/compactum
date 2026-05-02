"""pywebview-based GUI bridge.

Frontend calls window.pywebview.api.<method> — those map to the Api class below.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any

import webview

from . import __version__
from . import core


def _frontend_dir() -> Path:
    """Return the directory containing index.html — works in dev and PyInstaller bundle."""
    here = Path(__file__).resolve().parent
    candidate = here / "webui" / "index.html"
    if candidate.exists():
        return candidate.parent
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundled = Path(meipass) / "compactum" / "webui" / "index.html"
        if bundled.exists():
            return bundled.parent
    raise FileNotFoundError(f"Cannot locate webui/index.html (looked at {candidate})")


class Api:
    """Methods exposed to the JS frontend via pywebview's bridge."""

    def __init__(self) -> None:
        self._window: "webview.Window | None" = None

    def attach(self, window: "webview.Window") -> None:
        self._window = window

    # --------- file selection ---------

    def pickFiles(self) -> list[dict[str, Any]]:
        if self._window is None:
            return []
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=(
                "Supported (*.pdf;*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tif;*.tiff;*.gif)",
                "PDF files (*.pdf)",
                "Image files (*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tif;*.tiff;*.gif)",
                "All files (*.*)",
            ),
        )
        if not result:
            return []
        return [self._describe(Path(p)) for p in result if self._is_supported(Path(p))]

    def resolveDropped(self, paths: list[str]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for p in paths:
            path = Path(p)
            if not path.exists() or not self._is_supported(path):
                continue
            out.append(self._describe(path))
        return out

    def saveDroppedContent(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fallback for backends (notably macOS WKWebView) that don't expose
        a file path on drag-drop. The frontend reads each file as base64 and
        sends {name, b64}; we write it to a per-session temp dir and return
        regular file descriptors."""
        import base64, tempfile
        if not hasattr(self, "_drop_dir") or self._drop_dir is None:
            self._drop_dir = Path(tempfile.mkdtemp(prefix="compactum-drop-"))
        out: list[dict[str, Any]] = []
        for it in items:
            name = (it.get("name") or "file").replace("/", "_").replace("\\", "_")
            b64 = it.get("b64") or ""
            if not b64:
                continue
            target = self._drop_dir / name
            try:
                target.write_bytes(base64.b64decode(b64))
            except Exception:
                continue
            if self._is_supported(target):
                out.append(self._describe(target))
        return out

    @staticmethod
    def _is_supported(path: Path) -> bool:
        return core.is_pdf_path(path) or core.is_image_path(path)

    @staticmethod
    def _describe(path: Path) -> dict[str, Any]:
        stat = path.stat()
        return {
            "name": path.name,
            "path": str(path.resolve()),
            "size": stat.st_size,
        }

    # --------- run job ---------

    def run(self, job: dict[str, Any]) -> dict[str, Any]:
        mode = job.get("mode", "jpg")
        kb = int(job.get("kb", 500))
        scale = float(job.get("scale", 1.5))
        compress = bool(job.get("compress", True))
        paths = [Path(p) for p in job.get("paths", [])]

        if not paths:
            raise ValueError("No files provided.")
        if compress and kb < 20:
            raise ValueError("Target size must be at least 20 KB.")
        if scale < 1.0 or scale > 4.0:
            raise ValueError("Render scale must be between 1.0 and 4.0.")

        outputs: list[str] = []
        stats: list[dict[str, Any]] = []
        total_files = len(paths)

        def make_progress(file_idx: int):
            def cb(info: dict) -> None:
                pct = info.get("percent", 0)
                overall = int((file_idx + pct / 100) / total_files * 100)
                payload = dict(info)
                payload["percent"] = overall
                payload["file_idx"] = file_idx + 1
                payload["total_files"] = total_files
                self._push_progress(payload)
            return cb

        for idx, file_path in enumerate(paths):
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Image input — single-image compression, mode toggle ignored
            if core.is_image_path(file_path):
                img_result = core.compress_image(
                    file_path, kb,
                    compress=compress,
                    progress=make_progress(idx),
                )
                outputs.append(str(img_result.output_path))
                stats.append({
                    "mode": "image",
                    "name": file_path.name,
                    "input_size": img_result.input_size,
                    "output_size": img_result.output_size,
                    "cap_exceeded": img_result.cap_exceeded,
                })
                continue

            # PDF input — Mode A or Mode B per user choice
            if mode == "jpg":
                jpg_result = core.pdf_to_jpgs(
                    file_path, kb,
                    scale=scale, compress=compress,
                    progress=make_progress(idx),
                )
                outputs.append(str(jpg_result.output_dir))
                stats.append({
                    "mode": "jpg",
                    "name": file_path.name,
                    "input_size": jpg_result.input_size,
                    "output_size": jpg_result.total_output_size,
                    "page_count": len(jpg_result.files),
                    "cap_exceeded": jpg_result.cap_exceeded,
                })
            elif mode == "pdf":
                pdf_result = core.pdf_to_compressed_pdf(
                    file_path, kb,
                    scale=scale, compress=compress,
                    progress=make_progress(idx),
                )
                outputs.append(str(pdf_result.output_path))
                stats.append({
                    "mode": "pdf",
                    "name": file_path.name,
                    "input_size": pdf_result.input_size,
                    "output_size": pdf_result.output_size,
                    "effective_scale": round(pdf_result.effective_scale, 3),
                    "input_scale": scale,
                    "quality": pdf_result.quality,
                    "cap_exceeded": pdf_result.cap_exceeded,
                })
            else:
                raise ValueError(f"Unknown mode: {mode}")

        return {"outputs": outputs, "stats": stats}

    def _push_progress(self, info: dict) -> None:
        if self._window is None:
            return
        try:
            payload = json.dumps(info)
            self._window.evaluate_js(f"window.shrinkProgress({payload})")
        except Exception:
            pass

    # --------- open output ---------

    def openFolder(self, path_str: str) -> None:
        path = Path(path_str)
        target = path if path.is_dir() else path.parent
        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.run(["open", str(target)], check=False)
            elif system == "Windows":
                if path.is_file():
                    subprocess.run(["explorer", "/select,", str(path)], check=False)
                else:
                    os.startfile(str(target))  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", str(target)], check=False)
        except Exception:
            pass

    def openExternal(self, url: str) -> None:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def version(self) -> str:
        return __version__


def launch() -> int:
    api = Api()
    index_path = _frontend_dir() / "index.html"
    window = webview.create_window(
        title=f"Compactum v{__version__}",
        url=index_path.as_uri(),
        js_api=api,
        width=900,
        height=680,
        min_size=(760, 580),
        resizable=True,
    )
    api.attach(window)
    webview.start()
    return 0


if __name__ == "__main__":
    sys.exit(launch())
