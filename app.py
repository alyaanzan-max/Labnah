# -*- coding: utf-8 -*-
"""
لَبنَة — منصة تنفيذ وقياس جاهزية للمشاريع التقنية
=====================================================
تطبيق Streamlit مبني على «التقرير الاستراتيجي المتكامل لمنصة لَبنَة».

الأقسام الأربعة الأساسية (القسم 6 من التقرير):
    مساري  |  المشاريع  |  المسح  |  جواز لَبنَة

الأوضاع الخاصة (لا تظهر كأقسام دائمة):
    وضع المنظم   → غرفة الهاكثون + مؤشرات القياس + مراجعة الأدلة
    وضع المطوّر  → مختبر التصميم (taste-skill / impeccable / designlang)

التشغيل:
    pip install -r requirements.txt
    streamlit run labna_app.py

متغيرات بيئة اختيارية:
    ANTHROPIC_API_KEY   لتفعيل «فكّك فكرتي» الذكي والتعرف البصري المقترح
    LABNA_MODEL         اسم النموذج (الافتراضي claude-sonnet-5-5)
    LABNA_DATA          مسار ملف الحفظ (الافتراضي ./labna_data/state.json)
"""
from __future__ import annotations

import base64
import html as _html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlparse

import streamlit as st

# ════════════════════════════════════════════════════════════════════════════
# 0) ثوابت عامة
# ════════════════════════════════════════════════════════════════════════════
APP_NAME = "لَبنَة"
DATA_PATH = Path(os.getenv("LABNA_DATA", "./labna_data/state.json"))
MODEL = os.getenv("LABNA_MODEL", "claude-sonnet-5-5")

NAV = ["مساري", "المشاريع", "المسح", "جواز لَبنَة"]

# مستويات الدليل (القسم 7.5)
LEVELS = ["لم تبدأ", "أكملتها", "تحققت", "راجعتها"]
LEVEL_ICON = ["○", "◐", "✓", "✓✓"]

# أنواع نقاط الشجاعة (القسم 10)
COURAGE = {
    "start": "شجاعة البداية",
    "try": "شجاعة التجربة",
    "fix": "شجاعة الإصلاح",
}

# المهارات الممارسة (القسم 1 — «جمع متطلبات، توصيل حساس، اختبار نظام …»)
SKILLS = [
    "جمع متطلبات",
    "توصيل حساس",
    "اختبار نظام",
    "تحليل بيانات",
    "بناء نموذج أولي",
    "شرح قرار تقني",
]

# مراجع التقرير (القسم 2)
REFERENCES = {
    "رؤية السعودية 2030 — نظرة عامة": "https://www.vision2030.gov.sa/en/overview",
    "برنامج تنمية القدرات البشرية": "https://www.vision2030.gov.sa/en/explore/programs/human-capability-development-program",
    "إطار المهارات الرقمية — وزارة الاتصالات وتقنية المعلومات": "https://futureskills.mcit.gov.sa/en/skills-framework",
    "مبادرات الهيئة السعودية للبيانات والذكاء الاصطناعي": "https://sdaia.gov.sa/en/MediaCenter/Initiatives/Pages/default.aspx",
}

# المسارات السعودية المقترحة (القسم 14) — سياقات تعليمية، دون نسبتها لجهة بعينها
LOCAL_TRACKS = {
    "مدن أذكى": "جمع بيانات بيئية أو حضرية وعرضها وصياغة تدخل صغير، مع التفكير في جودة البيانات وخصوصية الأفراد.",
    "صحراء وموارد": "الماء والطاقة والحرارة والزراعة في البيئات القاسية: القياس والمعايرة وحدود الاستنتاج.",
    "بيانات عربية مفهومة": "تنظيف بيانات عامة أو مصطنعة وعرضها وشرحها بعربية واضحة.",
    "ذكاء اصطناعي مسؤول": "نموذج تصنيف بسيط مع اختبار الانحياز والتمييز بين التنبؤ والقرار.",
    "حلول الإتاحة": "أدوات وواجهات تراعي كبار السن والأشخاص ذوي الإعاقة.",
    "تراث وثقافة": "توثيق قصة أو صوت أو مكان أو حرفة بالتقنية مع احترام الخصوصية والحقوق.",
}


# ════════════════════════════════════════════════════════════════════════════
# 1) نظام التصميم  (مبني على مبادئ taste-skill + impeccable + designlang)
# ════════════════════════════════════════════════════════════════════════════
# taste-skill: نظام واحد متسق، «تُوزَّع» الألوان والخطوط حسب نوع المنتج، حواف متساوية،
#              لا قوالب «ذكاء اصطناعي» عامة، حركة قليلة ومقصودة.
# impeccable : مفردات تصميم + كاشف «slop» (62 قاعدة) + مراجعة وصول/تباين.
# designlang : استخراج رموز التصميم (DTCG) من موقع حي وتطبيقها بعد فحص WCAG.

TYPE_PAIR = {
    "display": "Reem Kufi",
    "body": "IBM Plex Sans Arabic",
    "mono": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
    "google": (
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600"
        "&family=Reem+Kufi:wght@500;700&display=swap"
    ),
}

# «مكتبة الألوان» — palettes يُختار منها لكل نوع منتج (على غرار library/palettes.json)
PALETTES: dict[str, dict[str, dict[str, str]]] = {
    "حجر": {  # الافتراضي: بارد هادئ، أخضر وظيفي للتقدم
        "light": dict(bg="#F4F6F3", surface="#FFFFFF", ink="#17232B", muted="#4F5E66",
                      primary="#0E6B5C", on_primary="#FFFFFF", accent="#8F5A00",
                      warn="#A93A24", ok="#14693F", line="#D5DBD3", soft="#E6EEEA"),
        "dark": dict(bg="#12191E", surface="#1A242B", ink="#E8EEF0", muted="#9AA9B0",
                     primary="#4FC3AA", on_primary="#08201B", accent="#E0A63A",
                     warn="#F08A74", ok="#6FD39B", line="#2C3A42", soft="#1F2D33"),
    },
    "واحة": {
        "light": dict(bg="#F3F6EE", surface="#FFFFFF", ink="#1B2A1E", muted="#4F5F52",
                      primary="#2F6B2A", on_primary="#FFFFFF", accent="#8A5A00",
                      warn="#A63A2A", ok="#1E6B3A", line="#D3DBCB", soft="#E5EEDD"),
        "dark": dict(bg="#101712", surface="#18221A", ink="#E6EFE6", muted="#9DB09F",
                     primary="#7FD07A", on_primary="#0A1D0B", accent="#E0B04A",
                     warn="#F09080", ok="#7FD79F", line="#2A3A2C", soft="#1D2B20"),
    },
    "حبر": {
        "light": dict(bg="#F4F5F8", surface="#FFFFFF", ink="#171B2B", muted="#505768",
                      primary="#2F4BA8", on_primary="#FFFFFF", accent="#8A5600",
                      warn="#A63A33", ok="#17693F", line="#D6D9E3", soft="#E6E9F4"),
        "dark": dict(bg="#11141F", surface="#191D2B", ink="#E8EAF2", muted="#9AA1B8",
                     primary="#8EA6F2", on_primary="#0C1330", accent="#E0A63A",
                     warn="#F08A80", ok="#6FD39B", line="#2B3042", soft="#1E2336"),
    },
}

RADII = {"sm": "6px", "md": "10px", "lg": "14px"}  # ثلاث درجات فقط (لا نصف قطر واحد للكل)

CSS_TEMPLATE = Template(r"""
@import url('$google');
:root{
  --bg:$bg; --surface:$surface; --ink:$ink; --muted:$muted;
  --primary:$primary; --on-primary:$on_primary; --accent:$accent;
  --warn:$warn; --ok:$ok; --line:$line; --soft:$soft;
  --r-sm:$r_sm; --r-md:$r_md; --r-lg:$r_lg;
  --font-body:'$body', system-ui, sans-serif;
  --font-display:'$display', '$body', system-ui, sans-serif;
  --edge:clamp(16px, 4vw, 48px);
}
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background:var(--bg) !important; color:var(--ink);
  font-family:var(--font-body); direction:rtl;
}
[data-testid="stHeader"]{ background:transparent; }
.block-container{ max-width:1080px; padding:2.2rem var(--edge) 4rem; }
[data-testid="stSidebar"]{ background:var(--surface); border-inline-start:1px solid var(--line); }
h1,h2,h3{ font-family:var(--font-display); color:var(--ink); letter-spacing:0; }
h1{ font-size:2rem; line-height:1.35; font-weight:700; }
h2{ font-size:1.45rem; line-height:1.4; }
h3{ font-size:1.15rem; line-height:1.5; }
p, li, label, .stMarkdown{ line-height:1.9; font-size:1.02rem; }
.stMarkdown p{ max-width:68ch; }
code, pre, .stCode, [data-testid="stCodeBlock"]{ direction:ltr !important; text-align:left !important; font-family:$mono; }
a{ color:var(--primary); }

/* بطاقات: ثلاث درجات استدارة بحسب الأهمية، بلا ظلال زخرفية */
.lb-card{ background:var(--surface); border:1px solid var(--line); border-radius:var(--r-md);
          padding:1.1rem 1.25rem; margin:0 0 1rem; }
.lb-card.primary{ border-color:var(--primary); border-width:2px; border-radius:var(--r-lg); }
.lb-card h3{ margin:.1rem 0 .4rem; }
.lb-muted{ color:var(--muted); }
.lb-row{ display:flex; gap:.6rem; flex-wrap:wrap; align-items:center; }
.lb-tag{ display:inline-block; padding:.12rem .6rem; border:1px solid var(--line); border-radius:var(--r-sm);
         background:var(--soft); color:var(--ink); font-size:.88rem; }
.lb-tag.ok{ border-color:var(--ok); color:var(--ok); background:transparent; }
.lb-tag.warn{ border-color:var(--warn); color:var(--warn); background:transparent; }
.lb-tag.acc{ border-color:var(--accent); color:var(--accent); background:transparent; }

/* تحذير السلامة: يبقى ظاهرًا دائمًا (القسم 5) — الأيقونة + النص، لا اللون وحده */
.lb-safety{ border:2px solid var(--warn); border-radius:var(--r-md); padding:.8rem 1rem; margin:.6rem 0 1rem;
            background:var(--surface); }
.lb-safety strong{ color:var(--warn); }

/* شريط اللبنات */
.lb-strip{ display:grid; grid-auto-flow:column; grid-auto-columns:1fr; gap:6px; margin:.4rem 0 1rem; }
.lb-seg{ text-align:center; padding:.45rem 0; border:1px solid var(--line); border-radius:var(--r-sm);
         background:var(--surface); font-size:.9rem; color:var(--muted); }
.lb-seg.s1{ border-color:var(--accent); color:var(--accent); }
.lb-seg.s2{ border-color:var(--ok); color:var(--ok); }
.lb-seg.s3{ background:var(--ok); border-color:var(--ok); color:var(--surface); }
.lb-seg.cur{ outline:2px solid var(--primary); outline-offset:2px; }
.lb-seg.lock{ opacity:.55; }

.lb-big{ font-family:var(--font-display); font-size:1.7rem; line-height:1.5; margin:.2rem 0; }
.lb-result{ border-inline-start:4px solid var(--primary); padding:.2rem 1rem; margin:.6rem 0 1rem; background:var(--soft);
            border-radius:var(--r-sm); }

/* أزرار */
.stButton > button, .stDownloadButton > button, [data-testid^="stBaseButton"]{
  border-radius:var(--r-sm); font-family:var(--font-body); font-weight:500;
  transition:background-color .15s ease, border-color .15s ease;
}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"]{
  background:var(--primary) !important; color:var(--on-primary) !important; border:1px solid var(--primary) !important;
}
.stButton > button[kind="secondary"], [data-testid="stBaseButton-secondary"]{
  background:var(--surface) !important; color:var(--ink) !important; border:1px solid var(--line) !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input, [data-baseweb="select"] > div{
  background:var(--surface) !important; color:var(--ink) !important; border-radius:var(--r-sm) !important;
}
[data-testid="stMetricValue"]{ font-family:var(--font-display); }
[data-testid="stExpander"]{ border:1px solid var(--line); border-radius:var(--r-md); background:var(--surface); }

/* قابلية الوصول: تركيز لوحة المفاتيح ظاهر + احترام تقليل الحركة */
:focus-visible{ outline:3px solid var(--primary); outline-offset:2px; }
@media (prefers-reduced-motion: reduce){ *{ transition:none !important; animation:none !important; } }
@media (max-width:640px){ h1{ font-size:1.6rem; } .block-container{ padding-top:1.2rem; } }
""")


def get_theme_name() -> str:
    return st.session_state.get("db", {}).get("palette", "حجر")


def get_tokens(dark: bool | None = None) -> dict[str, str]:
    db = st.session_state.get("db", {})
    if dark is None:
        dark = bool(db.get("dark_mode", False))
    base = dict(PALETTES.get(get_theme_name(), PALETTES["حجر"])["dark" if dark else "light"])
    override = db.get("theme_override") or {}
    base.update({k: v for k, v in override.items() if k in base and _is_hex(v)})
    return base


def build_css(tokens: dict[str, str]) -> str:
    return CSS_TEMPLATE.safe_substitute(
        google=TYPE_PAIR["google"], body=TYPE_PAIR["body"], display=TYPE_PAIR["display"],
        mono=TYPE_PAIR["mono"], r_sm=RADII["sm"], r_md=RADII["md"], r_lg=RADII["lg"], **tokens,
    )


def inject_css() -> None:
    st.markdown(f"<style>{build_css(get_tokens())}</style>", unsafe_allow_html=True)


# ── أدوات اللون وWCAG (مقابل لفحص WCAG في designlang) ───────────────────────
def _is_hex(v: Any) -> bool:
    return isinstance(v, str) and bool(re.fullmatch(r"#[0-9a-fA-F]{6}", v.strip()))


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg: str, bg: str) -> float:
    a, b = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def token_pairs(t: dict[str, str]) -> list[tuple[str, str, str, float]]:
    pairs = [
        ("النص الأساسي على الخلفية", t["ink"], t["bg"], 4.5),
        ("النص الأساسي على السطح", t["ink"], t["surface"], 4.5),
        ("النص الثانوي على السطح", t["muted"], t["surface"], 4.5),
        ("نص الزر الأساسي", t["on_primary"], t["primary"], 4.5),
        ("لون التقدم على السطح", t["primary"], t["surface"], 3.0),
        ("لون التحذير على السطح", t["warn"], t["surface"], 4.5),
        ("لون نقاط الشجاعة على السطح", t["accent"], t["surface"], 4.5),
        ("لون النجاح على السطح", t["ok"], t["surface"], 4.5),
    ]
    return [(n, f, b, r) for n, f, b, r in pairs]


def local_design_audit(tokens: dict[str, str], css: str) -> list[dict[str, str]]:
    """تدقيق ذاتي سريع بقواعد مستلهمة من taste-skill وimpeccable.
    ليس بديلًا عن كاشف impeccable الأصلي (يعمل من مختبر التصميم عبر Node)."""
    out: list[dict[str, str]] = []

    def add(rule: str, ok: bool, msg: str, sev: str = "FAIL") -> None:
        out.append({"rule": rule, "status": "PASS" if ok else sev, "msg": msg})

    for name, fg, bg, need in token_pairs(tokens):
        r = contrast(fg, bg)
        add("contrast", r >= need, f"{name}: {r:.2f}:1 (المطلوب {need}:1)")
    fams = set(re.findall(r"font-family:\s*([^;]+);", css))
    add("one-system", len({TYPE_PAIR["body"], TYPE_PAIR["display"]}) <= 2,
        "أسرة خطوط واحدة أو اثنتان فقط (عرض + نص)")
    add("overused-font", not re.search(r"\b(Inter|Roboto|Arial)\b", css),
        "لا خطوط مستهلكة افتراضيًا (Inter/Roboto/Arial)", "WARN")
    add("ai-gradient", not re.search(r"linear-gradient\([^)]*(purple|#[89ab][0-9a-f]{2}[0-9a-f]{3})", css, re.I),
        "لا تدرجات بنفسجي→أزرق زخرفية", "WARN")
    add("caps-eyebrow", "text-transform:uppercase" not in css.replace(" ", ""),
        "لا عناوين علوية بأحرف كبيرة مفروضة", "WARN")
    add("reduced-motion", "prefers-reduced-motion" in css, "احترام تقليل الحركة")
    add("focus-visible", ":focus-visible" in css, "تركيز لوحة المفاتيح ظاهر")
    radii = set(re.findall(r"border-radius:\s*var\(--r-(sm|md|lg)\)", css))
    add("radius-scale", 1 < len(radii) <= 3, f"درجات استدارة مقصودة ({len(radii)} درجات)", "WARN")
    add("equal-edges", "--edge" in css and "padding:2.2rem var(--edge)" in css,
        "حواف يمين/يسار متساوية عبر متغيّر واحد")
    return out


# ════════════════════════════════════════════════════════════════════════════
# 2) جسر Node  (impeccable + designlang)  — اختياري ويعمل في وضع المطوّر
# ════════════════════════════════════════════════════════════════════════════
def node_env() -> dict[str, str | None]:
    return {"node": shutil.which("node"), "npx": shutil.which("npx")}


def _run(args: list[str], cwd: str | None = None, timeout: int = 240) -> dict[str, Any]:
    """تشغيل أمر دون shell، مع إيقاف تتبّع الاستخدام (DO_NOT_TRACK=1)."""
    env = {**os.environ, "DO_NOT_TRACK": "1", "CI": "1", "NO_COLOR": "1"}
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)
        return {"rc": p.returncode, "out": p.stdout, "err": p.stderr}
    except subprocess.TimeoutExpired:
        return {"rc": -1, "out": "", "err": f"انتهت المهلة ({timeout}ث)"}
    except FileNotFoundError as e:
        return {"rc": -1, "out": "", "err": f"الأمر غير موجود: {e}"}


def safe_url(u: str) -> str | None:
    p = urlparse(u.strip())
    if p.scheme in ("http", "https") and p.netloc:
        return u.strip()
    return None


def impeccable_detect(target: str) -> dict[str, Any]:
    """npx impeccable detect --json <مجلد|رابط>  (رمز الخروج 2 = وُجدت ملاحظات، 1 = تعذّر الفحص)."""
    env = node_env()
    if not env["npx"]:
        return {"ok": False, "error": "Node/npx غير مثبّت. ثبّت Node 20+ ثم أعد المحاولة."}
    res = _run([env["npx"], "--yes", "impeccable", "detect", "--json", target])
    findings: list[dict[str, Any]] = []
    raw = res["out"].strip()
    try:
        data = json.loads(raw) if raw else []
        items = data if isinstance(data, list) else data.get("findings", data.get("results", []))
        for it in items if isinstance(items, list) else []:
            if isinstance(it, dict):
                findings.append(it)
    except json.JSONDecodeError:
        pass
    return {"ok": res["rc"] in (0, 2), "rc": res["rc"], "findings": findings, "raw": raw, "err": res["err"]}


def designlang_extract(url: str, outdir: str, system_chrome: bool = False) -> dict[str, Any]:
    """npx designlang <url> --out <dir> ثم قراءة *-design-tokens.json (DTCG)."""
    env = node_env()
    if not env["npx"]:
        return {"ok": False, "error": "Node/npx غير مثبّت."}
    args = [env["npx"], "--yes", "designlang", url, "--out", outdir, "--name", "ref"]
    if system_chrome:
        args.append("--system-chrome")
    res = _run(args, timeout=300)
    files = sorted(Path(outdir).glob("*design-tokens.json"))
    tokens = None
    if files:
        try:
            tokens = json.loads(files[0].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            tokens = None
    md = sorted(Path(outdir).glob("*design-language.md"))
    return {"ok": tokens is not None, "rc": res["rc"], "tokens": tokens, "err": res["err"], "out": res["out"],
            "files": [f.name for f in Path(outdir).glob("*")] if Path(outdir).exists() else [],
            "language_md": md[0].read_text(encoding="utf-8")[:6000] if md else ""}


def _flatten_dtcg(node: Any, path: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(node, dict):
        if "$value" in node:
            flat[path] = node["$value"]
        for k, v in node.items():
            if k.startswith("$"):
                continue
            flat.update(_flatten_dtcg(v, f"{path}.{k}" if path else k))
    return flat


def _hex_of(v: Any) -> str | None:
    if isinstance(v, str) and _is_hex(v):
        return v.upper()
    if isinstance(v, dict):
        for key in ("hex", "value"):
            if _is_hex(v.get(key)):
                return str(v[key]).upper()
    return None


def dtcg_to_overrides(dtcg: dict[str, Any], base: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """يختار primary/bg/ink من رموز DTCG ثم يفحص WCAG؛ يرفض ما لا يحقق 4.5:1."""
    flat = {k.lower(): _hex_of(v) for k, v in _flatten_dtcg(dtcg).items() if _hex_of(v)}
    notes: list[str] = []

    def pick(*words: str) -> str | None:
        for k, v in flat.items():
            if all(w in k for w in words):
                return v
        return None

    cand = dict(base)
    primary = pick("primary") or pick("brand")
    bg = pick("background") or pick("surface")
    ink = pick("text") or pick("foreground")
    if primary:
        cand["primary"] = primary
        cand["on_primary"] = "#FFFFFF" if contrast("#FFFFFF", primary) >= contrast("#101820", primary) else "#101820"
    if bg:
        cand["bg"] = bg
    if ink:
        cand["ink"] = ink
    picked = [n for n, v in (("primary", primary), ("bg", bg), ("ink", ink)) if v]
    notes.append("رموز مُلتقطة: " + ("، ".join(picked) if picked else "لا شيء"))
    failures = [n for n, f, b, need in token_pairs(cand) if contrast(f, b) < need and n in (
        "النص الأساسي على الخلفية", "نص الزر الأساسي")]
    if failures:
        notes.append("رُفض التطبيق لعدم تحقيق WCAG AA في: " + "، ".join(failures))
        return {}, notes
    return {k: v for k, v in cand.items() if base.get(k) != v}, notes


# ════════════════════════════════════════════════════════════════════════════
# 3) نموذج المحتوى: اللبنات والمشاريع  (القسمان 4 و13)
# ════════════════════════════════════════════════════════════════════════════
def blk(bid: str, name: str, goal: str, action: list[str], expected: str, verify: dict,
        diag: list[tuple[str, str]], skill: str, stamp: str, *, minutes: int = 10,
        inputs: list[str] | None = None, safety: str | None = None, bridge: dict | None = None,
        code: str | None = None, why: str = "", deps: list[str] | None = None,
        core: bool = True, kind: str = "hw") -> dict[str, Any]:
    return dict(id=bid, name=name, goal=goal, action=action, expected=expected, verify=verify,
                diag=diag, skill=skill, stamp=stamp, minutes=minutes, inputs=inputs or [],
                safety=safety, bridge=bridge, code=code, why=why, deps=deps, core=core, kind=kind)


HW_SAFETY = ("افصل التغذية (كابل USB) قبل أي إعادة توصيل، وتحقق من جهد التشغيل في ورقة بيانات "
             "القطعة قبل وصلها باللوحة.")

# ─────────── المشروع 1: محطة مراقبة جودة الهواء (القسم 13 حرفيًا) ───────────
AIR = dict(
    id="air", title="محطة مراقبة جودة الهواء", kind="hardware", level="مبتدئ",
    outcome="محطة صغيرة تقرأ حسّاس هواء، تسجّل القياسات، وتعرض حالة مفهومة مع تنبيه بسيط.",
    tracks=["مدن أذكى", "صحراء وموارد"], tags=["إنترنت الأشياء والهاردوير", "مدن ذكية وجودة حياة", "لبنات قصيرة للمبتدئين", "مشروع لفريق هاكثون"],
    tools=["mcu", "sensor_air", "jumper", "breadboard", "usb", "led", "resistor"],
    risk="منخفض — جهد منخفض عبر USB. القراءة تعليمية وليست قياسًا معايَرًا ولا حكم سلامة.",
    blocks=[
        blk("a1", "افهم النتيجة", "تعرف ما ستقيسه المحطة وما لن تقيسه.",
            ["اقرأ بطاقة المشروع وصورة النتيجة النهائية.", "اكتب بكلماتك: ماذا ستقيس؟ وماذا لا يمكنها قياسه؟"],
            "عبارة واضحة عن حدود القياس.",
            dict(type="choice", q="أي عبارة صحيحة عن قراءة الحساس في نسختك الأولى؟",
                 options=["قراءة خام تدل على التغيّر وليست تركيزًا معايَرًا",
                          "تعطي تركيز الملوثات بدقة مخبرية",
                          "تحدد ما إذا كان الهواء آمنًا للتنفس"], answer=0),
            [("هل قرأت قسم «ما لن تقيسه المحطة»؟", "ارجع إلى بطاقة المشروع واقرأ الحدود أولًا.")],
            "جمع متطلبات", "عرّف نطاق القياس", minutes=6, kind="concept",
            why="الحدود الصريحة تمنع الاستنتاجات المبالغ فيها لاحقًا في العرض."),
        blk("a2", "جهّز وحدة التحكم", "اللوحة متصلة بالحاسوب وتظهر في بيئة البرمجة.",
            ["صِل اللوحة بكابل USB.", "اختر نوع اللوحة والمنفذ في بيئة البرمجة.", "ارفع برنامج «وميض» تجريبيًا."],
            "يومض ضوء اللوحة المدمج حسب البرنامج.",
            dict(type="choice", q="كيف تعرف أن اللوحة متصلة؟",
                 options=["يظهر منفذ تسلسلي جديد في بيئة البرمجة عند التوصيل", "يضيء الحاسوب", "لا يوجد ما يدل"], answer=0),
            [("هل جرّبت كابل USB آخر (بعض الكابلات للشحن فقط)؟", "بدّل الكابل؛ كثير من الكابلات لا تنقل البيانات."),
             ("هل ظهر منفذ جديد عند التوصيل؟", "ثبّت برنامج تشغيل اللوحة ثم أعد التوصيل."),
             ("هل نوع اللوحة المختار مطابق للوحتك؟", "أعد اختيار اللوحة الصحيحة من القائمة.")],
            "بناء نموذج أولي", "شغّل وحدة التحكم", minutes=12, inputs=["لوحة تحكم", "كابل USB"], safety=HW_SAFETY,
            why="اللوحة هي «العقل»: تقرأ المدخلات وتنفذ المنطق وتحرك المخرجات."),
        blk("a3", "وصّل أول حساس", "قراءة أول قيمة من حساس تماثلي عبر منفذ محدد.",
            ["افصل التغذية.", "صِل: تغذية الحساس ← 5V/3.3V (بحسب ورقة بيانات طرازك)، الأرضي ← GND، الخرج ← المنفذ A0.",
             "أعد التغذية وافتح الشاشة التسلسلية."],
            "تظهر أرقام على الشاشة التسلسلية.",
            dict(type="range", label="القراءة التي ظهرت على الشاشة التسلسلية", min=0, max=4095, edge_fail=True,
                 hint="حتى 1023 على Uno، وحتى 4095 على ESP32"),
            [("هل التغذية موصولة بالجهد الصحيح للطراز؟", "راجع ورقة بيانات القطعة قبل إعادة التغذية."),
             ("هل رقم المنفذ في الكود مطابق لمنفذ التوصيل؟", "غيّر ثابت SENSOR_PIN ليطابق المنفذ الفعلي."),
             ("هل القيمة 0 أو أقصى قيمة ثابتة؟", "غالبًا الخرج غير موصول أو الأرضي مفقود؛ أعد فحص السلك."),
             ("هل نجح اختبار «وميض» الأساسي قبل هذه اللبنة؟", "ارجع للّبنة السابقة وأكدها أولًا.")],
            "توصيل حساس", "وصّل مدخلًا تماثليًا", minutes=15,
            inputs=["حساس هواء تماثلي", "3 أسلاك توصيل", "لوحة تجارب"], safety=HW_SAFETY,
            bridge=dict(part="خرج الحساس", port="A0", ref="analogRead(A0)"),
            code="""const int SENSOR_PIN = A0;      // المنفذ الذي وصّلت به خرج الحساس

void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(SENSOR_PIN);
  Serial.println(raw);
  delay(1000);
}""", why="الجهد على الطرف يتحول إلى رقم؛ ما تقرؤه الشاشة هو انعكاس مباشر للتوصيل."),
        blk("a4", "اقرأ البيانات", "تربط القراءة بمتغيّر وتفهم وحدتها.",
            ["خزّن القراءة في متغيّر باسم له معنى.", "اكتب سطرًا يشرح: هذه قيمة خام وليست تركيزًا."],
            "تظهر القراءة باسم واضح مع وصف وحدتها.",
            dict(type="delta", q="سجّل قراءتين: الأولى في مكانك، والثانية بعد نقل الحساس لمكان آخر في الغرفة.",
                 min_delta=3),
            [("هل القراءتان متطابقتان تمامًا؟", "انتظر ثوانيَ بين القراءتين أو بدّل المكان أكثر."),
             ("هل تتذبذب القراءة بشدة؟", "اترك الحساس يسخن دقائق، فبعض الحساسات تحتاج وقت استقرار.")],
            "توصيل حساس", "فسّر قراءة حساس", minutes=10, deps=["a3"],
            bridge=dict(part="الحساس", port="A0", ref="raw"),
            code="""int raw = analogRead(A0);
Serial.print("air_raw=");     // قيمة خام: ليست ppm ولا معايَرة
Serial.println(raw);""", why="القيمة الخام تفيد في مقارنة التغيّر، لا في ادعاء تركيز."),
        blk("a5", "سجّل القياسات", "حفظ عدة قراءات بدل لقطة واحدة.",
            ["خزّن آخر 10 قراءات في مصفوفة.", "احسب المتوسط واطبعه."],
            "تظهر قيمة المتوسط بجانب القراءة الحالية.",
            dict(type="range", label="عدد القياسات التي سجّلتها", min=10, max=100000),
            [("هل المصفوفة تتجاوز حدودها؟", "تأكد أن المؤشر يعود إلى 0 عند بلوغ N.")],
            "اختبار نظام", "سجّل قياسات متعددة", minutes=15, deps=["a4"], core=True,
            code="""const int N = 10;
int readings[N];
int idx = 0;

void loop() {
  readings[idx] = analogRead(A0);
  idx = (idx + 1) % N;
  long sum = 0;
  for (int i = 0; i < N; i++) sum += readings[i];
  Serial.println(sum / N);   // المتوسط المتحرك
  delay(1000);
}"""),
        blk("a6", "اعرض الحالة", "عرض القراءة في واجهة بسيطة (الشاشة التسلسلية أو شاشة صغيرة).",
            ["اعرض: القراءة + المتوسط + نص حالة («مستقرة» / «تغيّرت»).", "حدّد من يقرأ الشاشة وماذا يحتاج أن يفهم."],
            "رسالة حالة مفهومة لمستخدم غير تقني.",
            dict(type="self", q="تظهر لي رسالة حالة مفهومة بالعربية بدل الأرقام وحدها."),
            [("هل الرسالة تشرح ما يجب فعله؟", "أضف جملة إجراء واحدة بجانب الحالة.")],
            "بناء نموذج أولي", "اعرض حالة النظام", minutes=15, deps=["a4"]),
        blk("a7", "اختبر التغيّر", "تتأكد أن النظام يستجيب لتغيّر حقيقي.",
            ["سجّل قراءة في مكان، وأخرى بعد 5 دقائق في مكان مختلف.", "دوّن الفرق."],
            "فرق ملحوظ في القراءتين مع ملاحظة السبب المحتمل.",
            dict(type="delta", q="أدخل قراءتين من ظرفين مختلفين.", min_delta=3),
            [("هل الظرفان مختلفان فعلًا؟", "غيّر الموقع أو التهوية بوضوح.")],
            "اختبار نظام", "اختبر استجابة نظام", minutes=12, deps=["a4"]),
        blk("a8", "فسّر النتيجة", "تكتب ما يمكن استنتاجه وما لا يمكن.",
            ["اكتب 3 استنتاجات مسموحة و3 غير مسموحة.", "اربط كل استنتاج بالدليل من دفتر الرحلة."],
            "نص تفسيري قصير يفرق بين الملاحظة والادعاء.",
            dict(type="text", q="اكتب ما يمكن وما لا يمكن استنتاجه من قراءاتك.", min_words=12),
            [("هل استنتاجك مدعوم بقراءة مسجلة؟", "ارجع لدفترك واذكر القراءة التي تدعمه.")],
            "شرح قرار تقني", "فسّر نتيجة اختبار", minutes=12, deps=["a5", "a7"]),
        blk("a9", "أضف تنبيهًا", "قاعدة واضحة ومراجعة تغيّر ضوءًا أو رسالة.",
            ["اختر عتبة من قياساتك لا من تخمين.", "أضف LED يضيء عند تجاوز العتبة."],
            "يضيء المؤشر عند تحقق الشرط.",
            dict(type="text", q="اكتب قاعدة التنبيه ومن أين جاءت العتبة.", min_words=8),
            [("هل العتبة قريبة من قراءاتك العادية؟", "ارفعها قليلًا حتى لا يعمل التنبيه دائمًا.")],
            "بناء نموذج أولي", "حوّل قراءة إلى قرار", minutes=15, deps=["a4", "a8"], core=False,
            inputs=["LED", "مقاومة 220Ω"], safety=HW_SAFETY,
            bridge=dict(part="LED", port="D13", ref="digitalWrite(13, HIGH)"),
            code="""const int LED_PIN = 13;
const int THRESHOLD = 600;   // قيمة تجريبية: حدّدها من قياساتك أنت

void setup() { pinMode(LED_PIN, OUTPUT); Serial.begin(9600); }

void loop() {
  int raw = analogRead(A0);
  digitalWrite(LED_PIN, raw > THRESHOLD ? HIGH : LOW);
  delay(500);
}"""),
        blk("a10", "جهّز بطاقة العرض", "تلخيص المشكلة والحل والدليل والحدود.",
            ["اكتب: المشكلة، الحل، الدليل (قراءة أو صورة)، الحدود."],
            "بطاقة عرض جاهزة للمشاركة.",
            dict(type="text", q="لخّص المشروع: المشكلة والحل والدليل والحدود.", min_words=20),
            [("هل ذكرت حدود المشروع بصراحة؟", "أضف جملة عمّا لا يفعله المشروع.")],
            "شرح قرار تقني", "اعرض مشروعًا بأدلته", minutes=15, deps=["a8"], kind="concept"),
    ],
)

# ─────────── المشروع 2: ري ذكي (صحراء وموارد) ───────────
SOIL_SAFETY = HW_SAFETY + " لا تتعامل مع كهرباء المنزل في هذا المسار؛ المخرجات هنا مؤشرات جهد منخفض فقط."
SOIL = dict(
    id="soil", title="مؤشر ري ذكي للنبات", kind="hardware", level="مبتدئ",
    outcome="نظام يقرأ رطوبة التربة ويعلن «اسقِ الآن» أو «كافٍ» بقاعدة معايَرة من قياساتك.",
    tracks=["صحراء وموارد"], tags=["إنترنت الأشياء والهاردوير", "استدامة وماء وطاقة", "لبنات قصيرة للمبتدئين"],
    tools=["mcu", "sensor_soil", "jumper", "breadboard", "usb", "led", "resistor"],
    risk="منخفض — جهد منخفض. محاكاة الري بمؤشر LED أولًا قبل أي مضخة.",
    blocks=[
        blk("s1", "افهم المشكلة", "تعرف لماذا القياس أفضل من الري بالتخمين.",
            ["حدّد نباتًا واحدًا وسؤالًا: متى يحتاج الماء فعلًا؟"], "سؤال قياس واضح.",
            dict(type="self", q="كتبت سؤال القياس الذي سيجيب عنه الحساس."), [("هل السؤال قابل للقياس؟", "اجعله عن رطوبة التربة لا عن «صحة النبات».")],
            "جمع متطلبات", "حدّد سؤال قياس", minutes=6, kind="concept"),
        blk("s2", "جهّز اللوحة", "اللوحة تعمل ومتصلة.", ["صِل اللوحة بـ USB وارفع برنامج الوميض."],
            "يومض الضوء المدمج.", dict(type="self", q="ظهر الوميض كما هو متوقع."),
            [("هل الكابل ينقل البيانات؟", "جرّب كابلًا آخر.")], "بناء نموذج أولي", "شغّل وحدة التحكم", minutes=10, safety=HW_SAFETY),
        blk("s3", "اقرأ رطوبة التربة", "أول قراءة تماثلية من حساس التربة.",
            ["افصل التغذية ثم وصّل: التغذية، الأرضي، الخرج ← A0.", "اقرأ القيمة وهو في الهواء."],
            "تظهر قيمة خام ثابتة نسبيًا في الهواء.",
            dict(type="range", label="القراءة في الهواء", min=0, max=4095, edge_fail=True),
            [("هل الأرضي موصول؟", "أعد فحص سلك GND."), ("هل المنفذ مطابق للكود؟", "طابق رقم المنفذ.")],
            "توصيل حساس", "وصّل مدخلًا تماثليًا", minutes=15, deps=["s2"], safety=SOIL_SAFETY,
            bridge=dict(part="خرج حساس التربة", port="A0", ref="analogRead(A0)"),
            code="""const int SOIL_PIN = A0;
void setup() { Serial.begin(9600); }
void loop() { Serial.println(analogRead(SOIL_PIN)); delay(1000); }"""),
        blk("s4", "عايِر الجاف والمبلل", "تحدد قيمتين مرجعيتين من قياسك.",
            ["سجّل القراءة والحساس في الهواء (جاف).", "سجّل القراءة في كوب ماء حتى الخط المحدد على الحساس (مبلل)."],
            "قيمتان مختلفتان بوضوح: DRY وWET.",
            dict(type="delta", q="أدخل قراءة الجاف ثم قراءة المبلل.", min_delta=50),
            [("هل غمرت الحساس أكثر من خط الغمر؟", "اغمره حتى الخط فقط لحماية الإلكترونيات.")],
            "اختبار نظام", "عايِر حساسًا", minutes=15, deps=["s3"], safety=SOIL_SAFETY),
        blk("s5", "حوّل القراءة لنسبة", "تحويل القيمة الخام إلى نسبة 0–100%.",
            ["استخدم DRY وWET في دالة map."], "تظهر نسبة رطوبة منطقية.",
            dict(type="range", label="النسبة التي ظهرت", min=0, max=100),
            [("هل النسبة معكوسة؟", "بعض الحساسات تنخفض قيمتها عند البلل؛ بدّل ترتيب DRY وWET.")],
            "تحليل بيانات", "حوّل قياسًا لنسبة", minutes=12, deps=["s4"],
            bridge=dict(part="قيمة خام", port="raw", ref="map(raw, DRY, WET, 0, 100)"),
            code="""const int DRY = 800;   // ضع قيمتك من لبنة المعايرة
const int WET = 400;

int pct = map(analogRead(A0), DRY, WET, 0, 100);
pct = constrain(pct, 0, 100);
Serial.println(pct);"""),
        blk("s6", "قرار الري", "مؤشر LED يمثل «اسقِ الآن».",
            ["اختر عتبة مثل 30%.", "أضئ LED عندما تقل النسبة عنها."], "يضيء المؤشر عند الجفاف.",
            dict(type="self", q="يضيء المؤشر عند جفاف التربة ويطفأ عند البلل."),
            [("هل العتبة مناسبة لنباتك؟", "جرّبها أسبوعًا وعدّلها من الملاحظة.")],
            "بناء نموذج أولي", "حوّل قراءة إلى قرار", minutes=15, deps=["s5"], inputs=["LED", "مقاومة 220Ω"], safety=SOIL_SAFETY,
            bridge=dict(part="LED", port="D13", ref="digitalWrite(13, pct < 30)")),
        blk("s7", "اختبر ظروفًا مختلفة", "تعرف أين يخطئ النظام.",
            ["اختبر تربة جافة، رطبة، ومبللة بالكامل.", "دوّن حالات الخطأ."], "جدول ثلاث حالات.",
            dict(type="text", q="صف نتائج الحالات الثلاث وأين أخطأ النظام.", min_words=15),
            [("هل غيّرت شيئًا واحدًا فقط في كل اختبار؟", "اختبر متغيرًا واحدًا كل مرة.")],
            "اختبار نظام", "اختبر استجابة نظام", minutes=15, deps=["s6"]),
        blk("s8", "جهّز بطاقة العرض", "تلخيص الحل بأدلته وحدوده.", ["اكتب المشكلة والحل والدليل والحدود."],
            "بطاقة عرض.", dict(type="text", q="لخّص المشروع بأدلته وحدوده.", min_words=20),
            [("هل ذكرت معايرتك الفعلية؟", "أدرج قيمتي DRY وWET.")], "شرح قرار تقني", "اعرض مشروعًا بأدلته", minutes=12, deps=["s7"], kind="concept"),
    ],
)

# ─────────── المشروع 3: بيانات عربية مفهومة (بلا هاردوير) ───────────
DATA = dict(
    id="data", title="لوحة بيانات عربية مفهومة", kind="software", level="مبتدئ",
    outcome="لوحة صغيرة تنظّف بيانات استهلاك مصطنعة وتعرضها وتشرح ما يمكن وما لا يمكن استنتاجه.",
    tracks=["بيانات عربية مفهومة", "مدن أذكى"], tags=["ذكاء اصطناعي وبيانات", "لبنات قصيرة للمبتدئين", "مشروع لفريق هاكثون"],
    tools=["laptop", "python"], risk="منخفض — بيانات مصطنعة، لا بيانات شخصية.",
    blocks=[
        blk("d1", "عرّف السؤال", "سؤال واحد قابل للإجابة بالبيانات.", ["اكتب السؤال والمقياس والمصدر."], "سؤال محدد.",
            dict(type="self", q="كتبت السؤال وتعريف المقياس ومصدره."), [("هل يمكن الإجابة عنه بجدول؟", "قلّص السؤال حتى يصير قابلًا للقياس.")],
            "جمع متطلبات", "عرّف سؤال بيانات", minutes=8, kind="sw"),
        blk("d2", "حمّل بيانات مصطنعة", "جدول من 60 صفًا فيه قيم ناقصة مقصودة.", ["شغّل الكود وأنشئ الجدول."],
            "جدول فيه 3 قيم ناقصة.", dict(type="range", label="عدد القيم الناقصة", min=3, max=3),
            [("هل استخدمت نفس البذرة 7؟", "غيّر rng ليكون default_rng(7).")], "تحليل بيانات", "حمّل بيانات", minutes=10, kind="sw", deps=["d1"],
            bridge=dict(part="الكود", port="DataFrame df", ref="df.isna().sum()"),
            code="""import numpy as np, pandas as pd

rng = np.random.default_rng(7)
days = pd.date_range("2026-01-01", periods=60, freq="D")
df = pd.DataFrame({
    "التاريخ": days,
    "الحي": rng.choice(["أ", "ب", "ج"], 60),
    "استهلاك_الماء_لتر": rng.normal(180, 25, 60).round(1),
})
df.loc[rng.choice(60, 3, replace=False), "استهلاك_الماء_لتر"] = np.nan
print(df.isna().sum())"""),
        blk("d3", "افحص الجدول", "تعرف شكل البيانات قبل تنظيفها.", ["شغّل info وdescribe."], "تفهم الأعمدة والقيم الناقصة.",
            dict(type="choice", q="لماذا نفحص الجدول قبل التنظيف؟",
                 options=["لنعرف الأنواع والنواقص والقيم الشاذة قبل أي قرار", "لأن التنظيف يتم تلقائيًا", "لا حاجة للفحص"], answer=0),
            [("هل ظهرت أنواع الأعمدة؟", "شغّل df.info().")], "تحليل بيانات", "افحص جدولًا", minutes=8, kind="sw", deps=["d2"],
            code="df.info()\nprint(df.describe(include='all'))"),
        blk("d4", "نظّف", "معالجة القيم الناقصة بقرار مُعلَّل.", ["املأ الناقص بوسيط الحي.", "دوّن سبب اختيارك."], "لا قيم ناقصة وتوثيق للقرار.",
            dict(type="range", label="عدد القيم الناقصة بعد التنظيف", min=0, max=0),
            [("هل غيّرت القيم الأصلية؟", "اعمل على نسخة df.copy().")], "تحليل بيانات", "نظّف بيانات", minutes=12, kind="sw", deps=["d3"],
            code="""clean = df.copy()
col = "استهلاك_الماء_لتر"
clean[col] = clean[col].fillna(clean.groupby("الحي")[col].transform("median"))
print(clean[col].isna().sum())"""),
        blk("d5", "لخّص", "متوسط الاستهلاك لكل حي.", ["استخدم groupby."], "جدول من 3 صفوف.",
            dict(type="range", label="عدد الأحياء في الملخص", min=3, max=3),
            [("هل جمّعت بعمود الحي؟", "groupby('الحي').")], "تحليل بيانات", "لخّص بيانات", minutes=8, kind="sw", deps=["d4"],
            code='summary = clean.groupby("الحي")["استهلاك_الماء_لتر"].mean().round(1)\nprint(summary)'),
        blk("d6", "ارسم", "رسم يجيب عن السؤال لا يزيّن الصفحة.", ["ارسم أعمدة لكل حي بعنوان عربي واضح."], "رسم بعنوان ووحدة.",
            dict(type="self", q="الرسم له عنوان ووحدة ويجيب عن سؤالي."), [("هل تظهر الحروف العربية صحيحة؟", "استخدم خطًا عربيًا في matplotlib أو أداة عرض Streamlit.")],
            "بناء نموذج أولي", "اعرض بيانات", minutes=12, kind="sw", deps=["d5"],
            code='summary.plot.bar(title="متوسط استهلاك الماء (لتر) لكل حي")'),
        blk("d7", "فسّر النتيجة", "ما يمكن وما لا يمكن استنتاجه.", ["اكتب استنتاجين مسموحين وآخرين غير مسموحين."], "نص تفسيري.",
            dict(type="text", q="اكتب ما يمكن وما لا يمكن استنتاجه.", min_words=15),
            [("هل البيانات مصطنعة؟", "اذكر ذلك صراحة ولا تعمّم.")], "شرح قرار تقني", "فسّر نتيجة اختبار", minutes=10, kind="sw", deps=["d6"]),
        blk("d8", "جهّز بطاقة العرض", "تلخيص بأدلته.", ["اكتب المشكلة والحل والدليل والحدود."], "بطاقة عرض.",
            dict(type="text", q="لخّص المشروع.", min_words=20), [("هل ذكرت الحدود؟", "أضف جملة عن حدود البيانات.")],
            "شرح قرار تقني", "اعرض مشروعًا بأدلته", minutes=10, kind="concept", deps=["d7"]),
    ],
)

PROJECTS: dict[str, dict[str, Any]] = {p["id"]: p for p in (AIR, SOIL, DATA)}


def all_projects() -> dict[str, dict[str, Any]]:
    """المشاريع الرسمية + المسارات المعتمدة من المنظم (من «فكّك فكرتي»)."""
    merged = dict(PROJECTS)
    for pid, p in st.session_state.get("db", {}).get("custom_projects", {}).items():
        merged[pid] = p
    return merged


def block_deps(project: dict, idx: int) -> list[str]:
    b = project["blocks"][idx]
    if b["deps"] is not None:
        return b["deps"]
    return [project["blocks"][idx - 1]["id"]] if idx > 0 else []


# ════════════════════════════════════════════════════════════════════════════
# 4) كتالوج الأدوات وقواعد التوافق  (طبقة الأدوات والتوافق — القسم 12)
# ════════════════════════════════════════════════════════════════════════════
CATALOG: dict[str, dict[str, str]] = {
    "mcu": dict(name="لوحة تحكم", note="Arduino Uno أو ESP32 DevKit أو ما يعادلها"),
    "sensor_air": dict(name="حساس هواء تماثلي", note="الطراز يحدده المشرف"),
    "sensor_soil": dict(name="حساس رطوبة تربة تماثلي", note="سعوي أو مقاومي"),
    "jumper": dict(name="أسلاك توصيل", note=""),
    "breadboard": dict(name="لوحة تجارب", note=""),
    "usb": dict(name="كابل USB للبيانات", note="ليس كابل شحن فقط"),
    "led": dict(name="LED", note=""),
    "resistor": dict(name="مقاومة 220Ω", note=""),
    "laptop": dict(name="حاسوب", note=""),
    "python": dict(name="Python 3.10+", note=""),
    "mcu_esp32_variant": dict(name="لوحة ESP32 DevKit (بديل معتمد بشروط)", note="منطق 3.3V"),
}

# قواعد بدائل مراجَعة (لا تُقترح البدائل لمجرد تشابه الاسم)
REVIEWED_SUBS: dict[str, list[tuple[str, str]]] = {
    "mcu": [("mcu_esp32_variant", "ESP32 بديل بشرط: منطق 3.3V (لا 5V) ومدى ADC حتى 4095؛ عدّل المدى في الكود.")],
}

AVAIL = {
    "yes": ("متوفر", "ok"),
    "verify": ("متوفر لكن يحتاج تحققًا من الطراز", "acc"),
    "missing": ("ناقص", "warn"),
    "sub": ("يوجد بديل معتمد", "acc"),
    "unknown": ("غير معروف — لا نريد التخمين", ""),
}


def availability(db: dict, need: str) -> tuple[str, str]:
    """يعيد (مفتاح الحالة, ملاحظة)."""
    owned = [t for t in db["tools"].values() if t["cat"] == need]
    confirmed = [t for t in owned if t["status"] in ("confirmed", "documented")]
    if confirmed:
        return ("yes", "") if any(t["model"] for t in confirmed) else ("verify", "أضف الطراز لتأكيده.")
    if any(t["status"] == "suggested" for t in owned):
        return "unknown", "اقتراح بصري لم تؤكده بعد."
    for sub_cat, rule in REVIEWED_SUBS.get(need, []):
        if any(t["cat"] == sub_cat and t["status"] in ("confirmed", "documented") for t in db["tools"].values()):
            return "sub", rule
    return "missing", ""


# ════════════════════════════════════════════════════════════════════════════
# 5) الحالة والحفظ والأحداث
# ════════════════════════════════════════════════════════════════════════════
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_db() -> dict[str, Any]:
    return dict(
        profile=dict(name="", experience="مبتدئ", minutes=30, team="فردي", goal=""),
        formal_mode=False, dark_mode=False, palette="حجر", leaderboard=False, theme_override={},
        tools={}, projects={}, ledger=[], stamps=[], notebook=[], events=[], drafts=[], custom_projects={},
        active=dict(project=None, block=None),
        team=dict(name="", members=[], project=None, contrib=[], help=[], reviews=[]),
        share=dict(show_name=False, show_notes=False, show_evidence=True, show_team=False),
    )


def load_db() -> dict[str, Any]:
    base = new_db()
    try:
        if DATA_PATH.exists():
            saved = json.loads(DATA_PATH.read_text(encoding="utf-8"))
            for k, v in saved.items():
                base[k] = v
    except (OSError, json.JSONDecodeError):
        pass
    return base


def save() -> None:
    try:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = DATA_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(st.session_state["db"], ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(DATA_PATH)
    except OSError:
        pass  # الحفظ best-effort؛ لا يوقف التطبيق


def db() -> dict[str, Any]:
    if "db" not in st.session_state:
        st.session_state["db"] = load_db()
    return st.session_state["db"]


def log_event(kind: str, **kw: Any) -> None:
    db()["events"].append({"ts": now_iso(), "kind": kind, **kw})


def goto(page: str) -> None:
    st.session_state["_goto"] = page
    st.rerun()


def pstate(pid: str) -> dict[str, Any]:
    return db()["projects"].setdefault(pid, dict(started_at=None, blocks={}))


def bstate(pid: str, bid: str) -> dict[str, Any]:
    return pstate(pid)["blocks"].setdefault(
        bid, dict(level=0, note="", attempts=0, helps=0, diagnosed=0, fixed=0, started_at=None, done_at=None, reviewer=None))


def block_level(pid: str, bid: str) -> int:
    return int(pstate(pid)["blocks"].get(bid, {}).get("level", 0))


def is_unlocked(project: dict, idx: int) -> bool:
    return all(block_level(project["id"], d) >= 1 for d in block_deps(project, idx))


def score_label() -> str:
    return "رصيد التقدم" if db()["formal_mode"] else "نقاط الشجاعة"


def points_total() -> dict[str, int]:
    tot = {k: 0 for k in COURAGE}
    for r in db()["ledger"]:
        tot[r["kind"]] = tot.get(r["kind"], 0) + r["points"]
    return tot


def award(kind: str, points: int, reason: str, key: str) -> bool:
    """منح نقاط مع منع التكرار والتلاعب: المفتاح فريد لكل سبب."""
    if any(r["key"] == key for r in db()["ledger"]):
        return False
    db()["ledger"].append(dict(ts=now_iso(), kind=kind, points=points, reason=reason, key=key))
    return True


def grant_stamp(project: dict, block: dict, level: int) -> None:
    for s in db()["stamps"]:
        if s["project"] == project["id"] and s["block"] == block["id"]:
            s["level"] = max(s["level"], level)
            return
    db()["stamps"].append(dict(ts=now_iso(), project=project["id"], block=block["id"], stamp=block["stamp"],
                               skill=block["skill"], level=level))


# ════════════════════════════════════════════════════════════════════════════
# 6) التحقق من اللبنة
# ════════════════════════════════════════════════════════════════════════════
def evaluate(spec: dict, v: dict[str, Any]) -> tuple[bool, int, str]:
    """يعيد (نجح؟, مستوى الدليل, رسالة). self/text → أكملتها، والبقية → تحققت."""
    t = spec["type"]
    if t == "self":
        return bool(v.get("checked")), 1, "أكدت التنفيذ. للحصول على «تحققت» أضف نتيجة قابلة للملاحظة في دفتر الرحلة."
    if t == "choice":
        ok = v.get("choice") == spec["answer"]
        return ok, 2, "إجابة صحيحة." if ok else "ليست دقيقة. راجع شرح اللبنة ثم أعد المحاولة."
    if t == "range":
        x = v.get("x")
        if x is None:
            return False, 2, "أدخل القيمة."
        if spec.get("edge_fail") and x in (spec["min"], spec["max"]):
            return False, 2, "القيمة طرفية (أدنى أو أقصى). غالبًا هناك مشكلة في التوصيل؛ جرّب مسار التشخيص."
        ok = spec["min"] <= x <= spec["max"]
        return ok, 2, "ظهرت نتيجة ضمن المدى المتوقع." if ok else f"خارج المدى المتوقع ({spec['min']}–{spec['max']})."
    if t == "delta":
        a, b = v.get("a"), v.get("b")
        if a is None or b is None:
            return False, 2, "أدخل القراءتين."
        ok = abs(a - b) >= spec["min_delta"]
        return ok, 2, "اختلفت القراءتان بما يكفي لإثبات الاستجابة." if ok else \
            f"الفرق أقل من {spec['min_delta']}. غيّر الظرف بوضوح ثم أعد القياس."
    if t == "text":
        words = len((v.get("text") or "").split())
        ok = words >= spec["min_words"]
        return ok, 1, "تم حفظ التفسير." if ok else f"النص قصير ({words} كلمة). المطلوب {spec['min_words']} على الأقل."
    return False, 0, "نوع تحقق غير معروف."


def complete_block(project: dict, block: dict, level: int, evidence: dict[str, Any]) -> None:
    bs = bstate(project["id"], block["id"])
    first_time = bs["level"] == 0
    bs["level"] = max(bs["level"], level)
    bs["done_at"] = bs["done_at"] or now_iso()
    bs["attempts"] += 1
    bs["evidence"] = evidence
    pid, bid = project["id"], block["id"]
    if level >= 2:
        award("try", 10, f"تحقق من نتيجة: {block['name']}", f"verify:{pid}:{bid}")
    else:
        award("try", 3, f"أكمل: {block['name']}", f"done:{pid}:{bid}")
    grant_stamp(project, block, bs["level"])
    log_event("block_done", project=pid, block=bid, level=bs["level"], first=first_time)


# ════════════════════════════════════════════════════════════════════════════
# 7) خدمات الذكاء الاصطناعي (اختيارية) — لا تُصدر أحكام سلامة ولا تختلق مواصفات
# ════════════════════════════════════════════════════════════════════════════
def llm_json(system: str, user: str, image: tuple[bytes, str] | None = None) -> tuple[Any, str | None]:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None, "لم يُضبط ANTHROPIC_API_KEY؛ يعمل النظام بالقواعد المحلية."
    try:
        import anthropic  # noqa: WPS433
    except ImportError:
        return None, "ثبّت الحزمة: pip install anthropic"
    content: list[dict[str, Any]] = []
    if image:
        content.append({"type": "image", "source": {"type": "base64", "media_type": image[1],
                                                    "data": base64.b64encode(image[0]).decode()}})
    content.append({"type": "text", "text": user})
    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(model=MODEL, max_tokens=1500, system=system,
                                      messages=[{"role": "user", "content": content}])
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
        return json.loads(text), None
    except Exception as e:  # noqa: BLE001
        return None, f"تعذّر الاتصال بالنموذج: {e}"


SYS_IDEA = ("أنت مساعد في منصة لَبنَة. حوّل فكرة المستخدم إلى مسودة قابلة للمراجعة فقط، بصيغة JSON بالمفاتيح: "
            "problem, beneficiary, outcome, v1, blocks (قائمة أسماء أفعال قصيرة), tools, risks, questions. "
            "لا تخترع دوائر أو مواصفات أو كودًا. اذكر عدم اليقين. أجب بـ JSON فقط بالعربية.")
SYS_VISION = ("اقترح تعرّفًا أوليًا على القطع الإلكترونية في الصورة. أجب بـ JSON: قائمة عناصر "
              "{name, category, confidence (0-1), needs_review (bool), note}. هذا اقتراح لا تأكيد، ولا تحكم بالسلامة "
              "ولا تذكر طرازًا إلا إذا كان مكتوبًا بوضوح على القطعة.")

SAFETY_WORDS = ["غاز", "كهرباء", "حريق", "دواء", "طبي", "سلامة", "تيار", "جهد عال", "بطارية ليثيوم", "مضخة"]
DOMAIN_RULES = [
    (["هواء", "غبار", "تلوث"], "air", "مدن أذكى"),
    (["ري", "ماء", "نبات", "زراعة", "تربة"], "soil", "صحراء وموارد"),
    (["بيانات", "تحليل", "لوحة", "إحصاء"], "data", "بيانات عربية مفهومة"),
]


def decompose_idea(idea: str) -> dict[str, Any]:
    """مسودة بقواعد محلية، وتُحسَّن بالنموذج إن توفّر المفتاح. تبقى مسودة حتى يعتمدها منظم."""
    risks = [f"الفكرة تمس موضوع «{w}»: تحتاج مراجعة مختص ولا تُعتمد كجهاز سلامة." for w in SAFETY_WORDS if w in idea]
    def has_word(w: str) -> bool:
        return bool(re.search(rf"(?<!\w)(?:ال|لل|بال|ل|ب)?{re.escape(w)}\w{{0,2}}(?!\w)", idea))

    related = next(((pid, tr) for words, pid, tr in DOMAIN_RULES if any(has_word(w) for w in words)), None)
    draft: dict[str, Any] = dict(
        idea=idea, status="مسودة — تحتاج مراجعة", ts=now_iso(),
        problem="", beneficiary="", outcome="", v1="",
        blocks=["افهم النتيجة", "جهّز الأدوات", "نفّذ أصغر نسخة تعمل", "اختبرها بحالتين", "فسّر النتيجة", "جهّز بطاقة العرض"],
        tools=[], risks=risks, related=related[0] if related else None, track=related[1] if related else None,
        questions=["من المستفيد بالضبط؟", "ما أصغر نتيجة يمكن ملاحظتها؟", "ما الأدوات المتاحة لديك الآن؟"],
        source="rules",
    )
    obj, err = llm_json(SYS_IDEA, idea)
    if isinstance(obj, dict):
        for k in ("problem", "beneficiary", "outcome", "v1", "blocks", "tools", "risks", "questions"):
            if obj.get(k):
                draft[k] = obj[k] if k != "risks" else list(dict.fromkeys(risks + list(obj[k])))
        draft["source"] = "llm"
    elif err:
        draft["llm_note"] = err
    return draft


def draft_to_project(d: dict[str, Any]) -> dict[str, Any]:
    pid = "c" + re.sub(r"\D", "", d["ts"])[-10:]
    blocks = []
    for i, name in enumerate(d["blocks"], 1):
        blocks.append(blk(f"{pid}b{i}", str(name), f"نتيجة ملاحظة لـ «{name}».", ["نفّذ الخطوة ودوّن ما رأيته."],
                          "نتيجة قابلة للملاحظة.", dict(type="text", q=f"صف ما ظهر لك في «{name}».", min_words=8),
                          [("ما النتيجة التي ظهرت؟", "دوّنها ثم ضيّق الاحتمالات مع المرشد.")],
                          "بناء نموذج أولي", f"أنجز: {name}", minutes=15, kind="concept"))
    return dict(id=pid, title=(d["idea"][:60] or "مسار مخصص"), kind="custom", level="مبتدئ",
                outcome=d.get("outcome") or d.get("v1") or "نسخة أولى تعمل.", tracks=[d.get("track") or "مدن أذكى"],
                tags=["مشروع لفريق هاكثون"], tools=[], risk="؛ ".join(d.get("risks") or ["بحسب مراجعة المنظم"]), blocks=blocks)


# ════════════════════════════════════════════════════════════════════════════
# 8) مكونات واجهة مشتركة
# ════════════════════════════════════════════════════════════════════════════
def esc(x: Any) -> str:
    return _html.escape(str(x))


def card(inner: str, cls: str = "") -> None:
    st.markdown(f'<div class="lb-card {cls}">{inner}</div>', unsafe_allow_html=True)


def tag(text: str, kind: str = "") -> str:
    return f'<span class="lb-tag {kind}">{esc(text)}</span>'


def strip(project: dict, current_idx: int | None = None) -> None:
    segs = []
    for i, b in enumerate(project["blocks"]):
        lv = block_level(project["id"], b["id"])
        cls = f"lb-seg s{lv}" + (" cur" if i == current_idx else "") + ("" if is_unlocked(project, i) else " lock")
        label = f'{i + 1}{LEVEL_ICON[lv] if lv else ""}'
        segs.append(f'<div class="{cls}" title="{esc(b["name"])} — {LEVELS[lv]}">{label}</div>')
    st.markdown(f'<div class="lb-strip" role="list" aria-label="خريطة اللبنات">{"".join(segs)}</div>', unsafe_allow_html=True)


def project_progress(project: dict) -> tuple[int, int]:
    core = [b for b in project["blocks"] if b["core"]]
    done = sum(1 for b in core if block_level(project["id"], b["id"]) >= 1)
    return done, len(core)


def next_block_idx(project: dict) -> int | None:
    for i, b in enumerate(project["blocks"]):
        if block_level(project["id"], b["id"]) == 0 and is_unlocked(project, i):
            return i
    return None


def ready_for_showcase(project: dict) -> bool:
    """جاهزة للعرض: كل اللبنات الأساسية مكتملة، والقابلة للقياس منها (قراءة/اختبار/سؤال) متحقق منها فعلًا."""
    for b in project["blocks"]:
        if not b["core"]:
            continue
        need = 2 if b["verify"]["type"] in ("range", "delta", "choice") else 1
        if block_level(project["id"], b["id"]) < need:
            return False
    return True


def graph_dot(project: dict) -> str:
    colors = {0: "#9AA5AA", 1: "#A66A00", 2: "#14693F", 3: "#0E6B5C"}
    lines = ['digraph G { rankdir=RL; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, fontcolor="white"];']
    for i, b in enumerate(project["blocks"]):
        lv = block_level(project["id"], b["id"])
        lines.append(f'"{b["id"]}" [label="{i + 1}. {b["name"]}\\n{LEVELS[lv]}", fillcolor="{colors[lv]}"];')
    for i, b in enumerate(project["blocks"]):
        for d in block_deps(project, i):
            lines.append(f'"{d}" -> "{b["id"]}";')
    lines.append("}")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# 9) صفحة: مساري
# ════════════════════════════════════════════════════════════════════════════
def onboarding() -> None:
    d = db()
    st.markdown("## ماذا تريد أن تبني أو تحاول حلّه؟")
    st.markdown('<p class="lb-muted">لا تحتاج إلى فهم المشروع كله كي تبدأ. أجب عن أسئلة قليلة لنختار لك نقطة بداية.</p>',
                unsafe_allow_html=True)
    with st.form("onboard"):
        goal = st.selectbox("النتيجة التي تريدها", [
            "محطة تقيس شيئًا في البيئة", "نظام ري أو توفير موارد", "تحليل بيانات وعرضها بالعربية", "لا أعرف بعد"])
        c1, c2 = st.columns(2)
        exp = c1.selectbox("خبرتك", ["مبتدئ", "جرّبت قليلًا", "متوسط"])
        minutes = c2.select_slider("كم دقيقة لديك الآن؟", [10, 15, 30, 45, 60, 90], value=30)
        team = st.radio("تعمل", ["فردي", "مع فريق"], horizontal=True)
        tools = st.multiselect("الأدوات التي تملكها", [v["name"] for v in CATALOG.values()])
        if st.form_submit_button("اقترح لي نقطة بداية", type="primary"):
            d["profile"].update(goal=goal, experience=exp, minutes=minutes, team=team)
            for tid, v in CATALOG.items():
                if v["name"] in tools and not any(t["cat"] == tid for t in d["tools"].values()):
                    d["tools"][f"manual_{tid}"] = dict(cat=tid, name=v["name"], model="", count=1, status="confirmed", source="manual")
            log_event("onboarded", goal=goal)
            save()
            st.rerun()


def recommend() -> str:
    goal = db()["profile"].get("goal", "")
    if "ري" in goal:
        return "soil"
    if "بيانات" in goal:
        return "data"
    return "air"


def page_path() -> None:
    d = db()
    name = d["profile"].get("name")
    st.markdown(f"# {'أهلًا ' + esc(name) if name else 'مساري'}")
    if not d["profile"].get("goal"):
        onboarding()
        return

    # آخر مشروع نشط
    active_pid = d["active"]["project"] or next((pid for pid, p in d["projects"].items() if p["started_at"]), None)
    projects = all_projects()
    if not active_pid or active_pid not in projects or not pstate(active_pid)["started_at"]:
        rec = projects[recommend()]
        n_blocks = len(rec["blocks"])
        n_minutes = sum(b["minutes"] for b in rec["blocks"])
        card(f'<h3>ابدأ لبنتك الأولى</h3><div class="lb-big">{esc(rec["title"])}</div>'
             f'<p>{esc(rec["outcome"])}</p>'
             f'<div class="lb-row">{tag(str(n_blocks) + " لبنات")}{tag("≈ " + str(n_minutes) + " دقيقة")}{tag(rec["level"])}</div>',
             "primary")
        if st.button("ابدأ لبنتك الأولى", type="primary"):
            d["active"]["project"] = rec["id"]
            st.session_state["view_project"] = rec["id"]
            goto("المشاريع")
        return

    p = projects[active_pid]
    idx = next_block_idx(p)
    done, total = project_progress(p)
    st.progress(done / total if total else 0.0, text=f"{p['title']} — {done} من {total} لبنات أساسية")
    strip(p, idx)

    if idx is None:
        st.success("أكملت كل لبنات هذا المسار المتاحة. افتح جواز لَبنَة لتراجع الأدلة وتجهّز العرض.")
    else:
        b = p["blocks"][idx]
        mins_tag = tag("≈ " + str(b["minutes"]) + " دقائق")
        card(f'<h3>الخطوة التي تستطيع إنجازها الآن</h3><div class="lb-big">{esc(b["name"])}</div>'
             f'<p>{esc(b["goal"])}</p><div class="lb-row">{mins_tag}{tag(b["skill"])}</div>', "primary")
        if st.button("أكمل من حيث توقفت", type="primary"):
            d["active"].update(project=p["id"], block=b["id"])
            st.session_state["view_project"] = p["id"]
            goto("المشاريع")

    c1, c2, c3 = st.columns(3)
    tot = points_total()
    c1.metric(score_label(), sum(tot.values()))
    c2.metric("أختام الجواز", len(d["stamps"]))
    c3.metric("لبنات مكتملة", sum(1 for pr in d["projects"].values() for b in pr["blocks"].values() if b["level"] >= 1))

    # جلسة قصيرة مقترحة
    short = [(i, b) for i, b in enumerate(p["blocks"]) if block_level(p["id"], b["id"]) == 0 and is_unlocked(p, i) and b["minutes"] <= 10]
    if short:
        i, b = short[0]
        st.info(f"لديك لبنة مدتها {b['minutes']} دقائق: «{b['name']}».")
    stuck = [b["name"] for b in p["blocks"] if bstate(p["id"], b["id"])["diagnosed"] and block_level(p["id"], b["id"]) == 0]
    if stuck:
        st.warning("موضع التعثر: " + "، ".join(stuck))


# ════════════════════════════════════════════════════════════════════════════
# 10) صفحة: المشاريع (+ شاشة اللبنة)
# ════════════════════════════════════════════════════════════════════════════
TAG_FILTERS = ["أستطيع إنجازه بالأدوات التي أملكها", "لبنات قصيرة للمبتدئين", "مشروع لفريق هاكثون", "ذكاء اصطناعي وبيانات",
               "إنترنت الأشياء والهاردوير", "مدن ذكية وجودة حياة", "استدامة وماء وطاقة", "تقنيات مساعدة وإتاحة"]


def page_projects() -> None:
    st.markdown("# المشاريع")
    d = db()
    pid = st.session_state.get("view_project")
    projects = all_projects()
    if pid and pid in projects:
        project_view(projects[pid])
        return

    sel = st.multiselect("تصفية", TAG_FILTERS, placeholder="كل المشاريع")
    for p in projects.values():
        if sel:
            ok = True
            for f in sel:
                if f == "أستطيع إنجازه بالأدوات التي أملكها":
                    ok &= all(availability(d, t)[0] in ("yes", "verify", "sub") for t in p["tools"])
                else:
                    ok &= f in p["tags"]
            if not ok:
                continue
        done, total = project_progress(p)
        n_blocks = tag(str(len(p["blocks"])) + " لبنة")
        n_minutes = tag("≈ " + str(sum(b["minutes"] for b in p["blocks"])) + " دقيقة")
        track_tags = "".join(tag(t, "acc") for t in p["tracks"])
        card(f'<h3>{esc(p["title"])}</h3><p>{esc(p["outcome"])}</p><div class="lb-row">'
             f'{n_blocks}{n_minutes}{tag(p["level"])}{track_tags}</div>'
             f'<p class="lb-muted">تقدمك: {done} من {total} لبنات أساسية</p>')
        if st.button("افتح المشروع", key=f"open_{p['id']}"):
            st.session_state["view_project"] = p["id"]
            st.rerun()

    st.markdown("## مسارات التحديات المحلية")
    st.caption("سياقات تعليمية مستلهمة من احتياجات عامة. لا تُنسب إلى جهة معينة دون شراكة رسمية.")
    for t, desc in LOCAL_TRACKS.items():
        have = [p["title"] for p in projects.values() if t in p["tracks"]]
        st.markdown(f"**{t}** — {desc}" + (f"  \n*متاح الآن:* {'، '.join(have)}" if have else "  \n*قريبًا*"))


def project_view(p: dict) -> None:
    d = db()
    if st.button("‹ كل المشاريع"):
        st.session_state.pop("view_project", None)
        st.rerun()
    st.markdown(f"## {p['title']}")
    ps = pstate(p["id"])

    # بطاقة المشروع قبل البدء (القسم 5)
    if not ps["started_at"]:
        phases = {"مفهوم": 0, "تنفيذ": 0}
        for b in p["blocks"]:
            phases["مفهوم" if b["kind"] in ("concept",) else "تنفيذ"] += b["minutes"]
        card(f'<h3>بطاقة المشروع</h3><div class="lb-result">{esc(p["outcome"])}</div>'
             f'<p><b>الوقت التقريبي:</b> مفاهيم {phases["مفهوم"]} د — تنفيذ {phases["تنفيذ"]} د</p>'
             f'<p><b>المهارات:</b> {"، ".join(sorted({b["skill"] for b in p["blocks"]}))}</p>'
             f'<p><b>المخاطر والتنبيهات:</b> {esc(p["risk"])}</p>'
             f'<p><b>ما ستحصل عليه في الجواز:</b> {len({b["stamp"] for b in p["blocks"]})} أختامًا دقيقة و{score_label()}.</p>', "primary")
        st.markdown("**الأدوات**")
        for t in p["tools"]:
            key, note = availability(d, t)
            label, kind = AVAIL[key]
            st.markdown(f'{tag(label, kind)} {esc(CATALOG[t]["name"])} <span class="lb-muted">{esc(note)}</span>', unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        if c1.button("ابدأ بالنسخة الأساسية", type="primary", use_container_width=True):
            ps["started_at"] = now_iso()
            d["active"].update(project=p["id"], block=p["blocks"][0]["id"])
            award("start", 10, f"بدأ المشروع: {p['title']}", f"start:{p['id']}")
            log_event("project_start", project=p["id"])
            save()
            st.rerun()
        c2.button("استكشف المسار أولًا", use_container_width=True, key="explore")
        with st.expander("استكشاف المسار", expanded=False):
            for i, b in enumerate(p["blocks"], 1):
                st.markdown(f"{i}. **{b['name']}** — {b['goal']} " + ("" if b["core"] else "*(ترقية)*"))
        return

    # عودة بعد توقف
    last = max((x.get("done_at") or "" for x in ps["blocks"].values()), default="")
    if last:
        try:
            gap = datetime.now(timezone.utc) - datetime.fromisoformat(last)
            if gap.total_seconds() > 86400 and award("start", 5, "عودة بعد توقف", f"return:{datetime.now().date()}"):
                st.toast("شجاعة البداية: عدت بعد توقف.")
        except ValueError:
            pass

    active_bid = d["active"]["block"] if d["active"]["project"] == p["id"] else None
    idx = next((i for i, b in enumerate(p["blocks"]) if b["id"] == active_bid), None)
    if idx is None:
        idx = next_block_idx(p) or 0
    strip(p, idx)

    labels = [f'{i + 1}. {b["name"]} {LEVEL_ICON[block_level(p["id"], b["id"])]}' + ("" if is_unlocked(p, i) else " 🔒") +
              ("" if b["core"] else " (ترقية)") for i, b in enumerate(p["blocks"])]
    choice = st.selectbox("اللبنة", range(len(labels)), index=idx, format_func=lambda i: labels[i], label_visibility="collapsed")
    if choice != idx:
        d["active"].update(project=p["id"], block=p["blocks"][choice]["id"])
        st.rerun()
    block_screen(p, choice)


def block_screen(p: dict, idx: int) -> None:
    """شاشة اللبنة: هدف → نفّذ الآن → تحقق → مساعدة → انتقل."""
    d = db()
    b = p["blocks"][idx]
    bs = bstate(p["id"], b["id"])
    if not is_unlocked(p, idx):
        need = [x["name"] for x in p["blocks"] if x["id"] in block_deps(p, idx) and block_level(p["id"], x["id"]) < 1]
        st.warning("هذه اللبنة تعتمد على: " + "، ".join(need))
        return
    if not bs["started_at"]:
        bs["started_at"] = now_iso()
        log_event("block_start", project=p["id"], block=b["id"])
        save()

    st.markdown(f"### {b['name']}")
    st.markdown(f'<div class="lb-result"><b>الهدف المرئي:</b> {esc(b["goal"])}</div>', unsafe_allow_html=True)
    lvl_kind = "ok" if bs["level"] >= 2 else ("acc" if bs["level"] else "")
    st.markdown(tag("≈ " + str(b["minutes"]) + " دقائق") + tag(b["skill"]) + tag(LEVELS[bs["level"]], lvl_kind),
                unsafe_allow_html=True)

    if b["safety"]:  # لا يختبئ داخل «التفاصيل»
        st.markdown(f'<div class="lb-safety" role="alert"><strong>⚠ قبل أن تبدأ:</strong> {esc(b["safety"])}</div>', unsafe_allow_html=True)

    st.markdown("**نفّذ الآن**")
    for i, a in enumerate(b["action"], 1):
        st.markdown(f"{i}. {a}")
    if b["inputs"]:
        st.caption("تحتاج: " + "، ".join(b["inputs"]))
    st.markdown(f"**النتيجة المتوقعة:** {b['expected']}")

    if b["bridge"]:  # جسر المادة والكود (القسم 7.4)
        br = b["bridge"]
        if p["kind"] == "software":
            sentence = f"شغّلت «{br['part']}» فأنتج «{br['port']}»، لذلك يحسب البرنامج: {br['ref']}"
        else:
            sentence = f"وصلت «{br['part']}» بالمنفذ {br['port']}، لذلك يقرأ البرنامج القيمة من {br['port']}."
        st.markdown(f'<div class="lb-card"><b>جسر المادة والكود</b><p>{esc(sentence)}</p></div>', unsafe_allow_html=True)
        st.graphviz_chart(f'digraph{{rankdir=LR;node[shape=box,style=rounded,fontname=Helvetica];'
                          f'"{br["part"]}"->"{br["port"]}"->"{br["ref"]}"}}', use_container_width=True)

    if b["code"]:
        with st.expander("الكود", expanded=(b["kind"] == "sw")):
            st.code(b["code"], language="python" if p["kind"] == "software" else "cpp")
    if b["why"]:
        with st.expander("لماذا هذه القطعة / هذه الخطوة؟"):
            st.write(b["why"])

    # ── التحقق ──
    st.markdown("#### تحقق")
    spec = b["verify"]
    vals: dict[str, Any] = {}
    with st.form(f"verify_{p['id']}_{b['id']}"):
        t = spec["type"]
        if t == "self":
            vals["checked"] = st.checkbox(spec["q"])
        elif t == "choice":
            vals["choice"] = st.radio(spec["q"], range(len(spec["options"])), format_func=lambda i: spec["options"][i], index=None)
        elif t == "range":
            vals["x"] = st.number_input(spec["label"] + (f" ({spec['hint']})" if spec.get("hint") else ""), value=None, step=1, placeholder="أدخل رقمًا")
        elif t == "delta":
            st.write(spec["q"])
            c1, c2 = st.columns(2)
            vals["a"] = c1.number_input("القراءة الأولى", value=None, step=1, key=f"a_{b['id']}")
            vals["b"] = c2.number_input("القراءة الثانية", value=None, step=1, key=f"b_{b['id']}")
        elif t == "text":
            vals["text"] = st.text_area(spec["q"], height=120)
        submitted = st.form_submit_button("تحقق من نتيجتي", type="primary")
    if submitted:
        ok, level, msg = evaluate(spec, vals)
        if ok:
            ev = {k: v for k, v in vals.items() if v is not None}
            complete_block(p, b, level, ev)
            if t == "text" and vals.get("text"):
                bs["note"] = vals["text"]
            save()
            st.success(msg)
        else:
            bs["attempts"] += 1
            log_event("verify_fail", project=p["id"], block=b["id"])
            save()
            st.error(msg)

    # ── المساعدة والتشخيص ──
    with st.expander("تعثرت؟ شخّص المشكلة"):
        st.caption("كل سؤال يضيّق الاحتمالات. أجب بالترتيب.")
        resolved = True
        for qi, (q, advice) in enumerate(b["diag"]):
            ans = st.radio(q, ["لم أفحص", "نعم", "لا"], horizontal=True, key=f"dg_{p['id']}_{b['id']}_{qi}")
            if ans == "لم أفحص":
                resolved = False
                break
            if ans == "لا":
                st.markdown(f'<div class="lb-card"><b>جرّب هذا:</b> {esc(advice)}</div>', unsafe_allow_html=True)
                resolved = False
                break
        if resolved:
            st.info("تجاوزت الفحوص الأساسية. أعد التحقق، وإن بقي التعثر فاطلب مرشدًا.")
        c1, c2 = st.columns(2)
        if c1.button("سجّلت تشخيصًا", key=f"dgn_{b['id']}"):
            bs["diagnosed"] += 1
            log_event("diagnosis", project=p["id"], block=b["id"])
            save()
            st.toast("سُجّل التشخيص.")
        if c2.button("أصلحت المشكلة", key=f"fix_{b['id']}"):
            if bs["diagnosed"] and award("fix", 15, f"أصلح مشكلة موثقة: {b['name']}", f"fix:{p['id']}:{b['id']}"):
                bs["fixed"] += 1
                log_event("fix", project=p["id"], block=b["id"])
                save()
                st.success("شجاعة الإصلاح: واجهت الخطأ ووصلت إلى حله.")
            elif not bs["diagnosed"]:
                st.warning("سجّل التشخيص أولًا حتى يوثَّق الإصلاح.")
        msg = st.text_input("اطلب مساعدة المرشد (اختياري)", key=f"hm_{b['id']}", placeholder="ماذا ظهر لك بالضبط؟")
        if st.button("أرسل الطلب", key=f"hs_{b['id']}") and msg.strip():
            d["team"]["help"].append(dict(ts=now_iso(), project=p["id"], block=b["id"], msg=msg.strip(), open=True, who=d["profile"].get("name") or "—"))
            bs["helps"] += 1
            log_event("help", project=p["id"], block=b["id"])
            save()
            st.toast("أُرسل الطلب.")

    # ── دفتر الرحلة (القسم 7.7) ──
    with st.expander("دفتر الرحلة"):
        with st.form(f"nb_{b['id']}"):
            tried = st.text_input("ماذا جرّبت؟")
            failed = st.text_input("ماذا فشل؟")
            changed = st.text_input("ماذا غيّرت؟")
            learned = st.text_input("ما الذي فهمته؟")
            alt = st.checkbox("جرّبت بديلًا أو فرضية مختلفة")
            if st.form_submit_button("احفظ الملاحظة") and any([tried, failed, changed, learned]):
                d["notebook"].append(dict(ts=now_iso(), project=p["id"], block=b["id"], tried=tried, failed=failed, changed=changed, learned=learned))
                award("try", 3, f"ملاحظة تعلّم: {b['name']}", f"note:{p['id']}:{b['id']}")
                if alt:
                    award("try", 8, f"جرّب بديلًا: {b['name']}", f"alt:{p['id']}:{b['id']}")
                save()
                st.toast("حُفظت الملاحظة.")

    # ── انتقل ──
    if bs["level"] >= 1:
        st.markdown('<div class="lb-card primary"><b>أنجزت هذه اللبنة. الخطوة التالية تعتمد على ما بنيته الآن.</b></div>', unsafe_allow_html=True)
        nxt = idx + 1
        if nxt < len(p["blocks"]):
            if st.button("انتقل إلى اللبنة التالية", type="primary"):
                d["active"].update(project=p["id"], block=p["blocks"][nxt]["id"])
                save()
                st.rerun()
        else:
            st.success("وصلت إلى نهاية المسار. افتح جواز لَبنَة لتجهّز بطاقة العرض.")


# ════════════════════════════════════════════════════════════════════════════
# 11) صفحة: المسح
# ════════════════════════════════════════════════════════════════════════════
TOOL_STATUS = {
    "suggested": "مقترحة (من الصورة — لم تؤكد)",
    "confirmed": "أكدها المستخدم",
    "documented": "طراز موثق",
}


def page_scan() -> None:
    d = db()
    st.markdown("# المسح")
    st.markdown('<div class="lb-card"><b>تنبيه مهم:</b> التعرف البصري اقتراح فقط. تأكيدك للاسم والطراز لا يثبت أن القطعة تعمل أو أن التوصيل آمن.</div>',
                unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["صوّر أو ارفع صورة", "أضف يدويًا", "ابنِ بما لديك"])

    with t1:
        img = st.camera_input("التقط صورة للقطع") or st.file_uploader("أو ارفع صورة", type=["png", "jpg", "jpeg", "webp"])
        if img is not None:
            st.image(img, width=320)
            if st.button("اقترح تعرّفًا"):
                data = img.getvalue()
                mt = getattr(img, "type", None) or "image/jpeg"
                obj, err = llm_json(SYS_VISION, "ما القطع الظاهرة؟", (data, mt))
                if isinstance(obj, list):
                    st.session_state["scan_suggestions"] = obj
                else:
                    st.session_state["scan_suggestions"] = []
                    st.info(err or "لم يُرجع محرك التعرف نتيجة. أضف القطعة يدويًا.")
        for i, s in enumerate(st.session_state.get("scan_suggestions", [])):
            if not isinstance(s, dict):
                continue
            conf = float(s.get("confidence", 0) or 0)
            st.markdown(f'{tag("اقتراح", "acc")} **{esc(s.get("name", "؟"))}** — الفئة: {esc(s.get("category", "؟"))} — الثقة {conf:.0%}'
                        + (" — **يحتاج مراجعة**" if s.get("needs_review", True) or conf < 0.7 else ""), unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            model = c1.text_input("الطراز المكتوب على القطعة (إن وُجد)", key=f"sm_{i}")
            if c2.button("أؤكد", key=f"sc_{i}"):
                cat = next((k for k, v in CATALOG.items() if v["name"] in str(s.get("name", "")) or str(s.get("category", "")) in v["name"]), "other")
                d["tools"][f"scan_{i}_{int(time.time())}"] = dict(cat=cat, name=str(s.get("name", "قطعة")), model=model.strip(),
                                                                  count=1, status="confirmed", source="scan")
                save()
                st.toast("أُضيفت بعد تأكيدك.")

    with t2:
        with st.form("manual_tool"):
            c1, c2, c3 = st.columns([2, 2, 1])
            cat = c1.selectbox("الفئة", list(CATALOG), format_func=lambda k: CATALOG[k]["name"])
            model = c2.text_input("الطراز (اختياري)")
            cnt = c3.number_input("العدد", 1, 99, 1)
            if st.form_submit_button("أضف القطعة", type="primary"):
                d["tools"][f"manual_{cat}_{int(time.time())}"] = dict(cat=cat, name=CATALOG[cat]["name"], model=model.strip(),
                                                                     count=int(cnt), status="documented" if model.strip() else "confirmed", source="manual")
                save()
                st.rerun()
        if d["tools"]:
            st.markdown("**أدواتي**")
            for k, t in list(d["tools"].items()):
                c1, c2 = st.columns([6, 1])
                c1.markdown(f'{esc(t["name"])} × {t["count"]} {tag(TOOL_STATUS.get(t["status"], t["status"]), "ok" if t["status"] == "documented" else "")}'
                            f'{(" — " + esc(t["model"])) if t["model"] else ""}', unsafe_allow_html=True)
                if c2.button("حذف", key=f"rm_{k}"):
                    d["tools"].pop(k)
                    save()
                    st.rerun()
        else:
            st.info("لا أدوات بعد. أضف أول قطعة لتعرف ما يمكنك بناؤه.")

    with t3:
        st.caption("الحالات: متوفر · متوفر لكن يحتاج تحققًا من الطراز · ناقص · يوجد بديل معتمد · غير معروف.")
        for p in all_projects().values():
            if not p["tools"]:
                continue
            st.markdown(f"**{p['title']}**")
            for need in p["tools"]:
                key, note = availability(d, need)
                label, kind = AVAIL[key]
                st.markdown(f'{tag(label, kind)} {esc(CATALOG[need]["name"])} <span class="lb-muted">{esc(note)}</span>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 12) صفحة: جواز لَبنَة
# ════════════════════════════════════════════════════════════════════════════
def passport_summary() -> dict[str, Any]:
    d = db()
    projects = all_projects()
    skills: dict[str, dict[str, int]] = {s: {"n": 0, "max": 0} for s in SKILLS}
    for s in d["stamps"]:
        row = skills.setdefault(s["skill"], {"n": 0, "max": 0})
        row["n"] += 1
        row["max"] = max(row["max"], s["level"])
    done_projects = [p for p in projects.values() if pstate(p["id"])["started_at"] and ready_for_showcase(p)]
    return dict(skills=skills, done=done_projects)


def public_card_html(project: dict) -> str:
    d = db()
    sh = d["share"]
    t = get_tokens(False)
    rows = []
    for b in project["blocks"]:
        lv = block_level(project["id"], b["id"])
        if lv:
            rows.append(f'<li>{esc(b["name"])} — {esc(b["stamp"])}' + (f' <small>({LEVELS[lv]})</small>' if sh["show_evidence"] else "") + "</li>")
    notes = ""
    if sh["show_notes"]:
        n = [x for x in d["notebook"] if x["project"] == project["id"]]
        notes = "<h3>دفتر الرحلة</h3>" + "".join(f'<p>{esc(x["learned"] or x["tried"])}</p>' for x in n if (x["learned"] or x["tried"]))
    who = f'<p>{esc(d["profile"].get("name"))}</p>' if sh["show_name"] and d["profile"].get("name") else ""
    return (f'<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>{esc(project["title"])} — لَبنَة</title>'
            f'<style>body{{font-family:system-ui,sans-serif;background:{t["bg"]};color:{t["ink"]};max-width:46rem;margin:2rem auto;padding:0 1rem;line-height:1.9}}'
            f'h1,h3{{color:{t["primary"]}}}li{{margin:.3rem 0}}</style>'
            f'<h1>{esc(project["title"])}</h1>{who}<p>{esc(project["outcome"])}</p><h3>ما أُنجز</h3><ul>{"".join(rows)}</ul>{notes}'
            f'<p><small>{esc(project["risk"])}</small></p></html>')


def page_passport() -> None:
    d = db()
    st.markdown("# جواز لَبنَة")
    tot = points_total()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(score_label(), sum(tot.values()))
    for c, (k, lbl) in zip((c2, c3, c4), COURAGE.items()):
        c.metric(lbl, tot[k])
    tabs = st.tabs(["البداية", "البناء", "التشخيص", "الفريق", "العرض"])

    with tabs[0]:
        first = min((s["ts"] for s in d["stamps"]), default=None)
        if first:
            st.markdown(f"أول نتيجة لك كانت بتاريخ **{first[:10]}**.")
        else:
            st.info("لم تحصل على ختم بعد. أنجز أول لبنة وتحقق من نتيجتها.")
        st.markdown("**الأختام**")
        if d["stamps"]:
            projects = all_projects()
            for s in d["stamps"]:
                pt = projects.get(s["project"], {}).get("title", "")
                st.markdown(f'{tag(LEVELS[s["level"]], "ok" if s["level"] >= 2 else "acc")} **{esc(s["stamp"])}** — {esc(pt)} <span class="lb-muted">({esc(s["skill"])})</span>',
                            unsafe_allow_html=True)
    with tabs[1]:
        summ = passport_summary()
        for sk, row in summ["skills"].items():
            st.markdown(f"**{sk}** — {row['n']} ختمًا" + (f"، أعلى دليل: {LEVELS[row['max']]}" if row["n"] else " — لم تُمارس بعد"))
        st.markdown("**مستوى التقدم في كل مسار**")
        for p in all_projects().values():
            done, total = project_progress(p)
            st.progress(done / total if total else 0, text=f"{p['title']}: {done}/{total}")
    with tabs[2]:
        rows = [(p_id, b_id, b) for p_id, p in d["projects"].items() for b_id, b in p["blocks"].items() if b["diagnosed"] or b["fixed"]]
        projects = all_projects()
        if not rows:
            st.info("لم تسجل تشخيصًا بعد. التعثر الموثّق جزء من التقدم لا سبب للانسحاب.")
        for p_id, b_id, b in rows:
            name = next((x["name"] for x in projects.get(p_id, {}).get("blocks", []) if x["id"] == b_id), b_id)
            st.markdown(f"- {name}: {b['diagnosed']} تشخيصًا، {b['fixed']} إصلاحًا")
    with tabs[3]:
        tm = d["team"]
        if tm["name"]:
            st.markdown(f"**{tm['name']}** — {len(tm['members'])} أعضاء")
            for c in tm["contrib"][-10:]:
                st.markdown(f"- {esc(c['member'])}: {esc(c['note'])}")
        else:
            st.info("لا فريق بعد. يفعّل المنظم غرفة الهاكثون.")
    with tabs[4]:
        sh = d["share"]
        c1, c2 = st.columns(2)
        sh["show_name"] = c1.toggle("إظهار اسمي", sh["show_name"])
        sh["show_notes"] = c1.toggle("إظهار دفتر الرحلة", sh["show_notes"])
        sh["show_evidence"] = c2.toggle("إظهار مستوى الدليل", sh["show_evidence"])
        started = [p for p in all_projects().values() if pstate(p["id"])["started_at"]]
        if not started:
            st.info("ابدأ مشروعًا لتظهر بطاقة العرض.")
        for p in started:
            ok = ready_for_showcase(p)
            st.markdown(f'**{p["title"]}** {tag("جاهزة للعرض", "ok") if ok else tag("لم تكتمل اللبنات الأساسية", "acc")}', unsafe_allow_html=True)
            st.download_button("نزّل بطاقة العرض (HTML)", public_card_html(p), file_name=f"labna_{p['id']}.html", mime="text/html", key=f"dl_{p['id']}")
        st.caption("الصفحة العامة تحتوي فقط ما فعّلته أعلاه.")
        save()


# ════════════════════════════════════════════════════════════════════════════
# 13) وضع المنظم: غرفة الهاكثون، فكّك فكرتي، المؤشرات
# ════════════════════════════════════════════════════════════════════════════
def page_organizer() -> None:
    d = db()
    st.markdown("# غرفة الهاكثون")
    tm = d["team"]
    t1, t2, t3, t4 = st.tabs(["الفريق والتقدم", "فكّك فكرتي", "المراجعة والمساعدة", "مؤشرات القياس"])

    with t1:
        with st.form("team"):
            tm["name"] = st.text_input("اسم الفريق", tm["name"])
            projects = all_projects()
            pids = list(projects)
            tm["project"] = st.selectbox("التحدي/المسار", pids, index=pids.index(tm["project"]) if tm["project"] in pids else 0,
                                         format_func=lambda k: projects[k]["title"])
            c1, c2 = st.columns(2)
            mname = c1.text_input("عضو جديد")
            mrole = c2.text_input("الدور (مثال: توصيل، برمجة، اختبار)")
            if st.form_submit_button("حفظ / إضافة عضو", type="primary"):
                if mname.strip():
                    tm["members"].append(dict(name=mname.strip(), role=mrole.strip() or "عضو"))
                save()
                st.rerun()
        if tm["members"]:
            st.markdown("**الأعضاء:** " + "، ".join(f"{m['name']} ({m['role']})" for m in tm["members"]))
        if tm["project"]:
            p = projects[tm["project"]]
            st.markdown("**خريطة الاعتماد والتقدم**")
            st.graphviz_chart(graph_dot(p), use_container_width=True)
            dependents = {b["id"]: 0 for b in p["blocks"]}
            for i in range(len(p["blocks"])):
                for dep in block_deps(p, i):
                    dependents[dep] = dependents.get(dep, 0) + 1
            crit = sorted([b for b in p["blocks"] if block_level(p["id"], b["id"]) < 2 and dependents[b["id"]]],
                          key=lambda b: -dependents[b["id"]])[:3]
            if crit:
                st.warning("اللبنات الحرجة: " + "، ".join(f"{b['name']} (تعتمد عليها {dependents[b['id']]})" for b in crit))
            if tm["members"]:
                with st.form("contrib"):
                    who = st.selectbox("العضو", [m["name"] for m in tm["members"]])
                    blk_sel = st.selectbox("اللبنة", [b["id"] for b in p["blocks"]], format_func=lambda i: next(b["name"] for b in p["blocks"] if b["id"] == i))
                    note = st.text_input("المساهمة")
                    if st.form_submit_button("سجّل مساهمة") and note.strip():
                        tm["contrib"].append(dict(ts=now_iso(), member=who, block=blk_sel, project=p["id"], note=note.strip()))
                        save()
                        st.rerun()
            for c in tm["contrib"][-8:]:
                st.markdown(f"- `{c['ts'][:16]}` **{esc(c['member'])}**: {esc(c['note'])}")
            ready = ready_for_showcase(p)
            st.markdown(f"حالة التسليم: {tag('جاهز للعرض', 'ok') if ready else tag('لم تكتمل اللبنات الأساسية بالدليل', 'acc')}", unsafe_allow_html=True)
            st.download_button("نزّل جواز الفريق (JSON)", json.dumps(dict(team=tm, project=p["title"], stamps=d["stamps"],
                               notebook=[n for n in d["notebook"] if n["project"] == p["id"]]), ensure_ascii=False, indent=1),
                               file_name="team_passport.json", mime="application/json")
            st.caption("التقييم يعتمد على رحلة البناء: لبنات متحقق منها، دفتر الرحلة، تشخيصات، مساهمات الأعضاء — لا العرض النهائي وحده.")

    with t2:
        st.caption("الذكاء الاصطناعي هنا ينظّم الفكرة ويقلل رهبة البداية؛ لا يخترع دوائر ولا كودًا ولا أحكام سلامة.")
        idea = st.text_area("اكتب فكرتك بلغة طبيعية", placeholder="مثال: أريد جهازًا ينبه كبار السن عند ترك الغاز مفتوحًا", height=90)
        if st.button("فكّك فكرتي", type="primary") and idea.strip():
            d["drafts"].append(decompose_idea(idea.strip()))
            save()
        for i, dr in enumerate(reversed(d["drafts"])):
            real = len(d["drafts"]) - 1 - i
            with st.expander(f"{dr['idea'][:70]} — {dr['status']}", expanded=(i == 0)):
                for k, lbl in (("problem", "المشكلة"), ("beneficiary", "المستفيد"), ("outcome", "النتيجة المطلوبة"), ("v1", "نسخة أولى صغيرة")):
                    if dr.get(k):
                        st.markdown(f"**{lbl}:** {dr[k]}")
                st.markdown("**اللبنات المقترحة:** " + "، ".join(map(str, dr["blocks"])))
                if dr["tools"]:
                    st.markdown("**الأدوات المحتملة:** " + "، ".join(map(str, dr["tools"])))
                for r in dr["risks"]:
                    st.markdown(f'<div class="lb-safety"><strong>⚠ مخاطر:</strong> {esc(r)}</div>', unsafe_allow_html=True)
                st.markdown("**أسئلة مفتوحة:** " + "، ".join(map(str, dr["questions"])))
                if dr.get("llm_note"):
                    st.caption(dr["llm_note"])
                if dr.get("related"):
                    st.caption(f"قريب من مشروع قائم: {all_projects()[dr['related']]['title']}")
                if st.button("اعتماد كمسار رسمي (مراجعة المنظم)", key=f"ap_{real}"):
                    proj = draft_to_project(dr)
                    d["custom_projects"][proj["id"]] = proj
                    dr["status"] = "معتمدة"
                    log_event("draft_approved", project=proj["id"])
                    save()
                    st.rerun()

    with t3:
        st.markdown("**طلبات المساعدة**")
        projects = all_projects()
        open_help = [h for h in tm["help"] if h["open"]]
        if not open_help:
            st.info("لا طلبات مفتوحة.")
        for i, h in enumerate(tm["help"]):
            if not h["open"]:
                continue
            bn = next((b["name"] for b in projects.get(h["project"], {}).get("blocks", []) if b["id"] == h["block"]), h["block"])
            st.markdown(f"- **{esc(h['who'])}** في «{esc(bn)}»: {esc(h['msg'])}")
            if st.button("تم الرد", key=f"hd_{i}"):
                h["open"] = False
                save()
                st.rerun()
        st.markdown("**مراجعة الأدلة → «راجعتها»**")
        reviewer = st.text_input("اسم المراجع", key="rev_name")
        for pid, ps in d["projects"].items():
            p = projects.get(pid)
            if not p:
                continue
            for b in p["blocks"]:
                bs = ps["blocks"].get(b["id"])
                if bs and 1 <= bs["level"] < 3:
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"{p['title']} — {b['name']} ({LEVELS[bs['level']]})")
                    if c2.button("اعتمد", key=f"rv_{pid}_{b['id']}") and reviewer.strip():
                        bs["level"] = 3
                        bs["reviewer"] = reviewer.strip()
                        grant_stamp(p, b, 3)
                        tm["reviews"].append(dict(ts=now_iso(), project=pid, block=b["id"], reviewer=reviewer.strip()))
                        save()
                        st.rerun()

    with t4:
        ev = d["events"]
        starts = [e for e in ev if e["kind"] == "project_start"]
        dones = [e for e in ev if e["kind"] == "block_done"]
        fails = [e for e in ev if e["kind"] == "verify_fail"]
        helps = [e for e in ev if e["kind"] == "help"]
        diag = [e for e in ev if e["kind"] == "diagnosis"]
        fixes = [e for e in ev if e["kind"] == "fix"]
        ttf = None
        if starts and dones:
            t0 = datetime.fromisoformat(starts[0]["ts"])
            t1_ = next((datetime.fromisoformat(e["ts"]) for e in dones if e["level"] >= 2), None)
            ttf = int((t1_ - t0).total_seconds() // 60) if t1_ else None
        verified = sum(1 for pr in d["projects"].values() for b in pr["blocks"].values() if b["level"] >= 2)
        completed = sum(1 for pr in d["projects"].values() for b in pr["blocks"].values() if b["level"] >= 1)
        m1, m2, m3 = st.columns(3)
        m1.metric("الزمن حتى أول إنجاز متحقق (دقيقة)", ttf if ttf is not None else "—")
        m2.metric("نسبة التحقق الفعلي من المكتمل", f"{verified / completed:.0%}" if completed else "—")
        m3.metric("طلبات المساعدة", len(helps))
        m4, m5, m6 = st.columns(3)
        m4.metric("محاولات تحقق فاشلة", len(fails))
        m5.metric("تعثر انتهى بإصلاح", f"{len(fixes)}/{len(diag)}" if diag else "—")
        m6.metric("مشاريع بدأت", len(starts))
        by_block: dict[str, int] = {}
        for e in fails + helps + diag:
            by_block[e.get("block", "?")] = by_block.get(e.get("block", "?"), 0) + 1
        if by_block:
            names = {b["id"]: b["name"] for p in all_projects().values() for b in p["blocks"]}
            st.markdown("**أكثر اللبنات تسببًا في التعثر**")
            for bid, n in sorted(by_block.items(), key=lambda x: -x[1])[:5]:
                st.markdown(f"- {names.get(bid, bid)}: {n}")


# ════════════════════════════════════════════════════════════════════════════
# 14) وضع المطوّر: مختبر التصميم (taste-skill · impeccable · designlang)
# ════════════════════════════════════════════════════════════════════════════
def page_design_lab() -> None:
    d = db()
    st.markdown("# مختبر التصميم")
    env = node_env()
    st.caption(f"Node: {env['node'] or 'غير موجود'} · npx: {env['npx'] or 'غير موجود'}. الأدوات الثلاث مكتوبة بـ Node؛ التطبيق يستدعيها كعمليات خارجية ويعمل بدونها.")
    tabs = st.tabs(["نظام التصميم (taste-skill)", "مدقق impeccable", "استخراج designlang", "تدقيق ذاتي"])

    with tabs[0]:
        st.markdown("**taste-skill** يفرض نظام تصميم واحدًا: لوحة ألوان ومزاوجة خطوط تُختار لنوع المنتج، حواف متساوية، ومشهد واحد لكل شاشة. "
                    "هنا تُطبَّق هذه المبادئ عبر «مكتبة ألوان» ورموز موحدة.")
        names = list(PALETTES)
        d["palette"] = st.radio("لوحة الألوان", names, index=names.index(d["palette"]) if d["palette"] in names else 0, horizontal=True)
        d["dark_mode"] = st.toggle("الوضع الداكن", d["dark_mode"], key="dm_lab")
        if d["theme_override"]:
            st.info("تُطبَّق حاليًا رموز مستخرجة من designlang.")
            if st.button("أعد الرموز الافتراضية"):
                d["theme_override"] = {}
                save()
                st.rerun()
        t = get_tokens()
        st.markdown("".join(f'<span class="lb-tag" style="background:{v};color:{t["ink"] if k in ("bg","surface","soft","line") else t["on_primary"]}">{k} {v}</span> ' for k, v in t.items()),
                    unsafe_allow_html=True)
        st.markdown(f"**الخطوط:** عرض «{TYPE_PAIR['display']}» + نص «{TYPE_PAIR['body']}».")
        st.code("# لاستخدام المهارة الأصلية مع وكيل برمجة (Node 22+ وChrome)\n"
                'npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"', language="bash")
        save()

    with tabs[1]:
        st.markdown("**impeccable** كاشف حتمي (62 قاعدة، بلا LLM) يلتقط علامات التصميم «الآلي» ومشكلات التباين. نمرّر له لقطة CSS التطبيق أو رابطًا حيًا.")
        mode = st.radio("الهدف", ["لقطة CSS للتطبيق", "رابط حي"], horizontal=True)
        url = ""
        if mode == "رابط حي":
            url = st.text_input("الرابط", "http://localhost:8501")
        if st.button("شغّل الفحص", type="primary"):
            with st.spinner("يعمل impeccable …"):
                if mode == "لقطة CSS للتطبيق":
                    tmp = Path(tempfile.mkdtemp(prefix="labna_snap_"))
                    (tmp / "index.html").write_text(
                        f'<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><style>{build_css(get_tokens())}</style>'
                        f'<body><main class="block-container"><h1>لَبنَة</h1><p>لقطة للفحص</p>'
                        f'<div class="lb-card"><h3>بطاقة</h3><p>نص</p></div></main></body></html>', encoding="utf-8")
                    res = impeccable_detect(str(tmp))
                else:
                    u = safe_url(url)
                    res = impeccable_detect(u) if u else {"ok": False, "error": "رابط غير صالح (http/https فقط)."}
            st.session_state["imp_res"] = res
        res = st.session_state.get("imp_res")
        if res:
            if res.get("error"):
                st.error(res["error"])
            else:
                st.markdown(f"رمز الخروج: `{res['rc']}` (2 = وُجدت ملاحظات، 1 = تعذّر الفحص).")
                if res["findings"]:
                    for f in res["findings"][:50]:
                        st.markdown(f"- **{esc(f.get('rule') or f.get('id') or '؟')}** — {esc(f.get('message') or f.get('description') or f)}")
                elif res["ok"]:
                    st.success("لا ملاحظات.")
                if res.get("err"):
                    with st.expander("سجل الأخطاء"):
                        st.code(res["err"][-3000:])
                with st.expander("الناتج الخام"):
                    st.code(res["raw"][-6000:] or "(فارغ)")

    with tabs[2]:
        st.markdown("**designlang** يفتح الرابط في متصفح مُدار ويستخرج رموز التصميم (DTCG) وتباين WCAG. نستورد الألوان فقط بعد فحص AA ونرفض ما يكسر القراءة.")
        url = st.text_input("موقع مرجعي", "https://example.com", key="dl_url")
        sysc = st.checkbox("استخدم Chrome المثبّت (--system-chrome)", value=True)
        if st.button("استخرج الرموز", type="primary"):
            u = safe_url(url)
            if not u:
                st.error("رابط غير صالح (http/https فقط).")
            else:
                out = tempfile.mkdtemp(prefix="labna_dl_")
                with st.spinner("يقرأ designlang الصفحة … قد يستغرق دقائق"):
                    st.session_state["dl_res"] = designlang_extract(u, out, sysc)
        r = st.session_state.get("dl_res")
        if r:
            if r.get("error"):
                st.error(r["error"])
            elif not r["ok"]:
                st.error("لم تُنتج الأداة ملف رموز.")
                st.code((r["err"] or r["out"])[-3000:])
                st.caption("جرّب: npx designlang install-browser")
            else:
                st.success(f"استُخرجت الرموز ({len(r['files'])} ملفًا).")
                over, notes = dtcg_to_overrides(r["tokens"], get_tokens())
                for n in notes:
                    st.markdown(f"- {n}")
                if over:
                    st.json(over)
                    if st.button("طبّق على لَبنَة"):
                        d["theme_override"] = over
                        save()
                        st.rerun()
                if r["language_md"]:
                    with st.expander("لغة التصميم (مقتطف)"):
                        st.markdown(r["language_md"])

    with tabs[3]:
        css = build_css(get_tokens())
        res = local_design_audit(get_tokens(), css)
        bad = [x for x in res if x["status"] == "FAIL"]
        st.markdown(f"**النتيجة:** {len(res) - len(bad)}/{len(res)} ناجحة")
        for x in res:
            icon = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[x["status"]]
            st.markdown(f"`{icon} {x['status']}` **{x['rule']}** — {x['msg']}")
        st.caption("قواعد ذاتية مستوحاة من المبادئ ولا تُغني عن كاشف impeccable.")


# ════════════════════════════════════════════════════════════════════════════
# 15) الشريط الجانبي والتشغيل
# ════════════════════════════════════════════════════════════════════════════
def sidebar() -> tuple[bool, bool]:
    d = db()
    with st.sidebar:
        st.markdown(f"## {APP_NAME}")
        st.caption("ابدأ بلبنة، وتحقق من نتيجتك، ثم انتقل بثقة.")
        d["profile"]["name"] = st.text_input("اسمك", d["profile"].get("name", ""))
        d["formal_mode"] = st.toggle("وضع رسمي (رصيد التقدم)", d["formal_mode"])
        d["dark_mode"] = st.toggle("الوضع الداكن", d["dark_mode"], key="dm_side")
        st.divider()
        org = st.toggle("وضع المنظم", False, help="غرفة الهاكثون، فكّك فكرتي، المراجعة، المؤشرات")
        dev = st.toggle("وضع المطوّر", False, help="مختبر التصميم")
        with st.expander("عن لَبنَة"):
            st.markdown(
                "منصة تنفيذ وقياس جاهزية للمشاريع التقنية: تفكك الفكرة إلى لبنات صغيرة تربط التركيب والتوصيل بالبرمجة والتحقق، "
                "وتسجل الرحلة في جواز قابل للعرض.\n\n"
                "المواءمة مع المملكة لا تعني شراكة أو اعتمادًا من أي جهة.")
            for k, v in REFERENCES.items():
                st.markdown(f"- [{k}]({v})")
        with st.expander("البيانات"):
            st.download_button("نزّل بياناتي (JSON)", json.dumps(d, ensure_ascii=False, indent=1), file_name="labna_data.json", mime="application/json")
            if st.button("مسح كل بياناتي"):
                st.session_state["confirm_reset"] = True
            if st.session_state.get("confirm_reset"):
                st.warning("سيُحذف كل شيء نهائيًا.")
                if st.button("نعم، امسح"):
                    st.session_state["db"] = new_db()
                    st.session_state.pop("confirm_reset", None)
                    save()
                    st.rerun()
    save()
    return org, dev


def main() -> None:
    st.set_page_config(page_title=f"{APP_NAME} — من فكرة كبيرة إلى مشروع يعمل", page_icon="🧱", layout="wide")
    db()
    org, dev = sidebar()
    inject_css()

    if st.session_state.get("_goto"):
        st.session_state["nav"] = st.session_state.pop("_goto")

    pages = list(NAV) + (["غرفة الهاكثون"] if org else []) + (["مختبر التصميم"] if dev else [])
    if st.session_state.get("nav") not in pages:
        st.session_state["nav"] = NAV[0]
    page = st.radio("القسم", pages, horizontal=True, key="nav", label_visibility="collapsed")
    st.divider()

    {
        "مساري": page_path,
        "المشاريع": page_projects,
        "المسح": page_scan,
        "جواز لَبنَة": page_passport,
        "غرفة الهاكثون": page_organizer,
        "مختبر التصميم": page_design_lab,
    }[page]()


if __name__ == "__main__":
    main()
