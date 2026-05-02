"""
智能土壤改良与农业问诊系统

运行：
    streamlit run app.py
"""

import json
import os
import re
import time
from io import BytesIO

import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# ============================================================================
# 1. 基础配置与全局样式
# ============================================================================

st.set_page_config(
    page_title="智能农业问诊与土壤改良决策引擎",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
:root {
    --bg: #f7f8f5;
    --bg-soft: #eff4ec;
    --card: rgba(255, 255, 255, 0.88);
    --card-strong: #ffffff;
    --border: rgba(46, 91, 68, 0.12);
    --text: #18251f;
    --muted: #66756d;
    --faint: #9aa69f;
    --primary: #2e8b57;
    --primary-dark: #1f6f43;
    --primary-soft: #e6f3eb;
    --earth: #a6784f;
    --earth-soft: #f3ede4;
    --warn: #d36b4c;
    --warn-soft: #fff0eb;
    --shadow: 0 18px 46px rgba(34, 60, 45, 0.09);
    --shadow-soft: 0 8px 24px rgba(34, 60, 45, 0.06);
}

div[data-testid="stDecoration"] {
    display: none;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem;
}

header[data-testid="stHeader"]::before {
    display: none;
}

/* ===== 全局强制深色文字，解决手机白底白字 ===== */
.stApp, .stApp *, .stApp label, .stApp span, .stApp p,
div[data-testid="stMarkdown"] p,
div[data-testid="stText"],
.st-bd, .st-c0, .st-c1, .st-c2, .st-c3,
[data-testid="stSidebar"] *,
[data-testid="stSelectbox"] *,
[data-testid="stSelectbox"] div,
[data-testid="stSelectbox"] label,
[data-baseweb="select"] *,
[data-baseweb="select"] span,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea, select,
.stButton button, .stDownloadButton button,
div[role="radiogroup"] label,
div[role="radiogroup"] label * {
    color: #1a2a20 !important;
}

/* 输入框背景加深一点 */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea,
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #1a2a20 !important;
}

/* 侧边栏选中项文字加粗 */
div[data-testid="stSidebarContent"] label[data-baseweb="radio"]:has(input:checked) * {
    color: #1f6f43 !important;
    font-weight: 800 !important;
}

div[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
    border: 1px solid rgba(46, 91, 68, .14);
    border-radius: 12px;
    background: rgba(255, 255, 255, .88);
    box-shadow: 0 10px 28px rgba(34, 60, 45, .12);
    backdrop-filter: blur(16px);
}

[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapsedControl"] * {
    pointer-events: auto !important;
}

.stApp {
    background: linear-gradient(180deg, #ffffff 0%, var(--bg) 52%, #eef4ed 100%);
    color: var(--text);
}

.block-container {
    max-width: 1160px;
    padding: 22px 34px 56px;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(23, 35, 29, .08);
}

[data-testid="stSidebarContent"] {
    background: rgba(255, 255, 255, .80);
    backdrop-filter: blur(18px);
    padding: 0px 12px 6px;
    margin-top: -10px;
}

[data-testid="stSidebarContent"] [data-testid="stVerticalBlock"],
[data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] > div,
[data-testid="stSidebarContent"] [data-testid="element-container"] {
    width: 100%;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 4px 14px;
    border-bottom: 1px solid rgba(23, 35, 29, .08);
    margin-bottom: 12px;
}

.brand-logo {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2e8b57, #6ea384);
    color: white;
    font-weight: 850;
    box-shadow: 0 12px 28px rgba(46, 139, 87, .24);
}

.brand-title {
    color: var(--text);
    font-weight: 820;
    line-height: 1.28;
}

.brand-subtitle {
    color: var(--muted);
    font-size: .74rem;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-top: 3px;
}

.nav-title {
    color: var(--muted);
    font-size: .74rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-weight: 800;
    margin: 18px 4px 8px;
}

div[data-testid="stSidebarContent"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
}

div[data-testid="stSidebarContent"] div[data-testid="stRadio"] {
    width: 100%;
}

div[data-testid="stSidebarContent"] div[data-testid="stRadio"] > div {
    width: 100%;
}

div[data-testid="stSidebarContent"] div[data-testid="stRadio"] label {
    width: 100%;
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"] {
    position: relative;
    width: 100%;
    box-sizing: border-box;
    min-height: 44px;
    display: flex;
    align-items: center;
    border: 1px solid transparent;
    border-radius: 12px;
    background: transparent;
    padding: 10px 12px 10px 14px;
    margin: 0;
    transition: background .18s ease, border-color .18s ease, transform .18s ease;
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"] > div:first-child {
    display: none;
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"]:hover {
    background: rgba(230, 243, 235, .62);
    border-color: rgba(46, 139, 87, .12);
    transform: translateX(2px);
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(90deg, rgba(230, 243, 235, .95), rgba(255, 255, 255, .74));
    border-color: rgba(46, 139, 87, .20);
    box-shadow: 0 8px 22px rgba(46, 139, 87, .08);
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"]:has(input:checked)::before {
    content: "";
    position: absolute;
    left: 0;
    top: 9px;
    bottom: 9px;
    width: 4px;
    border-radius: 0 999px 999px 0;
    background: var(--primary);
}

div[data-testid="stSidebarContent"] label[data-baseweb="radio"]:has(input:checked) * {
    color: var(--primary-dark) !important;
    font-weight: 800;
}

.hero {
    position: relative;
    overflow: hidden;
    text-align: center;
    min-height: 200px;
    border-radius: 20px;
    padding: 48px 28px 40px;
    margin: 12px 0 24px;
    background:
        linear-gradient(180deg, rgba(12, 28, 20, .22), rgba(12, 28, 20, .52)),
        url("https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=1800&q=85") center/cover no-repeat;
    box-shadow: var(--shadow);
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 13px;
    border: 1px solid rgba(46, 139, 87, .18);
    border-radius: 999px;
    background: rgba(255, 255, 255, .82);
    color: var(--primary-dark);
    font-size: .82rem;
    font-weight: 720;
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(14px);
}

.hero-title {
    margin: 10px auto 6px;
    max-width: 920px;
    font-size: clamp(1.4rem, 2.8vw, 2.4rem);
    line-height: 1.1;
    font-weight: 880;
    letter-spacing: 0;
    color: #ffffff;
    text-shadow: 0 10px 32px rgba(0, 0, 0, .26);
}

.hero-subtitle {
    max-width: 760px;
    margin: 0 auto;
    color: rgba(255, 255, 255, .88);
    font-size: 1.04rem;
    line-height: 1.72;
}

.section-head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 16px;
    margin: 26px 0 12px;
}

.section-kicker {
    color: var(--primary);
    font-size: .76rem;
    font-weight: 820;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.section-title {
    color: var(--text);
    font-size: 1.28rem;
    font-weight: 820;
}

.section-desc {
    color: var(--muted);
    font-size: .92rem;
}

.glass-card {
    border: 1px solid var(--border);
    border-radius: 22px;
    background: var(--card-strong);
    box-shadow: var(--shadow-soft);
    padding: 22px;
}

.card-title {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--text);
    font-size: 1.04rem;
    font-weight: 820;
    margin-bottom: 4px;
}

.card-icon {
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: var(--primary-soft);
    color: var(--primary-dark);
    font-size: 15px;
    flex: 0 0 auto;
}

.card-desc {
    color: var(--muted);
    font-size: .88rem;
    line-height: 1.55;
    margin-bottom: 16px;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
}

.metric-card {
    border: 1px solid var(--border);
    border-radius: 18px;
    background: var(--card-strong);
    padding: 15px;
    box-shadow: var(--shadow-soft);
}

.metric-label {
    color: var(--muted);
    font-size: .78rem;
    font-weight: 720;
}

.metric-value {
    margin-top: 7px;
    color: var(--text);
    font-size: 1.28rem;
    font-weight: 840;
}

.metric-pill {
    display: inline-flex;
    margin-top: 9px;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: .74rem;
    font-weight: 760;
}

.pill-ok { background: var(--primary-soft); color: var(--primary-dark); }
.pill-warn { background: var(--earth-soft); color: #8a6237; }
.pill-danger { background: var(--warn-soft); color: var(--warn); }

.insight-box {
    border: 1px solid rgba(46, 139, 87, .16);
    border-left: 5px solid var(--primary);
    border-radius: 18px;
    background: rgba(230, 243, 235, .72);
    padding: 16px 18px;
    color: #244236;
    line-height: 1.72;
    margin: 14px 0;
}

.prescription-card {
    border: 1px solid rgba(46, 139, 87, .16);
    border-radius: 28px;
    background: rgba(255, 255, 255, .84);
    box-shadow: var(--shadow);
    backdrop-filter: blur(22px);
    padding: 24px;
    margin-top: 14px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--border);
    border-radius: 22px;
    background: #ffffff;
    box-shadow: var(--shadow-soft);
}

.ai-loading {
    display: flex;
    align-items: center;
    gap: 14px;
    border: 1px solid rgba(46, 139, 87, .16);
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(230, 243, 235, .92), rgba(255,255,255,.92));
    padding: 18px 20px;
    color: var(--primary-dark);
    font-weight: 780;
    box-shadow: var(--shadow-soft);
    margin: 16px 0;
}

.ai-spinner {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 3px solid rgba(46, 139, 87, .18);
    border-top-color: var(--primary);
    animation: ai-spin 0.9s linear infinite;
}

.ai-pulse {
    color: var(--muted);
    font-weight: 560;
    font-size: .9rem;
    margin-top: 3px;
}

@keyframes ai-spin {
    to { transform: rotate(360deg); }
}

.report-title {
    color: var(--text);
    font-size: 1.34rem;
    font-weight: 860;
    margin-bottom: 8px;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 14px !important;
    min-height: 46px;
    font-weight: 780 !important;
    border: 1px solid rgba(46, 139, 87, .18) !important;
    box-shadow: 0 12px 26px rgba(34, 60, 45, .08);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), #5aa97d) !important;
    border: 0 !important;
}

div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea {
    border-radius: 14px !important;
    border-color: rgba(46, 91, 68, .16) !important;
    background: rgba(255, 255, 255, .76) !important;
}

/* 下拉框箭头和整个下拉区域鼠标变小手 */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] [data-baseweb="select"] {
    cursor: pointer !important;
}

div[data-testid="stSelectbox"] [data-testid="stSelectbox"] {
    cursor: pointer !important;
}

div[data-testid="stSlider"] {
    padding-top: 4px;
}

table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    overflow: hidden;
    border-radius: 14px;
}

thead tr th {
    background: #edf7f1 !important;
    color: #1f6f43 !important;
}

tbody tr td {
    background: rgba(255, 255, 255, .76) !important;
}

/* ===== 移动端适配（手机 + 小平板） ===== */
@media (max-width: 900px) {
    .block-container { padding: 16px 14px !important; }
    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .hero { padding-top: 18px; min-height: 140px; padding: 28px 16px 24px; }
    .hero-title { font-size: 1.2rem !important; }
    .hero-subtitle { font-size: .88rem !important; }
    .brand-logo { width: 34px; height: 34px; font-size: 13px; }
    .brand-title { font-size: .82rem; }
}

@media (max-width: 640px) {
    .block-container { padding: 10px 10px 40px !important; }

    .metric-grid { grid-template-columns: 1fr; }

    .hero { padding: 20px 14px 18px; min-height: 120px; }
    .hero-title { font-size: 1.0rem !important; }
    .hero-subtitle { font-size: .78rem !important; }
    .hero-badge { font-size: .72rem; padding: 4px 10px; }

    div[data-testid="stSidebarContent"] label[data-baseweb="radio"] {
        min-height: 36px;
        padding: 7px 8px 7px 10px;
        font-size: .88rem;
    }

    .report-header { flex-direction: column; align-items: start; gap: 4px; }
    .report-header-left { flex-wrap: wrap; gap: 6px; }
    .report-crop { font-size: 1rem; }
    .section-head { flex-direction: column; gap: 4px; }

    .glass-card, .prescription-card { padding: 14px; }
    .metric-card { padding: 10px; }
    .metric-value { font-size: 1.0rem; }

    .stButton > button, .stDownloadButton > button {
        min-height: 38px;
        font-size: .88rem;
    }

    table { font-size: .78rem; }
    div[data-testid="stDataFrame"] { font-size: .78rem; }

    .brand { padding: 2px 4px 8px; margin-bottom: 6px; }
}

/* ===== 结果页 ===== */
.report-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 8px 0 0;
}

.report-header-left {
    display: flex;
    align-items: baseline;
    gap: 14px;
}

.report-crop {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text);
}

.report-meta {
    display: flex;
    align-items: center;
    gap: 10px;
}

.report-risk {
    display: inline-block;
    padding: 3px 10px;
    border-radius: var(--radius-pill);
    background: var(--primary-soft);
    color: var(--primary-dark);
    font-size: .76rem;
    font-weight: 700;
}

.report-date {
    color: var(--faint);
    font-size: .78rem;
}

/* ===== 加载页 ===== */
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: var(--bg);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 24px;
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin .8s linear infinite;
    margin-bottom: 28px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 8px;
}

.loading-crop {
    color: var(--muted);
    font-size: .92rem;
    margin-bottom: 28px;
}

.loading-steps {
    display: flex;
    gap: 24px;
    margin-bottom: 32px;
}

.loading-step {
    padding: 8px 18px;
    border-radius: 999px;
    font-size: .82rem;
    font-weight: 680;
    color: var(--faint);
    background: var(--bg-soft);
    border: 1px solid var(--border);
}

.loading-step.active {
    color: var(--primary-dark);
    background: var(--primary-soft);
    border-color: rgba(46,139,87,.2);
    animation: pulse-step 1.8s ease-in-out infinite;
}

@keyframes pulse-step {
    0%, 100% { opacity: .7; }
    50% { opacity: 1; }
}

.loading-hint {
    color: var(--faint);
    font-size: .82rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# 2. 数据配置
# ============================================================================

PROVIDER_URLS = {
    "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
    "OpenAI 兼容": "https://api.openai.com/v1/chat/completions",
    "通义千问": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "Moonshot": "https://api.moonshot.cn/v1/chat/completions",
    "硅基流动": "https://api.siliconflow.cn/v1/chat/completions",
}

PROVIDER_MODELS = {
    "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
    "OpenAI 兼容": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "通义千问": ["qwen-plus", "qwen-max", "qwen-turbo"],
    "Moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    "硅基流动": ["deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"],
}

CROP_PROFILES = {
    "茶树": {"ph": (4.5, 6.5), "organic": (1.5, 3.0), "n": (60, 120), "p": (10, 30), "k": (80, 150)},
    "水稻": {"ph": (5.5, 7.0), "organic": (2.0, 4.0), "n": (80, 150), "p": (10, 30), "k": (80, 160)},
    "小麦": {"ph": (6.0, 7.5), "organic": (1.5, 3.0), "n": (70, 140), "p": (10, 30), "k": (90, 180)},
    "玉米": {"ph": (6.0, 7.5), "organic": (2.0, 4.0), "n": (80, 160), "p": (15, 35), "k": (100, 200)},
    "番茄": {"ph": (6.0, 7.0), "organic": (2.5, 5.0), "n": (80, 180), "p": (20, 50), "k": (150, 300)},
    "其他作物": {"ph": (5.5, 7.5), "organic": (1.5, 4.0), "n": (60, 150), "p": (10, 40), "k": (80, 200)},
}

METRIC_NAMES = {
    "ph": ("土壤 pH", ""),
    "organic": ("有机质", "%"),
    "n": ("速效氮", "mg/kg"),
    "p": ("速效磷", "mg/kg"),
    "k": ("速效钾", "mg/kg"),
}


# ============================================================================
# 3. 工具函数
# ============================================================================

def init_state():
    defaults = {
        "provider": "DeepSeek",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "history": [],
        "api_key": os.getenv("DEEPSEEK_API_KEY", "") or os.getenv("API_KEY", ""),
        "saved_api_key": os.getenv("DEEPSEEK_API_KEY", "") or os.getenv("API_KEY", ""),
        "decision_view": "input",
        "is_loading": False,
        "latest_report": None,
        "latest_pdf_bytes": b"",
        "latest_filename_md": "",
        "latest_filename_pdf": "",
        "latest_crop": "",
        "latest_risk": "",
        "latest_risk_desc": "",
        "latest_timestamp": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def assess_value(value, low, high):
    if value < low:
        return "偏低", "pill-danger"
    if value > high:
        return "偏高", "pill-warn"
    return "适宜", "pill-ok"


def build_assessments(values, profile):
    return {key: assess_value(values[key], *profile[key]) for key in profile}


def risk_level(assessments):
    bad_count = sum(1 for status, _ in assessments.values() if status != "适宜")
    if bad_count == 0:
        return "低风险", "核心指标处于推荐区间"
    if bad_count <= 2:
        return "中风险", f"{bad_count} 项指标需要重点管理"
    return "高风险", f"{bad_count} 项指标偏离参考范围"


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="brand">
            <div class="brand-logo">农</div>
            <div>
                <div class="brand-title">智能土壤改良<br/>与农业问诊系统</div>
                <div class="brand-subtitle">Soil Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="nav-title">Navigation</div>', unsafe_allow_html=True)
    return st.sidebar.radio(
        "导航",
        ["决策系统", "历史记录", "API 配置"],
        label_visibility="collapsed",
        key="active_page",
    )


def render_hero():
    st.markdown(
        """
        <section class="hero">
            <h1 class="hero-title">AI 驱动的土壤改良专家</h1>
            <p class="hero-subtitle">
                输入地块数据，获取专属的智能改良方案。
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(kicker, title, desc=""):
    st.markdown(
        f"""
        <div class="section-head">
            <div>
                <div class="section-kicker">{kicker}</div>
                <div class="section-title">{title}</div>
            </div>
            <div class="section-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_config_page():
    st.markdown("### API 配置")
    st.caption("配置模型服务商、模型版本和 API Key，用于驱动农业智能分析。")

    render_section_header("MODEL SETTINGS", "模型与密钥", "API Key 仅保存在当前会话中")
    left, right = st.columns([1.25, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span class="card-icon">模</span>模型路由</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">选择兼容 OpenAI Chat Completions 格式的模型服务。</div>', unsafe_allow_html=True)
            provider = st.selectbox("模型服务商", list(PROVIDER_URLS.keys()), key="provider")
            models = PROVIDER_MODELS[provider]
            if st.session_state.model not in models:
                st.session_state.model = models[0]
            st.selectbox("模型", models, key="model")
            st.slider("创造性 Temperature", 0.0, 2.0, key="temperature", step=0.1)

    with right:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span class="card-icon">钥</span>访问凭据</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">推荐使用环境变量保存密钥；临时测试可在这里输入。</div>', unsafe_allow_html=True)
            st.text_input(
                "API Key",
                type="password",
                key="api_key_input",
                value=st.session_state.get("saved_api_key", ""),
                placeholder="sk-...",
            )
            if st.session_state.get("saved_api_key"):
                st.success("API Key 已就绪，可以返回决策系统生成分析。")
            else:
                st.warning("当前未配置 API Key。")
            st.caption("环境变量优先级：DEEPSEEK_API_KEY 或 API_KEY。页面输入不会写入本地文件。")

    if st.button("保存配置", type="primary", use_container_width=True):
        st.session_state.saved_api_key = st.session_state.get("api_key_input", "").strip()
        st.session_state.api_key = st.session_state.saved_api_key
        st.session_state.api_config_saved_at = time.strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"配置已保存到当前会话：{st.session_state.api_config_saved_at}")
        st.rerun()

    if st.session_state.get("api_config_saved_at"):
        st.caption(f"上次保存：{st.session_state.api_config_saved_at}")


def render_metric_cards(values, profile, assessments):
    cards = []
    for key, value in values.items():
        name, unit = METRIC_NAMES[key]
        low, high = profile[key]
        status, pill_class = assessments[key]
        unit_text = f" {unit}" if unit else ""
        cards.append(
            f"""
            <div class="metric-card">
                <div class="metric-label">{name}</div>
                <div class="metric-value">{value}{unit_text}</div>
                <div class="metric-pill {pill_class}">{status} · 参考 {low}-{high}{unit_text}</div>
            </div>
            """
        )
    st.markdown(f'<div class="metric-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def build_prompt(inputs, values, profile, assessments):
    # 把 None 统一替换成"未知"
    def _v(key):
        val = inputs.get(key)
        if val is None or val == "":
            return "未知"
        if isinstance(val, list):
            return "、".join(val) if val else "未知"
        return val

    assessment_lines = []
    for key, value in values.items():
        name, unit = METRIC_NAMES[key]
        low, high = profile[key]
        status, _ = assessments[key]
        unit_text = f" {unit}" if unit else ""
        assessment_lines.append(f"- {name}: {value}{unit_text}, 参考 {low}-{high}{unit_text}, 状态 {status}")

    return f"""
你是一位资深农业土壤专家、植物营养学家和田间农技顾问。请根据以下信息生成专业但易懂的土壤改良与农业问诊报告。

## 地块与环境
- 报告日期: {inputs["report_date"]}
- 地块编号: {_v("plot_id")}
- 作物: {_v("crop")}
- 地区: {_v("region")}
- 生育阶段: {_v("stage")}
- 种植面积: {inputs["area"]} 亩
- 灌溉方式: {_v("irrigation")}
- 土壤质地: {_v("texture")}
- 近期天气: {_v("weather")}
- 当前问题: {_v("issues")}
- 田间观察: {_v("observation")}

## 土壤指标
{chr(10).join(assessment_lines)}

请按以下结构输出：
1. 报告抬头：必须使用「报告日期：{inputs["report_date"]}」「地块编号：{_v("plot_id")}」「作物：{_v("crop")}（{_v("stage")}）」；不要使用示例日期，不要编造日期。
2. 核心结论：用一段话说明主要问题，例如土壤偏酸、肥力不足、结构板结等。
3. 改良步骤：用编号步骤给出 7 天、30 天、本季和长期养护计划。
4. 施肥/用药建议：用 Markdown 表格列出材料、每亩建议用量、施用时间、注意事项。
5. 科学机理：解释为什么这样改良。
6. 复检建议：列出建议复检指标和时间。

不要编造精确病害图像识别结论；不确定时给出保守范围并提醒结合当地农技标准。
""".strip()


def call_llm(prompt):
    api_key = st.session_state.get("saved_api_key") or st.session_state.get("api_key", "")
    response = requests.post(
        PROVIDER_URLS[st.session_state.provider],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "model": st.session_state.model,
            "messages": [
                {"role": "system", "content": "你是严谨、专业、实用的农业土壤改良专家。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": st.session_state.temperature,
            "max_tokens": 2400,
            "stream": True,
        },
        timeout=120,
        stream=True,
    )

    if response.status_code != 200:
        try:
            error_text = response.json()
        except ValueError:
            error_text = response.text[:500]
        raise RuntimeError(f"API 返回错误 {response.status_code}: {error_text}")

    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        data = line[6:].strip()
        if data == "[DONE]":
            break
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue
        choices = chunk.get("choices", [])
        if choices:
            content = choices[0].get("delta", {}).get("content", "")
            if content:
                yield content


def render_report(report):
    with st.container(border=True):
        st.markdown(report, unsafe_allow_html=True)


def clean_markdown_inline(text):
    """清理 Markdown 行内语法，并转换为 ReportLab 支持的简单 HTML。"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font face='STSong-Light'>\1</font>", text)
    return text


def is_markdown_table(lines, index):
    if index + 1 >= len(lines):
        return False
    current = lines[index].strip()
    separator = lines[index + 1].strip()
    return current.startswith("|") and current.endswith("|") and re.match(r"^\|[\s:\-\|]+\|$", separator)


def parse_markdown_table(lines, index):
    table_lines = []
    while index < len(lines):
        line = lines[index].strip()
        if not (line.startswith("|") and line.endswith("|")):
            break
        table_lines.append(line)
        index += 1

    rows = []
    for row_index, line in enumerate(table_lines):
        if row_index == 1 and re.match(r"^\|[\s:\-\|]+\|$", line):
            continue
        cells = [clean_markdown_inline(cell.strip()) for cell in line.strip("|").split("|")]
        rows.append(cells)
    return rows, index


def build_pdf_styles():
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    base = {
        "fontName": "STSong-Light",
        "leading": 17,
        "textColor": colors.HexColor("#17231d"),
        "alignment": TA_LEFT,
    }
    return {
        "title": ParagraphStyle("TitleCN", parent=styles["Title"], fontName="STSong-Light", fontSize=20, leading=26, textColor=colors.HexColor("#1f6f43"), spaceAfter=10),
        "meta": ParagraphStyle("MetaCN", parent=styles["Normal"], fontName="STSong-Light", fontSize=9, leading=13, textColor=colors.HexColor("#68756d"), spaceAfter=12),
        "h1": ParagraphStyle("H1CN", parent=styles["Heading1"], fontName="STSong-Light", fontSize=16, leading=22, textColor=colors.HexColor("#1f6f43"), spaceBefore=12, spaceAfter=8),
        "h2": ParagraphStyle("H2CN", parent=styles["Heading2"], fontName="STSong-Light", fontSize=14, leading=20, textColor=colors.HexColor("#2e8b57"), spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("H3CN", parent=styles["Heading3"], fontName="STSong-Light", fontSize=12, leading=18, textColor=colors.HexColor("#a6784f"), spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("BodyCN", parent=styles["BodyText"], fontSize=10.5, spaceAfter=6, **base),
        "bullet": ParagraphStyle("BulletCN", parent=styles["BodyText"], fontSize=10.5, leftIndent=14, firstLineIndent=-8, spaceAfter=4, **base),
        "cell": ParagraphStyle("CellCN", parent=styles["BodyText"], fontName="STSong-Light", fontSize=9, leading=13, textColor=colors.HexColor("#17231d")),
    }


def markdown_to_flowables(markdown_text, styles):
    flowables = []
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.strip()
        if not line:
            flowables.append(Spacer(1, 4))
            index += 1
            continue

        if is_markdown_table(lines, index):
            rows, index = parse_markdown_table(lines, index)
            if rows:
                table_data = [[Paragraph(cell, styles["cell"]) for cell in row] for row in rows]
                col_count = max(len(row) for row in rows)
                col_width = (A4[0] - 36 * mm) / max(col_count, 1)
                table = Table(table_data, colWidths=[col_width] * col_count, hAlign="LEFT", repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f3eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f6f43")),
                    ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cfdcd3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]))
                flowables.append(table)
                flowables.append(Spacer(1, 8))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            style_name = "h1" if level == 1 else "h2" if level == 2 else "h3"
            flowables.append(Paragraph(clean_markdown_inline(heading.group(2)), styles[style_name]))
            index += 1
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if bullet or ordered:
            item_text = clean_markdown_inline((bullet or ordered).group(1))
            marker = "•" if bullet else re.match(r"^(\d+)\.", line).group(1) + "."
            flowables.append(Paragraph(f"{marker} {item_text}", styles["bullet"]))
            index += 1
            continue

        flowables.append(Paragraph(clean_markdown_inline(line), styles["body"]))
        index += 1
    return flowables


def create_pdf_bytes(report, title="农业智能诊断书"):
    """使用 ReportLab 生成保留 Markdown 层级、列表与表格格式的 PDF。"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
    )
    styles = build_pdf_styles()
    flowables = [
        Paragraph(title, styles["title"]),
        Paragraph(f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}（北京时间）", styles["meta"]),
    ]
    flowables.extend(markdown_to_flowables(report, styles))
    doc.build(flowables)
    return buffer.getvalue()


# ============================================================================
# 4. 页面主体
# ============================================================================

def result_page():
    """结果页：展示 AI 分析报告，带返回按钮"""
    # 返回按钮（加载中和结果页都显示）
    if st.button("← 返回输入页", use_container_width=True):
        st.session_state.decision_view = "input"
        st.session_state.is_loading = False
        st.rerun()

    # ── 加载状态：调用 LLM ──
    if st.session_state.get("is_loading"):
        # 返回按钮放在最顶部
        if st.button("← 返回输入页"):
            st.session_state.decision_view = "input"
            st.session_state.is_loading = False
            st.rerun()

        crop = st.session_state.get("pending_crop", "—")
        risk = st.session_state.get("pending_risk", "—")
        prompt = st.session_state.get("pending_prompt", "")

        loading_placeholder = st.empty()

        def _loading_html(step):
            steps_html = ""
            for i, label in enumerate(["读取土壤指标", "匹配改良方案", "生成诊断报告"]):
                cls = "loading-step active" if i <= step else "loading-step"
                steps_html += f'<div class="{cls}">{label}</div>'
            return (
                '<div class="loading-screen">'
                '<div class="loading-spinner"></div>'
                f'<div class="loading-title">AI 正在分析</div>'
                f'<div class="loading-crop">{crop} · 风险评估：{risk}</div>'
                f'<div class="loading-steps">{steps_html}</div>'
                f'<div class="loading-hint">通常需要 10-30 秒，请耐心等待...</div>'
                '</div>'
            )

        # 阶段1
        loading_placeholder.markdown(_loading_html(0), unsafe_allow_html=True)
        time.sleep(0.6)

        # 阶段2
        loading_placeholder.markdown(_loading_html(1), unsafe_allow_html=True)
        try:
            result = ""
            for chunk in call_llm(prompt):
                result += chunk
        except Exception as exc:
            st.session_state.is_loading = False
            st.session_state.decision_view = "input"
            loading_placeholder.empty()
            st.error(f"模型调用失败：{exc}")
            return

        # 阶段3
        loading_placeholder.markdown(_loading_html(2), unsafe_allow_html=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        pdf_bytes = create_pdf_bytes(result, title=f"{crop}农业智能诊断书")
        time.sleep(0.5)

        loading_placeholder.empty()
        st.session_state.latest_report = result
        st.session_state.latest_crop = crop
        st.session_state.latest_risk = risk
        st.session_state.latest_risk_desc = st.session_state.get("pending_risk_desc", "")
        st.session_state.latest_timestamp = timestamp
        st.session_state.latest_filename_md = f"农业诊断书_{crop}_{timestamp}.md"
        st.session_state.latest_filename_pdf = f"农业诊断书_{crop}_{timestamp}.pdf"
        st.session_state.latest_pdf_bytes = pdf_bytes
        st.session_state.history.append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "crop": crop,
            "risk": risk,
            "report": result,
            "inputs": st.session_state.get("pending_inputs", {}),
            "values": st.session_state.get("pending_values", {}),
        })
        st.session_state.is_loading = False
        st.rerun()
        return

    # ── 正常结果页 ──
    if not st.session_state.get("latest_report"):
        st.info("暂无报告，请返回输入页进行分析。")
        return

    st.markdown(
        f"""
        <div class="report-header">
            <div class="report-header-left">
                <div class="report-crop">{st.session_state.get("latest_crop", "—")}</div>
                <div class="report-meta">
                    <span class="report-risk">风险：{st.session_state.get("latest_risk", "—")}</span>
                    <span class="report-date">{st.session_state.get("latest_timestamp", "—")}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    render_report(st.session_state.latest_report)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "下载诊断书 Markdown",
            st.session_state.latest_report,
            st.session_state.latest_filename_md,
            "text/markdown",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "下载诊断书 PDF",
            st.session_state.latest_pdf_bytes,
            st.session_state.latest_filename_pdf,
            "application/pdf",
            use_container_width=True,
        )


def history_page():
    st.markdown("### 历史诊断记录")
    st.caption(f"共 {len(st.session_state.history)} 条记录")

    if not st.session_state.history:
        st.info("暂无历史记录，请先在决策系统中生成报告。")
        return

    for idx, item in enumerate(reversed(st.session_state.history)):
        real_idx = len(st.session_state.history) - 1 - idx
        title = f"{item['time']}  |  {item['crop']}  |  风险：{item['risk']}"
        with st.expander(title):
            st.markdown(item["report"], unsafe_allow_html=True)
            file_time = item["time"].replace(":", "").replace(" ", "_")
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.download_button(
                    "下载 Markdown",
                    item["report"],
                    f"农业诊断书_{item['crop']}_{file_time}.md",
                    "text/markdown",
                    use_container_width=True,
                )
            with c2:
                st.download_button(
                    "下载 PDF",
                    create_pdf_bytes(item["report"], title=f"{item['crop']}农业智能诊断书"),
                    f"农业诊断书_{item['crop']}_{file_time}.pdf",
                    "application/pdf",
                    use_container_width=True,
                )
            with c3:
                if st.button("删除", key=f"del_{idx}", use_container_width=True):
                    st.session_state.history.pop(real_idx)
                    st.rerun()


def decision_page():
    if st.session_state.get("decision_view") == "result":
        result_page()
        return

    # ── 输入页 ──
    render_hero()

    # 输入模块：目标作物、pH、土壤质地与当前问题采集
    render_section_header("DATA COLLECTION", "输入模块", "采集地块核心数据，作为 AI 分析依据")
    soil_col, env_col = st.columns(2, gap="large")

    with soil_col:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span class="card-icon">田</span>基础地块数据</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">先录入作物、酸碱度和土壤质地，建立基础诊断画像。</div>', unsafe_allow_html=True)
            crop = st.selectbox("目标作物", list(CROP_PROFILES.keys()), index=None, placeholder="请选择目标作物", key="inp_crop")
            if crop == "其他作物":
                custom_crop = st.text_input("请输入作物名称", placeholder="例如：葡萄、柑橘、甘蔗", key="inp_custom_crop")
                crop = custom_crop.strip() if custom_crop and custom_crop.strip() else crop
            profile = CROP_PROFILES.get(crop) if crop in CROP_PROFILES else CROP_PROFILES["其他作物"]
            ph = st.number_input("土壤 pH 值", 0.0, 14.0, None, 0.1, placeholder="请输入数字", key="inp_ph")
            texture = st.selectbox("土壤质地", ["壤土", "沙土", "黏土", "砂壤土", "黏壤土", "不确定"], index=None, placeholder="请选择土壤质地", key="inp_texture")
            organic = st.number_input("有机质含量（%）", 0.0, 100.0, None, 0.1, placeholder="请输入数字", key="inp_organic")
            n = st.number_input("速效氮（mg/kg）", 0.0, 500.0, None, 1.0, placeholder="请输入数字", key="inp_n")
            p = st.number_input("速效磷（mg/kg）", 0.0, 300.0, None, 1.0, placeholder="请输入数字", key="inp_p")
            k = st.number_input("速效钾（mg/kg）", 0.0, 600.0, None, 1.0, placeholder="请输入数字", key="inp_k")

    with env_col:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span class="card-icon">诊</span>当前问题与环境</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">选择田间已观察到的问题，帮助 AI 明确优先处理方向。</div>', unsafe_allow_html=True)
            region = st.text_input("所在地区", placeholder="例如：浙江杭州、云南普洱", key="inp_region")
            plot_id = st.text_input("地块编号（可选）", placeholder="例如：A-03、茶园北坡 2 号", key="inp_plot_id")
            stage = st.selectbox("生育阶段", ["苗期", "营养生长期", "开花期", "结果期", "成熟期", "采收后", "越冬期"], index=None, placeholder="请选择生育阶段", key="inp_stage")
            area = st.number_input("种植面积（亩）", 0.1, 100000.0, None, 0.5, placeholder="请输入数字", key="inp_area")
            irrigation = st.selectbox("灌溉方式", ["自然降雨", "滴灌", "喷灌", "沟灌", "水田灌溉"], index=None, placeholder="请选择灌溉方式", key="inp_irrigation")
            weather = st.selectbox("近期天气", ["正常", "连续降雨", "高温干旱", "低温寡照", "昼夜温差大"], index=None, placeholder="请选择近期天气", key="inp_weather")
            issues = st.multiselect(
                "当前问题（可选）",
                ["长势弱", "有病虫害", "易板结", "叶片发黄", "根系弱", "产量下降", "排水不良", "肥效不稳"],
                placeholder="选择一个或多个田间问题",
                key="inp_issues",
            )
            observation = st.text_area("补充描述（可选）", placeholder="例如：局部死苗、雨后积水、新叶偏黄等", height=104, key="inp_observation")

    values = {
        "ph": ph if ph is not None else 0,
        "organic": organic if organic is not None else 0,
        "n": n if n is not None else 0,
        "p": p if p is not None else 0,
        "k": k if k is not None else 0,
    }
    assessments = build_assessments(values, profile)
    risk, risk_desc = risk_level(assessments)

    # 输出模块：提交后展示 AI 方案
    render_section_header("AI PLAN", "输出模块", "提交后展示核心结论、改良步骤和施肥建议")
    inputs = {
        "crop": crop,
        "plot_id": plot_id,
        "report_date": time.strftime("%Y年%m月%d日"),
        "region": region,
        "stage": stage,
        "area": area,
        "irrigation": irrigation,
        "texture": texture,
        "weather": weather,
        "issues": issues,
        "observation": observation,
    }
    prompt = build_prompt(inputs, values, profile, assessments)

    cta_col, clear_col = st.columns([3, 1])
    with cta_col:
        generate = st.button("AI 智能分析", type="primary", use_container_width=True)
    with clear_col:
        def _reset_inputs():
            st.session_state["inp_crop"] = None
            st.session_state["inp_ph"] = None
            st.session_state["inp_texture"] = None
            st.session_state["inp_organic"] = None
            st.session_state["inp_n"] = None
            st.session_state["inp_p"] = None
            st.session_state["inp_k"] = None
            st.session_state["inp_region"] = ""
            st.session_state["inp_plot_id"] = ""
            st.session_state["inp_stage"] = None
            st.session_state["inp_area"] = None
            st.session_state["inp_irrigation"] = None
            st.session_state["inp_weather"] = None
            st.session_state["inp_issues"] = []
            st.session_state["inp_observation"] = ""
        st.button("恢复默认数据", use_container_width=True, on_click=_reset_inputs)

    if generate:
        if not (st.session_state.get("saved_api_key") or st.session_state.get("api_key")):
            st.error("未配置 API Key。请先前往左侧「API 配置」页面输入 API Key，或设置环境变量 DEEPSEEK_API_KEY。")
            st.stop()

        # 校验：至少填写一个数据
        has_data = any(v is not None and v > 0 for v in [ph, organic, n, p, k, area])
        if not has_data:
            st.warning("请至少填写一个数据字段再进行分析。")
            st.stop()

        # 保存所有数据，立即跳转到结果页加载
        st.session_state.pending_prompt = prompt
        st.session_state.pending_crop = crop if crop else "未知作物"
        st.session_state.pending_inputs = inputs
        st.session_state.pending_values = values
        st.session_state.pending_risk = risk
        st.session_state.pending_risk_desc = risk_desc
        st.session_state.is_loading = True
        st.session_state.decision_view = "result"
        st.rerun()

    st.markdown(
        '<div style="text-align:center;color:var(--faint);font-size:.78rem;padding:18px 0 0;margin-top:24px">'
        '&#9888;&#65039; 免责声明：本系统生成内容仅供参考，具体施肥和病害处理请结合当地农技人员建议与正式检测报告。'
        '</div>',
        unsafe_allow_html=True,
    )


def main():
    init_state()
    active_page = render_sidebar()
    if active_page == "API 配置":
        api_config_page()
    elif active_page == "历史记录":
        history_page()
    else:
        decision_page()


if __name__ == "__main__":
    main()
