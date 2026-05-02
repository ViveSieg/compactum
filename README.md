<div align="center">

<img src="assets/logo.svg" width="96" height="96" alt="Compactum" />

# Compactum

**Force any PDF or image under a target size — the hard, honest way.**

[![Release](https://img.shields.io/github/v/release/ViveSieg/compactum?display_name=tag&style=flat-square)](https://github.com/ViveSieg/compactum/releases)
[![License: PolyForm NC](https://img.shields.io/badge/license-PolyForm%20Noncommercial-000091.svg?style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-2b2b2b.svg?style=flat-square)](#-download)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Issues](https://img.shields.io/github/issues/ViveSieg/compactum?style=flat-square)](https://github.com/ViveSieg/compactum/issues)

**[English](#-english)** · **[中文](#-中文)**

</div>

---

# 🇺🇸 English

> Drop a PDF or image, pick a target size, hit Start. The output is guaranteed below the cap when physically possible — and when it isn't, you get an honest warning instead of a silent fail.

Designed for visa applications, school portals, government forms, and any system with a hard "≤ 500 KB / 1 MB / 2 MB" upload limit.

**Supported inputs:** `PDF` · `JPG` · `PNG` · `WebP` · `BMP` · `TIFF` · `GIF`

## ⬇️ Download

> No Python install required. Just download, unzip, double-click.

| Platform | Download | How to run |
|---|---|---|
| **Windows** 10 / 11 | [⬇ Compactum-Windows.zip](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Windows.zip) | Unzip → double-click `Compactum.exe` |
| **macOS** 10.13+ | [⬇ Compactum-macOS.dmg](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-macOS.dmg) | Open the `.dmg` → drag `Compactum.app` into Applications |
| **Linux** | [⬇ Compactum-Linux.tar.gz](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Linux.tar.gz) | Untar → `./Compactum` |

> ⚠️ **macOS Gatekeeper** may say "cannot verify developer" on first launch — **right-click `Compactum.app` → Open → Open anyway**. If the app silently fails to launch (no window appears, no error), open Terminal and run:
> ```bash
> xattr -dr com.apple.quarantine /Applications/Compactum.app
> ```
> Then double-click again.

📦 All releases: [github.com/ViveSieg/compactum/releases](https://github.com/ViveSieg/compactum/releases)

## 🚀 Quick start

```
1. Open Compactum
2. Pick the output type
3. Drop a PDF or image (single or batch)
4. Pick a target size — 200 KB / 500 KB / 1 MB / …
5. Click Start
```

The output appears **right next to your original file** with a clear suffix in the name.

## 🔄 Modes — three of them

### ① PDF → Images

> **Each page becomes a separate JPG. Each JPG is compressed independently to ≤ target size.**

| | |
|---|---|
| **Input** | A PDF (any number of pages) |
| **Output** | A folder `<name>_jpg_500kb/` containing `<name>_page-0001.jpg`, `<name>_page-0002.jpg`, ... |
| **Per-file size** | ✅ Each JPG ≤ target |
| **Page count effect** | ❌ None — every page is compressed independently of every other page |
| **Best for** | Online forms requiring "each scanned page ≤ 500 KB" — visa portals, school applications, scholarship submissions |

### ② PDF → Smaller PDF

> **All pages re-rendered into a single image-based PDF. The whole PDF ≤ target size.**

| | |
|---|---|
| **Input** | A PDF |
| **Output** | A single file `<name>_compressed_500kb.pdf` |
| **Total size** | ✅ Whole file ≤ target |
| **Page count effect** | ⚠️ More pages = less budget per page = lower resolution. The *total* always stays bounded. |
| **Trade-off** | ⚠️ Output is image-based — searchable text, hyperlinks, bookmarks, form fields are **lost**. |
| **Best for** | "Single PDF must be ≤ 500 KB" portals where layout matters more than searchable text |

### ③ Image → Smaller JPG

> **One image in, one JPG out, ≤ target size. Format-agnostic input.**

| | |
|---|---|
| **Input** | A single image — JPG / PNG / WebP / BMP / TIFF / GIF (HEIC if supported by your Pillow build) |
| **Output** | `<name>_500kb.jpg` |
| **Output size** | ✅ ≤ target |
| **EXIF orientation** | ✅ Preserved — rotated phone photos open correctly |
| **Best for** | Profile photos, ID scans, exam photos, any "image upload ≤ X KB" form |

## ✨ Features

| | |
|---|---|
| 🎯 **Best-effort hard cap** | Output is always ≤ target when physically feasible. When the target is so small the content can't be represented at all, the app produces the smallest-possible result and shows a clear warning — never crashes, never silently lies. |
| 🌐 **Cross-platform** | Native Windows `.exe`, macOS `.app`, Linux binary. No Python required for end users. |
| 🔒 **100% offline** | Files never leave your machine. No telemetry, no analytics, no upload. |
| 🌍 **Bilingual UI** | English / 中文 — auto-detected from system language, manual toggle in the header. |
| 🪶 **Drag & drop** | No command line needed. Single or multiple files. |
| 📚 **Batch processing** | Drop multiple files at once — they're processed sequentially with a unified progress bar showing `[file 2/5] · current page 3/12`. |
| ⚙️ **Skip-limit option** | Toggle off the size cap to convert at native quality (handy for batch format conversion). |
| 📐 **Render-scale control** | Tune the starting bitmap resolution for PDF inputs (default 2.0×). |
| 📊 **Honest reporting** | Mode ② shows the actual effective render scale and JPEG quality after auto-shrink, so you can tell when your settings were too aggressive. |

## ⌨️ CLI

After `pip install -e .`:

```bash
compactum                                 # launch the GUI
compactum-jpg input.pdf  --max-kb 500     # PDF → folder of JPGs (mode ①)
compactum-pdf input.pdf  --max-kb 500     # PDF → single smaller PDF (mode ②)
compactum-img photo.png  --max-kb 500     # image → JPG (mode ③)
```

**Arguments:**

```
--max-kb N      Target size in KB (default 500). Output is hard-capped at N×1024 bytes when feasible.
--scale F       Initial render scale for PDFs, 1.0–3.0 (default 2.0). Image mode ignores this.
--version       Show version.
```

## 🛠 Build from source

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum

# Run from source (Python 3.9+)
pip install -r requirements.txt
python -m compactum

# Build a standalone binary for your platform
pip install pyinstaller
pyinstaller build/compactum.spec --noconfirm --clean
# Output appears in dist/
```

GitHub Actions automatically builds binaries for **macOS / Windows / Linux** on every `v*` tag and attaches them to a Release. See [`.github/workflows/release.yml`](.github/workflows/release.yml).

## ❓ FAQ

**Q: My output is over the target — bug?**
A: When the target is so small that even minimum-resolution + lowest-quality encoding still exceeds it, the algorithm produces the smallest-possible output and clearly warns you. **Increase the target size.**

**Q: Does it work offline?**
A: Yes, fully. No network calls. Files never leave your computer.

**Q: Will Mode ② keep my searchable text / hyperlinks / form fields?**
A: No. Mode ② rebuilds the PDF as an image-based PDF. If you need to keep searchable text, use Mode ①. If your goal is "small PDF that still has search", Compactum isn't the right tool.

**Q: Can I use it commercially?**
A: No. Compactum is licensed under PolyForm Noncommercial 1.0.0. For commercial use, contact the author via GitHub.

---

# 🇨🇳 中文

> 拖入 PDF 或图片，选目标大小，点开始。物理可行时输出**严格不超**目标大小；连最小尺寸都塞不下时给出明确告警，**绝不报错、绝不静默撒谎**。

适合签证、学校官网、政府办事系统等"文件必须 ≤ 500KB / 1MB / 2MB"的硬限制场景。

**支持格式：** `PDF` · `JPG` · `PNG` · `WebP` · `BMP` · `TIFF` · `GIF`

## ⬇️ 下载

> **不需要装 Python**，下载即用。

| 系统 | 下载 | 使用 |
|---|---|---|
| **Windows** 10 / 11 | [⬇ Compactum-Windows.zip](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Windows.zip) | 解压 → 双击 `Compactum.exe` |
| **macOS** 10.13+ | [⬇ Compactum-macOS.dmg](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-macOS.dmg) | 打开 `.dmg` → 把 `Compactum.app` 拖进"应用程序" |
| **Linux** | [⬇ Compactum-Linux.tar.gz](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Linux.tar.gz) | 解压 → 运行 `./Compactum` |

> ⚠️ **macOS Gatekeeper**：第一次打开可能提示"无法验证开发者" —— **右键 `Compactum.app` → 打开 → 仍要打开**。如果双击没反应、没窗口、没报错，打开 Terminal 跑一次：
> ```bash
> xattr -dr com.apple.quarantine /Applications/Compactum.app
> ```
> 然后再双击就行。

📦 所有版本：[github.com/ViveSieg/compactum/releases](https://github.com/ViveSieg/compactum/releases)

## 🚀 快速开始

```
1. 打开 Compactum
2. 选择输出类型
3. 拖入 PDF 或图片（支持批量）
4. 选目标大小 —— 200 KB / 500 KB / 1 MB / …
5. 点 开始
```

输出**直接放在原文件旁边**，文件名带清晰的后缀。

## 🔄 三种模式

### ① PDF → 图片

> **每页变成一张独立的 JPG，每张单独压缩到 ≤ 目标大小。**

| | |
|---|---|
| **输入** | 一份 PDF（任意页数） |
| **输出** | 文件夹 `<文件名>_jpg_500kb/`，里面是 `<文件名>_page-0001.jpg`、`<文件名>_page-0002.jpg`、... |
| **单文件大小** | ✅ 每张 JPG 都 ≤ 目标 |
| **页数影响** | ❌ **无影响** —— 每页单独处理，互不影响 |
| **典型场景** | 网申要求"每页扫描件 ≤ 500KB" —— 签证、学校申请、奖学金材料 |

### ② PDF → 压缩 PDF

> **所有页面重新渲染拼成一份图片版 PDF，整份文件 ≤ 目标大小。**

| | |
|---|---|
| **输入** | 一份 PDF |
| **输出** | 单文件 `<文件名>_compressed_500kb.pdf` |
| **总大小** | ✅ 整份 ≤ 目标 |
| **页数影响** | ⚠️ 页数越多 → 每页能分到的字节越少 → 分辨率被压低（**总和**始终不超目标） |
| **代价** | ⚠️ 输出是图片版 PDF —— 可搜索文字、超链接、书签、表单字段会**全部丢失** |
| **典型场景** | 系统只接受"一份 PDF ≤ 500KB"，且更看重排版而非文字可搜索 |

### ③ 图片 → 压缩 JPG

> **单张图进、单张 JPG 出，≤ 目标大小。输入格式不限。**

| | |
|---|---|
| **输入** | 单张图片 —— JPG / PNG / WebP / BMP / TIFF / GIF（如果你的 Pillow 支持，HEIC 也行） |
| **输出** | `<文件名>_500kb.jpg` |
| **输出大小** | ✅ ≤ 目标 |
| **EXIF 方向** | ✅ 保留 —— 手机竖拍照片不会歪 |
| **典型场景** | 证件照、考试照、各种"图片 ≤ X KB"上传场景 |

## ✨ 功能亮点

| | |
|---|---|
| 🎯 **尽力硬命中目标** | 物理可行时**严格不超**目标大小；连最小尺寸都塞不下时输出最小可行结果并明确告警，绝不崩溃、绝不撒谎。 |
| 🌐 **跨平台** | Windows `.exe` / macOS `.app` / Linux 原生二进制。用户**不需要装 Python**。 |
| 🔒 **完全离线** | 文件永远不离开你的电脑。零联网、零追踪、零上传。 |
| 🌍 **中英双语** | 自动跟随系统语言，可在右上角手动切换。 |
| 🪶 **拖拽即用** | 不需要命令行。支持单文件和批量。 |
| 📚 **批量处理** | 一次拖多个文件，按顺序处理，进度条显示 `[第 2/5 个] · 当前 3/12 页`。 |
| ⚙️ **可关闭压缩** | 关掉大小限制按原画质输出 —— 仅做格式转换时用。 |
| 📐 **渲染倍率可调** | PDF 输入的起点分辨率可调（默认 2.0×）。 |
| 📊 **诚实报告** | 模式 ② 显示**实际生效的渲染倍率**和最终 JPEG 质量 —— 你设的参数被自动调整时会明确告诉你。 |

## ⌨️ 命令行

`pip install -e .` 之后：

```bash
compactum                                 # 打开 GUI
compactum-jpg input.pdf  --max-kb 500     # PDF → 多张 JPG（模式 ①）
compactum-pdf input.pdf  --max-kb 500     # PDF → 压缩 PDF（模式 ②）
compactum-img photo.png  --max-kb 500     # 图片 → 压缩 JPG（模式 ③）
```

**参数：**

```
--max-kb N      目标大小（KB），默认 500。物理可行时硬命中 N×1024 字节。
--scale F       PDF 起点渲染倍率，1.0–3.0，默认 2.0。图片模式忽略此参数。
--version       显示版本号。
```

## 🛠 从源码编译

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum

# 直接源码运行（需 Python 3.9+）
pip install -r requirements.txt
python -m compactum

# 自己打包当前平台的二进制
pip install pyinstaller
pyinstaller build/compactum.spec --noconfirm --clean
# 输出在 dist/ 目录
```

推送 `v*` tag 会自动通过 GitHub Actions 编译三平台二进制并发布到 Releases。详见 [`.github/workflows/release.yml`](.github/workflows/release.yml)。

## ❓ 常见问题

**Q：输出超过了目标大小，是 bug 吗？**
A：当目标小到连最低分辨率最低质量都塞不下时，算法会输出最小可行结果并明确告警。**调大目标大小即可。**

**Q：能完全离线用吗？**
A：可以，100% 离线。零联网，文件不离开你的电脑。

**Q：模式 ② 会保留可搜索文字 / 超链接 / 表单字段吗？**
A：不会。模式 ② 把 PDF 重建成图片版，文字搜索、超链接、表单字段会全部丢失。要保留可搜索文字请用模式 ①。如果你需要的是"压缩了还能搜索"的 PDF，本工具不适合。

**Q：可以商用吗？**
A：**不可以**。本项目采用 PolyForm Noncommercial 1.0.0 许可。商业用途请通过 GitHub 联系作者。

---

## 📦 Project layout

```text
compactum/
├── src/compactum/
│   ├── core.py             # size-bounded compressor (PDFs + images)
│   ├── gui.py              # pywebview bridge
│   ├── cli.py              # CLI entry points
│   └── webui/              # bilingual HTML/CSS/JS frontend
│       ├── index.html
│       ├── style.css
│       ├── app.js
│       ├── donate/         # support-the-author QR codes
│       └── fonts/          # Marianne (Etalab Open License)
├── build/compactum.spec    # PyInstaller spec (Win/Mac/Linux)
├── .github/workflows/
│   └── release.yml         # auto-build on v* tags
├── assets/
│   ├── logo.svg
│   └── wordmark.svg
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 📄 License · 许可

[**PolyForm Noncommercial License 1.0.0**](LICENSE)

Free for personal, educational, research, government, charitable, and other non-commercial uses. **Commercial use is not permitted.** For commercial licensing, contact the author via GitHub.

个人 / 教育 / 研究 / 公益 / 政府用途免费。**禁止商业使用。** 商业授权请通过 GitHub 联系作者。

Copyright (c) 2026 ViveSieg. All rights reserved.

---

## 🙌 Credits

- PDF rendering — [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
- Image encoding — [Pillow](https://python-pillow.org/)
- Desktop wrapper — [pywebview](https://pywebview.flowrl.com/)
- Marianne font © Etalab — [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)

---

<div align="center">

**If Compactum saved you some pain, [⭐ star the repo](https://github.com/ViveSieg/compactum) — it costs nothing and means a lot.**
**如果本工具帮到了你，[⭐ 点个 star](https://github.com/ViveSieg/compactum) 是对作者最大的鼓励。**

</div>
