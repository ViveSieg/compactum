/* Compactum — frontend
 * Talks to Python backend via window.pywebview.api.{pickFiles,run,openFolder,openExternal,resolveDropped}
 */

(() => {

const $ = (id) => document.getElementById(id);

const DEFAULT_SCALE = 2.0;
const LANG_KEY = "compactum.lang";

const I18N = {
  en: {
    brand_tagline: "Offline · Free · Non-commercial",
    step1: "🎯 Output type",
    step2: "📥 Drop your file",
    step3: "📦 Target size",
    mode_jpg_title: "PDF → Images",
    mode_jpg_hint: "One JPG per page, each ≤ target.",
    mode_pdf_title: "PDF → Smaller PDF",
    mode_pdf_hint: "Single rebuilt PDF ≤ target.",
    mode_image_title: "Image → Smaller JPG",
    mode_image_hint: "JPG / PNG / WebP / … shrunk to target.",
    mode_jpg_short: "PDF → JPG",
    mode_pdf_short: "PDF → PDF",
    mode_image_short: "IMG → JPG",
    drop_unsupported: "Couldn't accept the dropped files. Please use Browse files instead.",
    drop_title: "📥 Drop a PDF or image here",
    drop_title_pdf: "📥 Drop a PDF here",
    drop_title_image: "📥 Drop an image here",
    drop_or: "or",
    drop_browse: "Browse files",
    drop_hint: "PDF · JPG · PNG · WebP · BMP · TIFF · GIF · stays local",
    drop_hint_pdf: "PDF · stays local",
    drop_hint_image: "JPG · PNG · WebP · BMP · TIFF · GIF · stays local",
    clear_files: "Clear files",
    custom_label: "Or enter a custom size (KB)",
    custom_placeholder: "e.g. 350",
    skip_title: "Skip size limit (native quality)",
    skip_hint: "Original quality, no size cap.",
    advanced: "Advanced",
    scale_label: "Render scale · PDF only · default 2.0×",
    scale_low: "1× soft",
    scale_high: "3× sharp",
    scale_hint: "Higher = sharper, larger starting size. The size cap is still enforced.",
    reset: "Reset",
    btn_start: "Start",
    btn_running: "Working…",
    actions_hint: "Output saved next to the original file.",
    processing: "Processing…",
    done: "✅ Done",
    done_warning: "Done · target not reached",
    cap_exceeded_msg: "Output is at the minimum feasible size. Try a larger target.",
    open_folder: "Open output folder",
    another: "Process another",
    error_title: "⚠️ Something went wrong",
    eff_scale: "Render scale",
    eff_quality: "JPEG q",
    pages: "pages",
    footer_desc: "100% offline · non-commercial · files stay local",
    support_author: "Support the author ☕",
    report_bug: "Report a bug",
    donate_title: "Buy me a coffee ☕",
    donate_intro: "Free for non-commercial use. Tips appreciated, never required.",
    alipay: "Alipay",
    wechat: "WeChat Pay",
    wise: "Wise (intl.)",
    thanks: "Thank you!",
    backend_not_ready: "App is still loading. Try again in a moment.",
  },
  zh: {
    brand_tagline: "完全离线 · 免费 · 仅限非商用",
    step1: "🎯 输出类型",
    step2: "📥 拖入文件",
    step3: "📦 目标大小",
    mode_jpg_title: "PDF → 图片",
    mode_jpg_hint: "每页一张 JPG，单张 ≤ 目标",
    mode_pdf_title: "PDF → 压缩 PDF",
    mode_pdf_hint: "整份 PDF 重建，整体 ≤ 目标",
    mode_image_title: "图片 → 压缩 JPG",
    mode_image_hint: "JPG / PNG / WebP / … 压到目标大小",
    mode_jpg_short: "PDF → JPG",
    mode_pdf_short: "PDF → PDF",
    mode_image_short: "图片 → JPG",
    drop_unsupported: "无法接受拖入的文件，请用「浏览文件」。",
    drop_title: "📥 拖入 PDF 或图片",
    drop_title_pdf: "📥 把 PDF 拖到这里",
    drop_title_image: "📥 把图片拖到这里",
    drop_or: "或者",
    drop_browse: "浏览文件",
    drop_hint: "PDF · JPG · PNG · WebP · BMP · TIFF · GIF · 不会上传",
    drop_hint_pdf: "PDF · 不会上传",
    drop_hint_image: "JPG · PNG · WebP · BMP · TIFF · GIF · 不会上传",
    clear_files: "清除文件",
    custom_label: "或输入自定义大小（KB）",
    custom_placeholder: "例如 350",
    skip_title: "不压缩，保留原始画质",
    skip_hint: "原画质输出，不限制大小",
    advanced: "高级选项",
    scale_label: "渲染倍率 · 仅 PDF · 默认 2.0×",
    scale_low: "1× 模糊",
    scale_high: "3× 清晰",
    scale_hint: "越大越清晰、起点越大；目标 KB 上限仍会硬命中",
    reset: "恢复默认",
    btn_start: "开始",
    btn_running: "处理中…",
    actions_hint: "输出保存在原文件旁边",
    processing: "处理中…",
    done: "✅ 完成",
    done_warning: "完成 · 未达到目标大小",
    cap_exceeded_msg: "已是最小可行尺寸，请改大目标。",
    open_folder: "打开输出位置",
    another: "再处理一个",
    error_title: "⚠️ 出错了",
    eff_scale: "实际倍率",
    eff_quality: "JPEG 质量",
    pages: "页",
    footer_desc: "100% 离线 · 非商用 · 文件不上传",
    support_author: "支持作者 ☕",
    report_bug: "反馈问题",
    donate_title: "请作者喝杯咖啡 ☕",
    donate_intro: "非商用免费。打赏完全自愿，不强制。",
    alipay: "支付宝",
    wechat: "微信支付",
    wise: "Wise（境外）",
    thanks: "谢谢！",
    backend_not_ready: "应用还在启动，请稍候。",
  },
};

const state = {
  files: [],
  mode: "jpg",
  kb: 500,
  scale: DEFAULT_SCALE,
  compress: true,
  busy: false,
  lang: "en",
};

/* ---------- i18n ---------- */

function applyI18n(lang) {
  const dict = I18N[lang] || I18N.en;
  state.lang = lang;
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] != null) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key] != null) el.setAttribute("placeholder", dict[key]);
  });

  document.querySelectorAll(".fr-lang-btn").forEach((b) => {
    b.classList.toggle("is-active", b.dataset.lang === lang);
  });

  applyDropText();
  applyModeHint();
  renderFiles();
}

function t(key) {
  return (I18N[state.lang] && I18N[state.lang][key]) || I18N.en[key] || key;
}

document.querySelectorAll(".fr-lang-btn").forEach((b) => {
  b.addEventListener("click", () => {
    const lang = b.dataset.lang;
    try { localStorage.setItem(LANG_KEY, lang); } catch {}
    applyI18n(lang);
  });
});

(function initLang() {
  let saved = null;
  try { saved = localStorage.getItem(LANG_KEY); } catch {}
  if (saved && I18N[saved]) {
    applyI18n(saved);
  } else if ((navigator.language || "").toLowerCase().startsWith("zh")) {
    applyI18n("zh");
  } else {
    applyI18n("en");
  }
})();

/* ---------- pywebview bridge ---------- */

function api() {
  if (!window.pywebview || !window.pywebview.api) {
    throw new Error(t("backend_not_ready"));
  }
  return window.pywebview.api;
}

/* ---------- mode radios ---------- */

document.querySelectorAll('input[name="mode"]').forEach((el) => {
  el.addEventListener("change", () => {
    if (el.checked) setMode(el.value);
  });
});

/* ---------- size presets ---------- */

document.querySelectorAll(".fr-preset").forEach((el) => {
  el.addEventListener("click", () => {
    document.querySelectorAll(".fr-preset").forEach((b) => b.classList.remove("is-active"));
    el.classList.add("is-active");
    state.kb = parseInt(el.dataset.kb, 10);
    $("customKb").value = "";
  });
});

$("customKb").addEventListener("input", () => {
  const v = parseInt($("customKb").value, 10);
  if (!isNaN(v) && v >= 20) {
    document.querySelectorAll(".fr-preset").forEach((b) => b.classList.remove("is-active"));
    state.kb = v;
  }
});

/* ---------- skip-limit (no-compression) checkbox ---------- */

const skipLimit = $("skipLimit");
const sizeGroup = $("sizeGroup");
skipLimit.addEventListener("change", () => {
  state.compress = !skipLimit.checked;
  sizeGroup.classList.toggle("is-disabled", skipLimit.checked);
});

/* ---------- render scale slider ---------- */

const scaleRange = $("scaleRange");
const scaleVal = $("scaleVal");
function updateScaleVal() {
  const v = parseFloat(scaleRange.value);
  state.scale = v;
  scaleVal.textContent = `${v.toFixed(1)}×`;
}
scaleRange.addEventListener("input", updateScaleVal);
$("resetScale").addEventListener("click", () => {
  scaleRange.value = String(DEFAULT_SCALE);
  updateScaleVal();
});
updateScaleVal();

/* ---------- file picker / drop ---------- */

$("pickBtn").addEventListener("click", async () => {
  try {
    const picked = await api().pickFiles();
    if (picked && picked.length) addFiles(picked);
  } catch (e) {
    showError(String(e.message || e));
  }
});

$("filePicker").addEventListener("change", () => {
  // pywebview blocks <input type="file"> from working in some webviews.
  // We rely on api().pickFiles() instead. Kept for safety.
});

$("clearBtn").addEventListener("click", () => {
  state.files = [];
  renderFiles();
  applyModeAvailability();
});

const drop = $("drop");
drop.addEventListener("dragover", (e) => {
  e.preventDefault();
  drop.classList.add("is-dragging");
});
drop.addEventListener("dragleave", (e) => {
  if (e.target === drop) drop.classList.remove("is-dragging");
});
drop.addEventListener("drop", async (e) => {
  e.preventDefault();
  drop.classList.remove("is-dragging");

  const files = Array.from(e.dataTransfer.files || []);
  if (files.length === 0) return;

  // Layer 1 — Chromium-based webviews (Win EdgeChromium, some Linux
  // GTK builds) expose f.path directly. Use the real OS path; output
  // lands next to the original file.
  const paths = files.filter((f) => f.path).map((f) => f.path);
  if (paths.length === files.length && paths.length > 0) {
    try {
      const resolved = await api().resolveDropped(paths);
      if (resolved && resolved.length) addFiles(resolved);
    } catch (err) { showError(String(err.message || err)); }
    return;
  }

  // Layer 2 — macOS WKWebView and any backend that strips f.path. Read
  // bytes via FileReader, then the backend asks once where to save (a
  // native folder picker), and the user-chosen folder becomes the
  // working directory for both inputs and outputs of this session.
  try {
    const items = await Promise.all(files.map(async (f) => ({
      name: f.name,
      b64: await readAsBase64(f),
    })));
    const res = await api().saveDroppedToFolder(items);
    if (res && Array.isArray(res.files) && res.files.length) {
      addFiles(res.files);
    } else if (res && res.cancelled) {
      // user dismissed the folder picker — quietly ignore
    } else {
      showError(t("drop_unsupported"));
    }
  } catch (err) {
    showError(String(err.message || err));
  }
});

function readAsBase64(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      const v = r.result || "";
      const c = v.indexOf(",");
      resolve(c >= 0 ? v.slice(c + 1) : v);
    };
    r.onerror = () => reject(r.error);
    r.readAsDataURL(file);
  });
}

function addFiles(picked) {
  const known = new Set(state.files.map((f) => f.path));
  for (const f of picked) {
    if (!known.has(f.path)) state.files.push(f);
  }
  renderFiles();
  autoSelectMode();
}

const IMAGE_EXT = /\.(jpg|jpeg|png|webp|bmp|tif|tiff|gif|heic|heif)$/i;
const PDF_EXT = /\.pdf$/i;

function autoSelectMode() {
  if (state.files.length === 0) return;
  const allImages = state.files.every((f) => IMAGE_EXT.test(f.name));
  const anyPdf = state.files.some((f) => PDF_EXT.test(f.name));
  if (allImages && state.mode !== "image") setMode("image");
  else if (anyPdf && state.mode === "image") setMode("jpg");
  applyModeAvailability();
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll('input[name="mode"]').forEach((el) => {
    el.checked = el.value === mode;
  });
  applyDropText();
  applyAdvancedVisibility();
  applyModeHint();
}

function applyModeHint() {
  const el = document.getElementById("modeHint");
  if (!el) return;
  const key = state.mode === "image" ? "mode_image_hint"
            : state.mode === "pdf"   ? "mode_pdf_hint"
            : "mode_jpg_hint";
  el.textContent = t(key);
}

function applyDropText() {
  const dict = I18N[state.lang] || I18N.en;
  const titleEl = document.querySelector('.fr-drop-title');
  const hintEl = document.querySelector('.fr-drop-hint');
  if (state.mode === "image") {
    if (titleEl) titleEl.textContent = dict.drop_title_image;
    if (hintEl) hintEl.textContent = dict.drop_hint_image;
  } else if (state.mode === "jpg" || state.mode === "pdf") {
    if (titleEl) titleEl.textContent = dict.drop_title_pdf;
    if (hintEl) hintEl.textContent = dict.drop_hint_pdf;
  } else {
    if (titleEl) titleEl.textContent = dict.drop_title;
    if (hintEl) hintEl.textContent = dict.drop_hint;
  }
}

function applyAdvancedVisibility() {
  const adv = document.querySelector('.fr-advanced');
  if (!adv) return;
  adv.hidden = (state.mode === "image");
}

function applyModeAvailability() {
  const sel = ".fr-seg-mode[data-mode], .fr-radio[data-mode]";
  if (state.files.length === 0) {
    document.querySelectorAll(sel).forEach((el) => el.classList.remove("is-disabled"));
    return;
  }
  const allImages = state.files.every((f) => IMAGE_EXT.test(f.name));
  const allPdfs = state.files.every((f) => PDF_EXT.test(f.name));
  document.querySelectorAll(sel).forEach((el) => {
    const m = el.dataset.mode;
    const ok = (m === "image" && allImages) || (m !== "image" && allPdfs) || (!allImages && !allPdfs);
    el.classList.toggle("is-disabled", !ok);
    const input = el.querySelector("input");
    if (input) input.disabled = !ok;
  });
}

function renderFiles() {
  const list = $("fileList");
  list.innerHTML = "";
  if (state.files.length === 0) {
    $("dropIdle").hidden = false;
    $("dropActive").hidden = true;
    $("runBtn").disabled = true;
    return;
  }
  $("dropIdle").hidden = true;
  $("dropActive").hidden = false;
  $("runBtn").disabled = state.busy;

  for (const f of state.files) {
    const li = document.createElement("li");
    li.className = "fr-file-item";
    const name = document.createElement("div");
    name.className = "fr-file-item-name";
    name.textContent = f.name;
    const meta = document.createElement("div");
    meta.className = "fr-file-item-meta";
    meta.textContent = humanBytes(f.size);
    li.append(name, meta);
    list.append(li);
  }
}

function humanBytes(n) {
  if (n == null) return "—";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

/* ---------- run ---------- */

$("runBtn").addEventListener("click", async () => {
  if (state.busy || state.files.length === 0) return;
  state.busy = true;
  $("runBtn").disabled = true;
  $("runBtn").textContent = t("btn_running");
  $("result").hidden = true;
  $("errorBox").hidden = true;
  $("progress").hidden = false;
  $("progressTitle").textContent = t("processing");
  $("progressText").textContent = "—";
  $("progressFill").style.width = "0%";

  try {
    const job = {
      mode: state.mode,
      kb: state.kb,
      scale: state.scale,
      compress: state.compress,
      paths: state.files.map((f) => f.path),
    };
    const result = await api().run(job);
    showResult(result);
  } catch (err) {
    showError(String(err.message || err));
  } finally {
    state.busy = false;
    $("progress").hidden = true;
    $("runBtn").textContent = t("btn_start");
    $("runBtn").disabled = state.files.length === 0;
  }
});

window.shrinkProgress = (info) => {
  if (!info) return;
  if (info.msg) $("progressTitle").textContent = info.msg;
  if (typeof info.percent === "number") $("progressFill").style.width = `${info.percent}%`;
  if (info.file) {
    const fileTxt = (info.total_files && info.total_files > 1)
      ? `[${info.file_idx}/${info.total_files}] ${info.file}`
      : info.file;
    const pageTxt = info.page != null ? ` · ${info.page}/${info.total}` : "";
    $("progressText").textContent = `${fileTxt}${pageTxt}`;
  }
};

function showResult(result) {
  const resultEl = $("result");
  resultEl.hidden = false;

  const stats = (result && result.stats) || [];
  const anyExceeded = stats.some((s) => s && s.cap_exceeded);

  resultEl.classList.toggle("fr-alert-success", !anyExceeded);
  resultEl.classList.toggle("fr-alert-warning", anyExceeded);
  $("resultTitle").textContent = anyExceeded ? t("done_warning") : t("done");

  const warnEl = $("resultWarning");
  warnEl.hidden = !anyExceeded;
  if (anyExceeded) warnEl.textContent = t("cap_exceeded_msg");

  const outputs = (result && result.outputs) || [];
  const list = $("resultList");
  list.innerHTML = "";
  outputs.forEach((path, i) => list.appendChild(buildResultItem(path, stats[i])));

  if (outputs.length) $("openFolderBtn").dataset.path = outputs[0];

  fireConfetti();
  maybeShowFirstSuccessDonate();
}

document.getElementById("resultClose").addEventListener("click", () => {
  document.getElementById("result").hidden = true;
});
document.getElementById("errorClose").addEventListener("click", () => {
  document.getElementById("errorBox").hidden = true;
});

function basename(path) {
  if (!path) return "";
  const m = String(path).match(/[^/\\]+[/\\]?$/);
  return m ? m[0].replace(/[/\\]$/, "") : String(path);
}

function buildResultItem(outputPath, stat) {
  const li = document.createElement("li");
  li.className = "fr-result-item";

  const name = document.createElement("div");
  name.className = "fr-result-name";
  name.textContent = basename(outputPath);
  li.appendChild(name);

  if (stat) {
    const meta = document.createElement("div");
    meta.className = "fr-result-meta";
    const parts = [];
    if (stat.input_size && stat.output_size) {
      const inSize = humanBytes(stat.input_size);
      const outSize = humanBytes(stat.output_size);
      const ratio = stat.input_size > 0
        ? Math.round((1 - stat.output_size / stat.input_size) * 100)
        : 0;
      parts.push(ratio > 0 ? `${inSize} → ${outSize} (-${ratio}%)` : `${inSize} → ${outSize}`);
    }
    if (stat.mode === "jpg" && stat.page_count != null) {
      parts.push(`${stat.page_count} ${t("pages")}`);
    } else if (stat.mode === "pdf" && stat.effective_scale != null) {
      parts.push(`${t("eff_scale")} ${Number(stat.effective_scale).toFixed(2)}×`);
      if (stat.quality) parts.push(`${t("eff_quality")} ${stat.quality}`);
    }
    meta.textContent = parts.join(" · ");
    li.appendChild(meta);
  }
  return li;
}

/* ---------- success animations ---------- */

const CONFETTI_COLORS = ["#000091", "#1212ff", "#e1000f", "#18753c", "#c8aa39", "#a558a0"];
function fireConfetti() {
  const layer = document.createElement("div");
  layer.className = "fr-confetti";
  document.body.appendChild(layer);
  const N = 60;
  for (let i = 0; i < N; i++) {
    const piece = document.createElement("span");
    const left = Math.random() * 100;
    const dx = (Math.random() - 0.5) * 240;
    const rot = (Math.random() * 720 + 360) * (Math.random() < 0.5 ? -1 : 1);
    const delay = Math.random() * 250;
    const dur = 1400 + Math.random() * 700;
    piece.style.left = left + "vw";
    piece.style.background = CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)];
    piece.style.setProperty("--dx", dx + "px");
    piece.style.setProperty("--rot", rot + "deg");
    piece.style.animationDelay = delay + "ms";
    piece.style.animationDuration = dur + "ms";
    layer.appendChild(piece);
  }
  setTimeout(() => layer.remove(), 2400);
}

const DONATE_COUNT_KEY = "compactum.successCount";
const DONATE_MILESTONES = new Set([1, 10, 20]);
function maybeShowFirstSuccessDonate() {
  let n = 0;
  try { n = parseInt(localStorage.getItem(DONATE_COUNT_KEY) || "0", 10) || 0; } catch {}
  n += 1;
  try { localStorage.setItem(DONATE_COUNT_KEY, String(n)); } catch {}
  if (DONATE_MILESTONES.has(n)) setTimeout(openDonate, 900);
}

function showError(msg) {
  $("errorBox").hidden = false;
  $("errorText").textContent = msg;
}

$("openFolderBtn").addEventListener("click", async () => {
  const p = $("openFolderBtn").dataset.path;
  if (!p) return;
  try { await api().openFolder(p); } catch (e) { showError(String(e.message || e)); }
});

$("resetBtn").addEventListener("click", () => {
  state.files = [];
  $("result").hidden = true;
  $("errorBox").hidden = true;
  renderFiles();
});

/* ---------- donate modal ---------- */

const donateModal = $("donateModal");
function openDonate() { donateModal.hidden = false; }
function closeDonate() { donateModal.hidden = true; }
$("donateBtn").addEventListener("click", openDonate);
$("closeDonate").addEventListener("click", closeDonate);
donateModal.querySelector('[data-close="donate"]').addEventListener("click", closeDonate);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !donateModal.hidden) closeDonate();
});

/* ---------- external links via OS browser ---------- */

document.querySelectorAll('a[target="_blank"]').forEach((a) => {
  a.addEventListener("click", async (e) => {
    if (!window.pywebview || !window.pywebview.api) return;
    e.preventDefault();
    try { await api().openExternal(a.href); } catch {}
  });
});

})();
