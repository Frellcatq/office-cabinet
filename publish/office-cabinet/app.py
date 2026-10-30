# -*- coding: utf-8 -*-
"""Рабочий кабинет координатора «Северная линия» (Streamlit).

Запуск:  ./run.sh   или   streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from cabinet import theme
from cabinet.store import get_workspace

st.set_page_config(
    page_title="Рабочий кабинет · Северная линия",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject()

NAV_ITEMS = [
    ("tasks", "Задачи"),
    ("calendar", "Календарь"),
    ("materials", "Материалы"),
    ("overview", "Обзор"),
    ("reports", "Отчёты"),
    ("backup", "Резервная копия"),
]
PAGE_BY_KEY = {
    "tasks": "cabinet.pages.tasks",
    "calendar": "cabinet.pages.calendar",
    "materials": "cabinet.pages.materials",
    "overview": "cabinet.pages.overview",
    "reports": "cabinet.pages.reports",
    "backup": "cabinet.pages.backup",
}
ws = get_workspace()
settings = ws.settings

# --- Боковая навигация ------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div style="padding: 6px 2px 2px;">'
        '<div style="font-size:22px; font-weight:700; color:#72539C;">Северная линия</div>'
        '<div style="color:#758093; font-size:13px; margin-top:4px;">'
        "Операционное сопровождение<br>Рабочий кабинет</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    nav_labels = [label for _, label in NAV_ITEMS]
    st.radio(
        "Навигация",
        nav_labels,
        index=nav_labels.index("Обзор"),
        key="nav_radio",
        label_visibility="collapsed",
    )

    st.write("")
    st.markdown(
        '<div style="color:#758093; font-size:13px;">Часовой пояс<br>'
        f'<b style="color:#263043;">{settings["timezone"]}</b></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        '<div class="cab-note">'
        "<b>Перед выходом скачайте резервную копию. При следующем посещении "
        "загрузите её. Автосохранения между посещениями нет.</b>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Настройки"):
        settings["coordinator_name"] = st.text_input(
            "Имя координатора", value=settings["coordinator_name"])
        settings["coordinator_role"] = st.text_input(
            "Роль", value=settings["coordinator_role"])
        settings["timezone"] = st.selectbox(
            "Часовой пояс",
            ["Europe/Minsk", "Europe/Moscow", "Europe/Kaliningrad", "UTC"],
            index=["Europe/Minsk", "Europe/Moscow", "Europe/Kaliningrad", "UTC"]
            .index(settings["timezone"]),
        )
        settings["default_period"] = st.selectbox(
            "Период по умолчанию",
            ["Текущая неделя", "Текущий месяц", "План ноября 2026"],
            index=["Текущая неделя", "Текущий месяц", "План ноября 2026"]
            .index(settings["default_period"]),
        )
        st.caption("Настройки хранятся в сеансе и попадают в резервную копию.")

    if ws.is_empty() and not ws.documents:
        st.markdown(
            '<div class="cab-note" style="margin-top:12px;">Кабинет пуст: данные '
            "не загружаются автоматически. Загрузите исходный план в разделе "
            "«Задачи» или резервную копию в разделе «Резервная копия».</div>",
            unsafe_allow_html=True,
        )

# --- Шапка с карточкой пользователя -----------------------------------------

header_left, header_right = st.columns([3, 1])
with header_right:
    initials = "".join(part[0] for part in settings["coordinator_name"].split()[:2]).upper()
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:10px;">'
        f'<div style="width:40px; height:40px; border-radius:50%; background:#EDE8FA; '
        f'color:#72539C; font-weight:700; display:flex; align-items:center; '
        f'justify-content:center;">{initials}</div>'
        f'<div><div style="font-weight:600; color:#263043;">'
        f'{settings["coordinator_name"]}</div>'
        f'<div style="color:#758093; font-size:13px;">{settings["coordinator_role"]}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )

# --- Выбранный раздел ---------------------------------------------------------

import importlib  # noqa: E402

nav_label = st.session_state.get("nav_radio", "Обзор")
nav_key = next(key for key, label in NAV_ITEMS if label == nav_label)
page_module = importlib.import_module(PAGE_BY_KEY[nav_key])
page_module.render()
