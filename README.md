# Compactum

> Force any PDF or image under a target size — default 500 KB.
> 把任意 PDF 或图片强制压到指定大小 —— 默认 500 KB。

[![Release](https://img.shields.io/github/v/release/ViveSieg/compactum?display_name=tag)](https://github.com/ViveSieg/compactum/releases)
[![License: PolyForm NC](https://img.shields.io/badge/License-PolyForm%20Noncommercial-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)]()
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A polished cross-platform desktop app for shrinking PDFs and images to **a hard size limit you choose**. Drop a file, hit Start, get an output that's mathematically guaranteed below the cap. Built for visa applications, school portals, government forms, and any system with a "≤ 500 KB / 1 MB / 2 MB" upload limit.

适合签证、学校官网、政府办事系统等"文件必须 ≤ 500KB"的硬限制场景。拖入 PDF 或图片、点开始，输出**严格不超**目标大小。

**Supported inputs · 支持格式**: PDF · JPG · PNG · WebP · BMP · TIFF · GIF

---

## 🇨🇳 中文 · 快速开始

### 方式 1 · 下载即用（推荐给电脑小白）

去 [Releases 页面](https://github.com/ViveSieg/compactum/releases/latest) 下载对应你系统的版本：

| 系统 | 下载文件 | 用法 |
|---|---|---|
| **Windows** | `Compactum-Windows.zip` | 解压，双击 `Compactum.exe` |
| **macOS** | `Compactum-macOS.zip` | 解压，双击 `Compactum.app` |
| **Linux** | `Compactum-Linux.tar.gz` | 解压，运行 `./Compactum` |

> ⚠️ macOS 第一次打开可能会提示"无法验证开发者"。右键 → 打开 → 仍要打开。

打开后：

1. 选择模式 —— **PDF → 图片**（每页一张 JPG）或 **PDF → 压缩 PDF**（整份）
2. 把 PDF 拖进窗口（或点 Browse files 选）
3. 选目标大小（200 KB / 500 KB / 1 MB / 2 MB / 自定义）
4. 点 **Start**

输出会自动保存在**原 PDF 同目录**下：
- 模式 A → `<文件名>_jpg_500kb/` 文件夹（里面是每页一张的 JPG）
- 模式 B → `<文件名>_compressed_500kb.pdf` 单文件

### 方式 2 · 装 Python 包

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum
pip install -e .

compactum        # 打开 GUI
compactum-jpg input.pdf --max-kb 500   # 命令行：转 JPG
compactum-pdf input.pdf --max-kb 500   # 命令行：压缩 PDF
```

---

## 🇺🇸 English · Quick start

### Option 1 · Download a prebuilt binary (recommended)

Grab the right file from [Releases](https://github.com/ViveSieg/compactum/releases/latest):

| Platform | Download | How to run |
|---|---|---|
| **Windows** | `Compactum-Windows.zip` | Unzip, double-click `Compactum.exe` |
| **macOS** | `Compactum-macOS.zip` | Unzip, double-click `Compactum.app` |
| **Linux** | `Compactum-Linux.tar.gz` | Untar, run `./Compactum` |

> ⚠️ macOS Gatekeeper may block on first launch. Right-click → Open → Open anyway.

Then:

1. Pick a mode — **PDF → Images** (one JPG per page) or **PDF → Smaller PDF**.
2. Drop a PDF in (or click *Browse files*).
3. Choose a target size (200 KB / 500 KB / 1 MB / 2 MB / custom).
4. Click **Start**.

The output is saved next to your original PDF:
- Mode A → folder `<name>_jpg_500kb/` with one JPG per page.
- Mode B → file `<name>_compressed_500kb.pdf`.

### Option 2 · Install as a Python package

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum
pip install -e .

compactum        # launches the GUI
compactum-jpg input.pdf --max-kb 500
compactum-pdf input.pdf --max-kb 500
```

---

## ✨ Features · 功能

- ✅ **Hard size guarantee** — output is verified ≤ target bytes; if it can't fit, the program errors instead of silently producing oversized files.
  **强制硬命中**目标大小，输出超标会直接报错，绝不静默产出。
- ✅ **Two modes** — page-by-page JPG or single rebuilt PDF.
  **两种模式** —— 每页一张 JPG / 整份重建的 PDF。
- ✅ **Cross-platform** — macOS / Windows / Linux, prebuilt binaries.
  **跨平台**，三大系统都有现成可执行文件。
- ✅ **100% offline** — files never leave your computer.
  **完全离线**，文件不会上传任何服务器。
- ✅ **Drag & drop** — no command line needed.
  **拖拽即用**，无需命令行。
- ✅ **Render-scale control** — tune sharpness vs. starting file size (default **1.5×** to prioritize hitting the size cap).
  可调**渲染倍率**平衡清晰度（默认 **1.5×**，优先保证压缩成功）。
- ✅ **Skip-limit option** — convert at native quality with no size enforcement when you only need format conversion.
  **可关闭压缩**，按原画质输出，仅做格式转换时使用。
- ✅ **Honest reporting** — Mode B shows the **actual** effective render scale (after auto-shrink) and final JPEG quality, so you know if your request was downscaled to hit the limit.
  Mode B 会显示**实际生效的渲染倍率**和最终 JPEG 质量 —— 如果你设的倍率过高被自动压低，会明确告诉你。

---

## 🧪 How it works · 工作原理

Two-stage binary search — provably **rate-distortion optimal** under uniform-scale, uniform-quality constraints.
两段二分搜索 —— 在统一倍率、统一质量的约束下，**信息论上最优**。

1. **Render**: PDF pages to bitmap via [pypdfium2](https://github.com/pypdfium2-team/pypdfium2); images loaded directly via [Pillow](https://python-pillow.org/).
   PDF 页面用 pypdfium2 栅格化；图片用 Pillow 直读。
2. **Stage 1 — maximize render scale**: 14-iteration binary search for the **largest resize ratio** where minimum-quality JPEG encoding still fits the byte budget. ~6×10⁻⁵ precision.
   **第一阶段 — 最大化渲染倍率**：14 次二分搜索找出"最低质量编码仍≤目标"的**最大缩放比**，精度约 6×10⁻⁵。
3. **Stage 2 — maximize JPEG quality**: at that resize, ~7-iteration binary search for the highest quality `q ∈ [5, 95]` whose bytes ≤ target.
   **第二阶段 — 最大化 JPEG 质量**：在该尺寸下二分搜索最高质量。
4. **Verify**: post-write disk size check; throws if it exceeds the cap (never happens, but the check is enforced).
   写盘后强制校验，超标直接报错。

---

## 🛠 Build from source · 从源码打包

```bash
pip install -r requirements.txt
pip install pyinstaller

pyinstaller build/compactum.spec --noconfirm --clean
# Output in dist/
```

GitHub Actions auto-builds binaries for all three platforms on every `v*` tag — see `.github/workflows/release.yml`.
推送 `v*` tag 会自动通过 GitHub Actions 编译三平台二进制并发布到 Releases。

---

## 📦 Project layout · 项目结构

```
compactum/
├── src/compactum/
│   ├── core.py          # cross-platform compressor (pypdfium2 + Pillow)
│   ├── gui.py           # pywebview bridge
│   ├── cli.py           # CLI entry points
│   └── webui/           # DSFR-styled HTML/CSS/JS frontend
│       ├── index.html
│       ├── style.css
│       ├── app.js
│       └── fonts/       # Marianne (Etalab Open License)
├── build/compactum.spec    # PyInstaller spec
├── .github/workflows/release.yml
├── pyproject.toml
└── README.md
```

---

## ⚠️ Notes · 注意事项

- **Mode B rebuilds the PDF as an image-based PDF.** Searchable text, vectors, hyperlinks, bookmarks and form fields will be lost.
  **模式 B 会把 PDF 重建成图片版**。可搜索文字、矢量内容、超链接、书签、表单字段会丢失。
- For very small targets with lots of pages (e.g. 100 pages → 500 KB), resolution will be aggressive — that's the cost of a hard cap.
  目标极小 + 页数极多时，分辨率会被压得很低，这是硬约束的必然代价。

---

## 📄 License · 许可

[**PolyForm Noncommercial License 1.0.0**](LICENSE) — free for personal, educational, research, and non-profit use. **Commercial use is not permitted.**

[**PolyForm Noncommercial License 1.0.0**](LICENSE) —— 个人、教育、研究、非营利用途免费。**禁止商业使用。**

For commercial licensing, contact the author via GitHub.
商业授权请通过 GitHub 联系作者。

---

## 🙌 Credits · 致谢

- PDF rendering by [pypdfium2](https://github.com/pypdfium2-team/pypdfium2).
- Image encoding by [Pillow](https://python-pillow.org/).
- Desktop wrapper by [pywebview](https://pywebview.flowrl.com/).
