<div align="center">

<img src="assets/logo.svg" width="96" height="96" alt="Compactum" />

# Compactum

Force any PDF or image under a target size.

[![Release](https://img.shields.io/github/v/release/ViveSieg/compactum?display_name=tag&style=flat-square)](https://github.com/ViveSieg/compactum/releases)
[![License: PolyForm NC](https://img.shields.io/badge/license-PolyForm%20Noncommercial-000091.svg?style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-2b2b2b.svg?style=flat-square)](#-download)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Issues](https://img.shields.io/github/issues/ViveSieg/compactum?style=flat-square)](https://github.com/ViveSieg/compactum/issues)

[English](#english) · [中文](#中文)

</div>

---

## English

A cross-platform desktop app that compresses PDFs and images to a size limit you choose. The output is bounded above by your target when the input is feasible at that size; when it isn't, the app produces the smallest possible result and shows a warning.

Typical use cases: visa applications, school portals, government forms, and other systems that enforce upload limits like "≤ 500 KB", "≤ 1 MB", or "≤ 2 MB".

**Supported inputs:** PDF, JPG, JPEG, PNG, WebP, BMP, TIFF, GIF.

### ⬇️ Download

Pre-built binaries are published on the [Releases page](https://github.com/ViveSieg/compactum/releases/latest). Python is not required.

| Platform | Download | How to run |
|---|---|---|
| Windows 10 / 11 | [Compactum-Windows.exe](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Windows.exe) | Double-click `Compactum-Windows.exe`. The first launch may show a SmartScreen warning — click **More info → Run anyway**. |
| macOS 10.13+ | [Compactum-macOS.dmg](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-macOS.dmg) | Open the `.dmg`, drag `Compactum.app` into Applications, then open it from Applications. |
| Linux | [Compactum-Linux.tar.gz](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Linux.tar.gz) | Extract the archive and run `./Compactum`. |

> **macOS first launch.** The build is not signed with an Apple Developer ID, so Gatekeeper blocks the first launch.
>
> 1. Try to open `Compactum.app` once. macOS will show a "cannot verify developer" dialog. Click **Done** or **Cancel**.
> 2. Open **System Settings → Privacy & Security**, scroll down to the *Security* section, and click **Open Anyway** next to the line that mentions Compactum.
> 3. Confirm in the next dialog. The app opens. Subsequent launches do not trigger this prompt.
>
> If the app still does not launch (no window, no error in System Settings), open Terminal and run:
> ```bash
> xattr -dr com.apple.quarantine /Applications/Compactum.app
> ```
> Then open it again.

All releases: <https://github.com/ViveSieg/compactum/releases>

### Quick start

1. Open Compactum.
2. Choose an output type.
3. Drop one or more files into the window (PDF or image).
4. Choose a target size: 200 KB, 500 KB, 1 MB, 2 MB, or a custom KB value.
5. Click **Start**.

The output is written to the same directory as the input, with a suffix added to the file name.

### Modes

#### ① PDF → Images

Each page is rasterized to a separate JPG. Each output JPG is compressed independently to the target size.

| | |
|---|---|
| Input | A single PDF (any number of pages). |
| Output | A folder named `<basename>_jpg_500kb/` containing `<basename>_page-0001.jpg`, `<basename>_page-0002.jpg`, … |
| Per-file size | Each JPG is bounded by the target. |
| Page count effect | None. Each page is processed independently of the others. |
| Use case | Forms that require each scanned page to be ≤ 500 KB individually. |

#### ② PDF → Smaller PDF

All pages are rasterized and rebuilt into one image-based PDF. The whole PDF is bounded by the target size.

| | |
|---|---|
| Input | A single PDF. |
| Output | A single file `<basename>_compressed_500kb.pdf`. |
| Total size | The whole PDF is bounded by the target. |
| Page count effect | More pages share the same byte budget, which lowers the per-page resolution. The total stays bounded. |
| Trade-off | The output is image-based. Searchable text, hyperlinks, bookmarks, and form fields are not preserved. |
| Use case | Systems that accept a single PDF up to a fixed size, where layout fidelity matters more than searchable text. |

#### ③ Image → Smaller JPG

A single image is compressed to a JPG bounded by the target size. The input format can be JPG, PNG, WebP, BMP, TIFF, or GIF; the output is always JPG.

| | |
|---|---|
| Input | A single image. |
| Output | `<basename>_500kb.jpg`. |
| Output size | Bounded by the target. |
| EXIF orientation | Preserved during the rotate-to-display step. |
| Use case | Profile photos, ID scans, and other image-upload forms. |

### Features

- Cross-platform: native binaries for Windows, macOS, and Linux. End users do not need to install Python.
- Offline. No network access, no telemetry. Files do not leave the machine.
- Bilingual interface (English / 中文), auto-selected from the system language and switchable in the header.
- Drag and drop with real OS paths via pywebview's native drop handler — output lands next to the original file on every platform.
- Batch processing. Multiple files are processed in order; the progress bar shows `[file 2/5] · current page 3/12`.
- "Open output folder" reveals (highlights) the file in Finder / Explorer / your file manager — it does not auto-open the contents.
- Skip-limit option. Disable the size cap to convert at native quality without compression (useful for format conversion only).
- Render-scale control. Adjusts the starting bitmap resolution for PDF inputs (default 2.0×). Image mode does not use this setting.
- Reporting. After Mode ② finishes, the app reports the effective render scale and the JPEG quality actually used, so a user-supplied scale that had to be reduced is visible rather than hidden.

### CLI

After `pip install -e .`:

```bash
compactum                                 # launch the GUI
compactum-jpg input.pdf  --max-kb 500     # mode ①: PDF → folder of JPGs
compactum-pdf input.pdf  --max-kb 500     # mode ②: PDF → single smaller PDF
compactum-img photo.png  --max-kb 500     # mode ③: image → JPG
```

Arguments:

```
--max-kb N      Target size in KB (default: 500). Output is bounded by N × 1024 bytes when feasible.
--scale F       Initial render scale for PDF inputs, range 1.0–3.0 (default: 2.0). Ignored by image mode.
--version       Print the version and exit.
```

### Build from source

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum

# Run from source (Python 3.9+)
pip install -r requirements.txt
python -m compactum

# Build a standalone binary for the current platform
pip install pyinstaller
pyinstaller build/compactum.spec --noconfirm --clean
# Output appears in dist/
```

GitHub Actions builds binaries for macOS, Windows, and Linux on every `v*` tag and attaches them to a GitHub Release. See [`.github/workflows/release.yml`](.github/workflows/release.yml).

### FAQ

**The output is larger than the target. Is this a bug?**
No. When the target is small enough that even minimum dimensions and minimum quality cannot fit it, the algorithm produces the smallest result it can and reports the situation. Increase the target.

**Does it work offline?**
Yes. No network calls are made.

**Does Mode ② preserve searchable text, hyperlinks, or form fields?**
No. Mode ② rebuilds the PDF as image data. Use Mode ① if you need per-page output that retains image fidelity but has no searchable text either; Compactum does not produce small PDFs with searchable text.

**Can I use Compactum commercially?**
No. The license is PolyForm Noncommercial 1.0.0. Contact the author via GitHub for commercial licensing.

---

## 中文

一个跨平台桌面程序，把 PDF 或图片压缩到你指定的大小上限。物理可行时输出不会超过目标；连最小尺寸都塞不下时，输出最小可行结果并显示警告。

典型场景：签证、学校官网、政府办事系统等强制"≤ 500 KB"、"≤ 1 MB"、"≤ 2 MB"上传上限的网页表单。

**支持输入格式：** PDF、JPG、JPEG、PNG、WebP、BMP、TIFF、GIF。

### ⬇️ 下载

预编译二进制发布在 [Releases 页面](https://github.com/ViveSieg/compactum/releases/latest)。**不需要安装 Python**。

| 平台 | 下载 | 使用 |
|---|---|---|
| Windows 10 / 11 | [Compactum-Windows.exe](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Windows.exe) | 双击 `Compactum-Windows.exe`。首次运行可能弹 SmartScreen 提示，点击"更多信息 → 仍要运行"。 |
| macOS 10.13+ | [Compactum-macOS.dmg](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-macOS.dmg) | 打开 `.dmg`，把 `Compactum.app` 拖进"应用程序"文件夹，再从"应用程序"里打开。 |
| Linux | [Compactum-Linux.tar.gz](https://github.com/ViveSieg/compactum/releases/latest/download/Compactum-Linux.tar.gz) | 解压后运行 `./Compactum`。 |

> **macOS 首次打开。** 当前版本没有 Apple Developer ID 签名，首次启动会被 Gatekeeper 拦下。
>
> 1. 先双击 `Compactum.app`，会弹出"无法验证开发者"提示，点**完成**或**取消**关掉。
> 2. 打开**系统设置 → 隐私与安全性**，下拉到"安全性"区域，会看到一行提示 Compactum 被阻止，点旁边的**仍要打开**。
> 3. 弹出确认框再点一次"打开"，应用就启动了。之后再打开就不会再有提示。
>
> 如果还是打不开（没窗口、系统设置里也没相关条目），打开 Terminal 跑一次：
> ```bash
> xattr -dr com.apple.quarantine /Applications/Compactum.app
> ```
> 然后再次打开。

所有版本：<https://github.com/ViveSieg/compactum/releases>

### 快速开始

1. 打开 Compactum。
2. 选择输出类型。
3. 把一个或多个文件拖进窗口（PDF 或图片）。
4. 选目标大小：200 KB、500 KB、1 MB、2 MB，或自定义 KB 数值。
5. 点击"开始"。

输出文件保存在与输入文件相同的目录下，文件名后会附加后缀。

### 三种模式

#### ① PDF → 图片

每页单独栅格化成一张 JPG，**每张 JPG 单独**压缩到目标大小。

| | |
|---|---|
| 输入 | 一份 PDF（任意页数）。 |
| 输出 | 文件夹 `<原文件名>_jpg_500kb/`，里面是 `<原文件名>_page-0001.jpg`、`<原文件名>_page-0002.jpg`、…… |
| 单文件大小 | 每张 JPG 都 ≤ 目标。 |
| 页数影响 | 无。每页独立处理，互不影响。 |
| 适用场景 | 网页表单要求"每张扫描页 ≤ 500 KB"的场景。 |

#### ② PDF → 压缩 PDF

所有页面栅格化后拼成一份图片版 PDF，**整份 PDF** 受目标大小约束。

| | |
|---|---|
| 输入 | 一份 PDF。 |
| 输出 | 单文件 `<原文件名>_compressed_500kb.pdf`。 |
| 总大小 | 整份 PDF ≤ 目标。 |
| 页数影响 | 页数越多，每页能分到的字节越少，分辨率会被压低；总和始终不超目标。 |
| 代价 | 输出是图片版 PDF。可搜索文字、超链接、书签、表单字段会丢失。 |
| 适用场景 | 系统接受"一份 PDF ≤ 固定大小"，且更看重排版而不是文字可搜索。 |

#### ③ 图片 → 压缩 JPG

单张图片压缩到目标大小，输出统一是 JPG。输入格式可以是 JPG、PNG、WebP、BMP、TIFF、GIF。

| | |
|---|---|
| 输入 | 单张图片。 |
| 输出 | `<原文件名>_500kb.jpg`。 |
| 输出大小 | ≤ 目标。 |
| EXIF 方向 | 处理前会按 EXIF 方向旋转，不会出现照片倒着。 |
| 适用场景 | 证件照、考试照、各种图片上传表单。 |

### 功能

- 跨平台：Windows、macOS、Linux 三套原生二进制。终端用户不需要装 Python。
- 离线运行。零联网、零追踪，文件不离开本机。
- 中英双语界面，自动跟随系统语言，可在标题栏手动切换。
- 拖放即用：通过 pywebview 原生拖放事件拿到真实 OS 路径，输出直接落在原文件旁边。
- 批量处理：多个文件按顺序处理，进度条显示 `[第 2/5 个] · 当前 3/12 页`。
- "打开输出位置"会在访达 / 资源管理器 / 文件管理器中**定位高亮**输出文件，不会自动打开文件内容。
- 关闭压缩选项：关掉大小约束按原画质输出，仅做格式转换时使用。
- 渲染倍率可调：调节 PDF 输入的起点位图分辨率（默认 2.0×），图片模式不使用该参数。
- 报告：模式 ② 结束后会显示实际生效的渲染倍率和最终的 JPEG 质量；用户设置过高被自动调低时不会被隐藏。

### 命令行

`pip install -e .` 之后：

```bash
compactum                                 # 打开 GUI
compactum-jpg input.pdf  --max-kb 500     # 模式 ①：PDF → 多张 JPG
compactum-pdf input.pdf  --max-kb 500     # 模式 ②：PDF → 单份压缩 PDF
compactum-img photo.png  --max-kb 500     # 模式 ③：图片 → JPG
```

参数：

```
--max-kb N      目标大小（KB），默认 500。可行时输出 ≤ N × 1024 字节。
--scale F       PDF 输入的起点渲染倍率，1.0–3.0，默认 2.0。图片模式不使用。
--version       打印版本并退出。
```

### 从源码编译

```bash
git clone https://github.com/ViveSieg/compactum.git
cd compactum

# 直接源码运行（需 Python 3.9+）
pip install -r requirements.txt
python -m compactum

# 自己编译当前平台的二进制
pip install pyinstaller
pyinstaller build/compactum.spec --noconfirm --clean
# 产物在 dist/ 目录
```

GitHub Actions 在每次推送 `v*` tag 时编译三平台二进制并附加到 GitHub Release。详见 [`.github/workflows/release.yml`](.github/workflows/release.yml)。

### 常见问题

**输出超过目标大小，是 bug 吗？**
不是。当目标小到连最低分辨率最低质量都塞不下时，算法输出最小可行结果并报告状态。请调大目标。

**能完全离线使用吗？**
能。没有任何联网调用。

**模式 ② 会保留可搜索文字、超链接、表单字段吗？**
不会。模式 ② 把 PDF 重建成图片数据。如果需要保留这些，应使用模式 ①（仅按图片保真度处理，但同样不带可搜索文字）。Compactum 不输出"既小又可搜索"的 PDF。

**能商用吗？**
不能。本项目使用 PolyForm Noncommercial 1.0.0 许可。商业使用请通过 GitHub 联系作者。

---

## Project layout

```text
compactum/
├── src/compactum/
│   ├── core.py             Size-bounded compressor for PDFs and images.
│   ├── gui.py              pywebview backend / JS bridge.
│   ├── cli.py              CLI entry points.
│   └── webui/              Bilingual HTML / CSS / JS frontend.
│       ├── index.html
│       ├── style.css
│       ├── app.js
│       ├── donate/         QR codes for donations.
│       └── fonts/          Marianne (Etalab Open License).
├── build/
│   ├── compactum.spec      PyInstaller spec.
│   ├── icon.icns           macOS icon.
│   ├── icon.ico            Windows icon.
│   └── icon.png            Linux icon.
├── .github/workflows/
│   └── release.yml         Build pipeline for v* tags.
├── assets/
│   ├── logo.svg
│   └── wordmark.svg
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## License · 许可

[PolyForm Noncommercial License 1.0.0](LICENSE).

Free for personal, educational, research, governmental, charitable, and other non-commercial use. Commercial use is not permitted. For commercial licensing, contact the author via GitHub.

允许个人、教育、研究、政府、公益等非商业用途使用，禁止商业使用。商业授权请通过 GitHub 联系作者。

Copyright (c) 2026 ViveSieg. All rights reserved.

---

## Credits

- PDF rendering: [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
- Image encoding: [Pillow](https://python-pillow.org/)
- Desktop wrapper: [pywebview](https://pywebview.flowrl.com/)
- Marianne font © Etalab — [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)
