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
        # pywebview 6.x exposes real OS file paths via the DOM 'drop' event:
        # subscribe to drop on the #drop element after the page loads, then
        # each dropped file gets a `pywebviewFullPath` field with the real
        # NSURL/Win/GTK path. Works on all four backends.
        try:
            window.events.loaded += self._wire_native_dom_drop
        except Exception as e:
            print(f"[compactum] cannot subscribe to loaded event: {e}", flush=True)

    def _wire_native_dom_drop(self) -> None:
        try:
            from webview.dom import DOMEventHandler  # type: ignore
            drop_el = self._window.dom.get_element("#drop") if self._window else None
            if drop_el is None:
                print("[compactum] #drop element not found at load time", flush=True)
                return
            drop_el.events.drop += DOMEventHandler(
                self._on_dom_drop, prevent_default=True, stop_propagation=True
            )
            print("[compactum] DOM drop handler wired", flush=True)
        except Exception as e:
            print(f"[compactum] DOM drop wiring failed: {e}", flush=True)

    def _on_dom_drop(self, event) -> None:
        try:
            data_transfer = (event or {}).get("dataTransfer") or {}
            files = data_transfer.get("files") or []
            descriptors: list[dict[str, Any]] = []
            for f in files:
                full = f.get("pywebviewFullPath") if isinstance(f, dict) else None
                if not full:
                    continue
                path = Path(full)
                if path.exists() and self._is_supported(path):
                    descriptors.append(self._describe(path))
            if descriptors and self._window is not None:
                self._window.evaluate_js(
                    f"window.onNativeFileDrop({json.dumps(descriptors)})"
                )
                print(f"[compactum] delivered {len(descriptors)} dropped path(s)", flush=True)
        except Exception as e:
            print(f"[compactum] _on_dom_drop error: {e}", flush=True)

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
        """Reveal the output in the OS file manager — never auto-open the
        file's contents. Each platform uses its native 'select & reveal'
        command, falling back to the parent directory if needed.
        """
        path = Path(path_str)
        if not path.exists():
            return
        system = platform.system()
        try:
            if system == "Darwin":
                # 'open -R' reveals path in its parent Finder window
                subprocess.run(["open", "-R", str(path)], check=False)
            elif system == "Windows":
                # 'explorer /select,<path>' highlights path in its parent
                # Explorer window. Works for both files and folders.
                subprocess.run(["explorer", f"/select,{path}"], check=False)
            else:
                # Linux: try DBus FileManager1 (works on most modern DEs);
                # then DE-specific --select fallbacks; finally xdg-open the
                # parent directory.
                parent = path if path.is_dir() else path.parent
                attempts = (
                    ["dbus-send", "--session",
                     "--dest=org.freedesktop.FileManager1",
                     "--type=method_call",
                     "/org/freedesktop/FileManager1",
                     "org.freedesktop.FileManager1.ShowItems",
                     f"array:string:file://{path}", "string:"],
                    ["nautilus", "--select", str(path)],
                    ["dolphin", "--select", str(path)],
                    ["nemo", str(path)],
                )
                ok = False
                for cmd in attempts:
                    try:
                        r = subprocess.run(cmd, check=False,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                        if r.returncode == 0:
                            ok = True
                            break
                    except FileNotFoundError:
                        continue
                if not ok:
                    subprocess.run(["xdg-open", str(parent)], check=False)
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
        width=940,
        height=740,
        min_size=(800, 620),
        resizable=True,
    )
    api.attach(window)
    webview.start()
    return 0


if __name__ == "__main__":
    sys.exit(launch())
