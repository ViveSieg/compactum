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

## ⬇️ Download · 下载

> Pre-built binaries are published on the [**Releases page**](https://github.com/ViveSieg/compactum/releases/latest). No Python install needed — just download, unzip, double-click.
> 全部三平台二进制都在 [**Releases 页面**](https://github.com/ViveSieg/compactum/releases/latest)。**不需要装 Python**——下载、解压、双击即可。

| Platform · 系统 | Direct download · 直接下载 | What to do · 用法 |
|---|---|---|
| **Windows** 10 / 11 | [Compactum-Windows.zip](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Windows.zip) | Unzip · double-click `Compactum.exe`<br/>解压、双击 `Compactum.exe` |
| **macOS** 10.13+ | [Compactum-macOS.zip](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-macOS.zip) | Unzip · drag `Compactum.app` to Applications · open<br/>解压、把 `Compactum.app` 拖进"应用程序"、打开 |
| **Linux** | [Compactum-Linux.tar.gz](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Linux.tar.gz) | Untar · `./Compactum`<br/>解压、运行 `./Compactum` |

> ⚠️ **macOS Gatekeeper**: first launch may show "cannot verify developer" — **right-click → Open → Open anyway**.
> macOS 第一次打开可能提示"无法验证开发者"——**右键 → 打开 → 仍要打开**。

---

## 🇨🇳 中文 · 快速开始

打开后：

1. 选择**输出类型** —— PDF → 图片 / PDF → 压缩 PDF / 图片 → 压缩 JPG
2. 把文件拖进窗口（或点 *Browse files* 选）—— PDF / JPG / PNG / WebP / BMP / TIFF / GIF 都行
3. 选目标大小（200 KB / 500 KB / 1 MB / 2 MB / 5 MB / 自定义）
4. 点 **Start**

输出会自动保存在**原文件同目录**下：
- PDF→图片 → `<文件名>_jpg_500kb/` 文件夹（每页一张 JPG）
- PDF→压缩 PDF → `<文件名>_compressed_500kb.pdf`
- 图片→压缩 → `<文件名>_500kb.jpg`

### 进阶：装成 Python 包用 CLI

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum
pip install -e .

compactum                              # 打开 GUI
compactum-jpg input.pdf  --max-kb 500  # PDF → 多张 JPG
compactum-pdf input.pdf  --max-kb 500  # PDF → 压缩 PDF
compactum-img photo.png  --max-kb 500  # 图片 → 压缩 JPG
```

---

## 🇺🇸 English · Quick start

After launching:

1. Pick the **output type** — PDF → Images / PDF → Smaller PDF / Image → Smaller JPG
2. Drop a file (or click *Browse files*) — PDF / JPG / PNG / WebP / BMP / TIFF / GIF supported
3. Choose a target size (200 KB / 500 KB / 1 MB / 2 MB / 5 MB / custom)
4. Click **Start**

The output lands next to your original file:
- PDF → Images → folder `<name>_jpg_500kb/` (one JPG per page)
- PDF → Smaller PDF → `<name>_compressed_500kb.pdf`
- Image → Smaller JPG → `<name>_500kb.jpg`

### Power users: install as a Python package

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum
pip install -e .

compactum                              # launch the GUI
compactum-jpg input.pdf  --max-kb 500  # PDF → multiple JPGs
compactum-pdf input.pdf  --max-kb 500  # PDF → smaller PDF
compactum-img photo.png  --max-kb 500  # image → smaller JPG
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

## 🧪 How it works · 简介

Compactum uses a multi-stage rate-distortion search to find the best output that still fits your size cap, with a final disk-size verification before reporting success. The output is mathematically guaranteed to never exceed the limit you set.

Compactum 在保证不超目标大小的前提下，用一套自研的多阶段优化流程寻找最优输出，并在写盘后再校验一次大小。**输出严格不超**你设的上限。

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
