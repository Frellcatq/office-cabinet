# -*- coding: utf-8 -*-
"""Раздел «Резервная копия»: ZIP со всеми данными и оригиналами материалов."""
from __future__ import annotations

import streamlit as st

from ..archive import MAX_MATERIAL_TOTAL_BYTES, build_zip, read_zip
from ..components import page_header
from ..store import get_workspace


def _size_label(count: int) -> str:
    value = float(count)
    for unit in ("Б", "КБ", "МБ"):
        if value < 1024 or unit == "МБ":
            return f"{value:.0f} {unit}" if unit == "Б" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} МБ"


def render() -> None:
    ws = get_workspace()
    page_header(
        "Рабочий кабинет",
        "Резервная копия",
        "Архив со всеми данными сеанса, материалами и их связями",
    )

    st.markdown(
        '<div class="cab-note">'
        "<b>Перед выходом скачайте резервную копию. При следующем посещении "
        "загрузите её. Автосохранения между посещениями нет.</b><br>"
        "Кабинет хранит данные только в сеансе: без внешней базы и общей папки. "
        "Архив включает все записи и материалы независимо от фильтров; "
        "коды записей сохраняются."
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Проекты", len(ws.projects))
    col2.metric("Сотрудники", len(ws.employees))
    col3.metric("Задачи", len(ws.tasks))
    col4.metric("Встречи", len(ws.meetings))
    col5.metric("Материалы", len(ws.documents))

    st.write("")
    left, right = st.columns(2)

    # --- Скачивание -----------------------------------------------------------
    with left, st.container(border=True):
        st.markdown("#### Скачать копию")
        st.caption(
            f"Материалы в архиве: {_size_label(ws.materials_total_bytes())} "
            f"из {_size_label(MAX_MATERIAL_TOTAL_BYTES)}"
        )
        archive_bytes = build_zip(ws)
        st.download_button(
            "Скачать ZIP-архив",
            data=archive_bytes,
            file_name="рабочий_кабинет_резервная_копия.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )
        st.caption(f"Размер архива: {_size_label(len(archive_bytes))}")
        if ws.source_note:
            st.caption(f"Источник данных: {ws.source_note}")

    # --- Восстановление ---------------------------------------------------------
    with right, st.container(border=True):
        st.markdown("#### Загрузить копию")
        uploaded = st.file_uploader(
            "Файл резервной копии (ZIP)",
            type=["zip"],
            key="backup_zip",
        )
        if uploaded is not None:
            manifest, files, errors = read_zip(uploaded.getvalue())
            if errors:
                st.error("Архив не загружен — данные сеанса не изменены:")
                for error in errors[:30]:
                    st.markdown(f"- {error}")
                if len(errors) > 30:
                    st.caption(f"…и ещё {len(errors) - 30} проблем.")
            else:
                saved_at = manifest.get("saved_at", "неизвестно")
                counts = (
                    f"проектов {len(manifest.get('projects', []))}, "
                    f"сотрудников {len(manifest.get('employees', []))}, "
                    f"задач {len(manifest.get('tasks', []))}, "
                    f"встреч {len(manifest.get('meetings', []))}, "
                    f"материалов {len(manifest.get('documents', []))}"
                )
                st.warning(
                    f"Архив от {saved_at}: {counts}. "
                    "Загрузка заменит все текущие данные сеанса."
                )
                if st.button("Заменить данные сеанса", type="primary"):
                    ws.load_snapshot(manifest, files)
                    st.success("Резервная копия загружена. Коды записей сохранены.")
                    st.rerun()
