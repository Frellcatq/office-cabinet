# -*- coding: utf-8 -*-
"""Общие UI-компоненты разделов."""
from __future__ import annotations

from typing import Optional

import streamlit as st


def page_header(kicker: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<p class="cab-kicker">{kicker}</p>'
        f'<h2 class="cab-title">{title}</h2>'
        + (f'<p class="cab-subtitle">{subtitle}</p>' if subtitle else ""),
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "") -> None:
    note_html = f'<div class="cab-metric-note">{note}</div>' if note else ""
    st.markdown(
        f'<div class="cab-metric">'
        f'<div class="cab-metric-label">{label}</div>'
        f'<div class="cab-metric-value">{value}</div>'
        f'{note_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, text: str, hint: Optional[str] = None) -> None:
    hint_html = f"<p>{hint}</p>" if hint else ""
    st.markdown(
        f'<div class="cab-empty">'
        f'<div class="cab-empty-icon">{icon}</div>'
        f"<h4>{title}</h4>"
        f"<p>{text}</p>"
        f"{hint_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def data_placeholder(section: str, what_will_be_here: list) -> None:
    """Единое пустое состояние для разделов без данных."""
    empty_state(
        icon="🗂️",
        title=f"В разделе «{section}» пока нет данных",
        text="Рабочее пространство этого сеанса пустое: исходные данные "
             "не загружаются автоматически. Загрузите резервную копию в разделе "
             "«Резервная копия» — и раздел наполнится записями.",
    )
    st.write("")
    items = "".join(f"<li>{item}</li>" for item in what_will_be_here)
    st.markdown(
        f'<div class="cab-panel"><h4>Что появится в разделе</h4>'
        f"<ul>{items}</ul>"
        f'<p class="cab-muted">Коды записей (TSK-…, MTG-…, PR-…, EMP-…) '
        f"сохраняются в исходном формате.</p></div>",
        unsafe_allow_html=True,
    )
