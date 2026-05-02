/* Compactum — frontend
 * Talks to Python backend via window.pywebview.api.{pickFiles,run,openFolder,openExternal,resolveDropped}
 */

(() => {

const $ = (id) => document.getElementById(id);

const DEFAULT_SCALE = 1.5;
const LANG_KEY = "compactum.lang";

const I18N = {
  en: {
    brand_tagline: "Offline · Free · Non-commercial",
    step1: "Pick output",
    step2: "Drop your PDF",
    step3: "Target size",
    mode_jpg_title: "PDF → Images",
    mode_jpg_hint: "One JPG per page. Each ≤ target size.",
    mode_pdf_title: "PDF → Smaller PDF",
    mode_pdf_hint: "Whole PDF rebuilt ≤ target size.",
    drop_title: "Drop a PDF here",
    drop_or: "or",
    drop_browse: "Browse files",
    drop_hint: "Single or multiple PDFs · Stays on your computer",
    clear_files: "Clear files",
    custom_label: "Or enter a custom size (KB)",
    custom_placeholder: "e.g. 350",
    skip_title: "Skip size limit (native quality)",
    skip_hint: "Output at original render quality, no size cap. Use when you only need to convert.",
    advanced: "Advanced",
    scale_label: "Render scale (default 1.5×)",
    scale_low: "1× soft",
    scale_high: "3× sharp",
    scale_hint: "Higher = sharper image, larger starting size before compression. The size limit is still hard-enforced regardless of this value.",
    reset: "Reset",
    btn_start: "Start",
    btn_running: "Working…",
    actions_hint: "Output is saved next to the original PDF.",
    processing: "Processing…",
    done: "Done",
    open_folder: "Open output folder",
    another: "Process another",
    error_title: "Something went wrong",
    eff_scale: "Render scale",
    eff_quality: "JPEG q",
    pages: "pages",
    footer_desc: "100% offline · Non-commercial use · Files never leave your machine",
    support_author: "Support the author",
    report_bug: "Report a bug",
    donate_title: "Buy me a coffee",
    donate_intro: "This tool is free for non-commercial use. If it saved you some pain, a small tip is appreciated — but never required.",
    alipay: "Alipay",
    wechat: "WeChat Pay",
    wise: "Wise (intl.)",
    thanks: "Thank you!",
    backend_not_ready: "App is still loading — please try again in a moment.",
  },
  zh: {
    brand_tagline: "完全离线 · 免费 · 仅限非商用",
    step1: "选择输出方式",
    step2: "拖入 PDF",
    step3: "目标大小",
    mode_jpg_title: "PDF → 图片",
    mode_jpg_hint: "每页一张 JPG，每张 ≤ 目标大小",
    mode_pdf_title: "PDF → 压缩 PDF",
    mode_pdf_hint: "整份 PDF 重建为图片版，整体 ≤ 目标大小",
    drop_title: "把 PDF 拖到这里",
    drop_or: "或者",
    drop_browse: "浏览文件",
    drop_hint: "支持单个或多个 PDF · 文件不会离开你的电脑",
    clear_files: "清除文件",
    custom_label: "或输入自定义大小（KB）",
    custom_placeholder: "例如 350",
    skip_title: "不压缩，保留原始画质",
    skip_hint: "按原渲染画质输出，不限制文件大小。仅当你只需要格式转换时使用。",
    advanced: "高级选项",
    scale_label: "渲染倍率（默认 1.5×）",
    scale_low: "1× 模糊",
    scale_high: "3× 清晰",
    scale_hint: "数值越大越清晰、压缩前的起点文件越大；目标 KB 上限仍然会强制硬命中。",
    reset: "恢复默认",
    btn_start: "开始",
    btn_running: "处理中…",
    actions_hint: "输出会自动保存在原 PDF 旁边。",
    processing: "处理中…",
    done: "完成",
    open_folder: "打开输出位置",
    another: "再处理一个",
    error_title: "出错了",
    eff_scale: "实际倍率",
    eff_quality: "JPEG 质量",
    pages: "页",
    footer_desc: "100% 离线 · 仅限非商用 · 文件不会上传任何服务器",
    support_author: "支持作者",
    report_bug: "反馈问题",
    donate_title: "请作者喝杯咖啡",
    donate_intro: "本工具非商用免费。如果对你有帮助，欢迎随心打赏 —— 完全自愿。",
    alipay: "支付宝",
    wechat: "微信支付",
    wise: "Wise（境外）",
    thanks: "谢谢！",
    backend_not_ready: "应用还在启动，稍等一下再试。",
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

  // re-render the file list since the empty/disabled states use translated text
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
    if (el.checked) state.mode = el.value;
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

  const paths = [];
  for (const f of e.dataTransfer.files) {
    if (f.path) paths.push(f.path);
  }
  if (paths.length === 0) {
    // Some webviews don't expose a real path on drop. Ask user to use the picker.
    showError(t("backend_not_ready"));
    return;
  }
  try {
    const resolved = await api().resolveDropped(paths);
    if (resolved && resolved.length) addFiles(resolved);
  } catch (err) {
    showError(String(err.message || err));
  }
});

function addFiles(picked) {
  const known = new Set(state.files.map((f) => f.path));
  for (const f of picked) {
    if (!known.has(f.path)) state.files.push(f);
  }
  renderFiles();
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
    const pageTxt = info.page != null ? ` · ${info.page}/${info.total}` : "";
    $("progressText").textContent = `${info.file}${pageTxt}`;
  }
};

function showResult(result) {
  $("result").hidden = false;
  if (result && result.outputs && result.outputs.length) {
    const lines = result.outputs.map((o, i) => formatStatLine(o, (result.stats || [])[i])).join("\n");
    $("resultPath").textContent = lines;
    $("openFolderBtn").dataset.path = result.outputs[0];
  } else {
    $("resultPath").textContent = "—";
  }
  fireConfetti();
  maybeShowFirstSuccessDonate();
}

function formatStatLine(outputPath, stat) {
  if (!stat) return outputPath;
  const inSize = humanBytes(stat.input_size);
  const outSize = humanBytes(stat.output_size);
  const ratio = stat.input_size > 0
    ? Math.round((1 - stat.output_size / stat.input_size) * 100)
    : 0;
  const ratioTxt = ratio > 0 ? ` (-${ratio}%)` : "";

  let extra = "";
  if (stat.mode === "pdf" && stat.effective_scale != null) {
    const eff = Number(stat.effective_scale).toFixed(2);
    const inp = Number(stat.input_scale).toFixed(2);
    extra = `   ${t("eff_scale")}: ${inp}× → ${eff}×`;
    if (stat.quality) extra += `   ${t("eff_quality")}: q=${stat.quality}`;
  } else if (stat.mode === "jpg" && stat.page_count != null) {
    extra = `   ${stat.page_count} ${t("pages")}`;
  }
  return `${outputPath}\n   ${inSize} → ${outSize}${ratioTxt}${extra}`;
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

const DONATE_SHOWN_KEY = "compactum.firstSuccessShown";
function maybeShowFirstSuccessDonate() {
  let shown = null;
  try { shown = localStorage.getItem(DONATE_SHOWN_KEY); } catch {}
  if (shown) return;
  setTimeout(() => {
    openDonate();
    try { localStorage.setItem(DONATE_SHOWN_KEY, "1"); } catch {}
  }, 900);
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
