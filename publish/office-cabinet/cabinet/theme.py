# -*- coding: utf-8 -*-
"""Тема оформления по референсу «Рабочий кабинет».

Светлый рабочий интерфейс: фон #F5F6FA, поверхности #FFFFFF,
текст #263043, второстепенный текст #758093, акцент #72539C,
светлое выделение #EDE8FA, предупреждения #FFF5E8.
"""
from __future__ import annotations

import streamlit as st

ACCENT = "#72539C"
ACCENT_LIGHT = "#EDE8FA"
WARNING_BG = "#FFF5E8"
TEXT_MAIN = "#263043"
TEXT_MUTED = "#758093"
PAGE_BG = "#F5F6FA"
SURFACE = "#FFFFFF"
BORDER = "#E3E6EF"

CSS = f"""
<style>
/* --- базовые поверхности --- */
.stApp {{
    background: {PAGE_BG};
    color: {TEXT_MAIN};
}}
section.stApp > header {{ background: transparent; }}

[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] * {{ color: {TEXT_MAIN}; }}

/* --- шапка Streamlit: убрать тёмную полосу и кнопку Deploy --- */
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stHeader"] * {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}

/* --- боковая навигация (радио в виде пунктов меню) --- */
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{
    gap: 2px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 2px;
    cursor: pointer;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{ display: none; }}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {{
    color: {TEXT_MAIN};
    font-size: 15px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
    background: {ACCENT_LIGHT};
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{
    color: {ACCENT};
    font-weight: 700;
}}

.block-container {{ padding-top: 1.2rem; max-width: 1200px; }}

/* --- заголовки разделов --- */
.cab-kicker {{
    color: {TEXT_MUTED};
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0;
}}
.cab-title {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_MAIN};
    margin: 0 0 4px 0;
}}
.cab-subtitle {{
    color: {TEXT_MUTED};
    font-size: 15px;
    margin-bottom: 16px;
}}

/* --- карточки-показатели: текст строго по центру --- */
.cab-metric {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
}}
.cab-metric .cab-metric-label {{ color: {TEXT_MUTED}; font-size: 14px; }}
.cab-metric .cab-metric-value {{
    font-size: 34px;
    font-weight: 700;
    color: {ACCENT};
    margin: 6px 0;
}}
.cab-metric .cab-metric-note {{ color: {TEXT_MUTED}; font-size: 13px; }}

/* --- пустое состояние --- */
.cab-empty {{
    background: {SURFACE};
    border: 1px dashed {ACCENT};
    border-radius: 12px;
    padding: 32px 28px;
    text-align: center;
}}
.cab-empty .cab-empty-icon {{ font-size: 34px; }}
.cab-empty h4 {{ color: {TEXT_MAIN}; font-size: 18px; margin: 10px 0 6px; }}
.cab-empty p {{ color: {TEXT_MUTED}; font-size: 14px; margin: 0 auto 6px; max-width: 560px; }}

/* --- панели и примечания --- */
.cab-panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px;
}}
.cab-panel h4 {{ color: {TEXT_MAIN}; margin-top: 0; }}
.cab-note {{
    background: {WARNING_BG};
    color: {TEXT_MAIN};
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 14px;
}}
.cab-muted {{ color: {TEXT_MUTED}; font-size: 14px; }}

/* --- кнопки в акцентном цвете --- */
div.stButton > button,
[data-testid="stDownloadButton"] > button {{
    border-radius: 10px;
    border: 1px solid {ACCENT};
    color: {ACCENT};
    background: {SURFACE};
    font-weight: 600;
}}
div.stButton > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {{
    background: {ACCENT} !important;
    color: #FFFFFF !important;
    border-color: {ACCENT} !important;
}}
div.stButton > button[kind="primary"] p,
[data-testid="stDownloadButton"] > button[kind="primary"] p {{
    color: #FFFFFF !important;
}}
div.stButton > button:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}

/* --- показатели st.metric в стиле референса --- */
[data-testid="stMetric"] label p {{ color: {TEXT_MUTED}; }}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {TEXT_MAIN};
    font-weight: 700;
}}

/* --- таблицы: читаемые столбцы, умеренная плотность --- */
.dataframe {{ font-size: 14px; }}
.dataframe th {{ color: {TEXT_MUTED}; font-weight: 600; }}

/* --- компактная навигация (в т.ч. на телефоне) --- */
[data-testid="stSidebar"] .stRadio label {{
    padding: 4px 2px;
    font-size: 15px;
}}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
