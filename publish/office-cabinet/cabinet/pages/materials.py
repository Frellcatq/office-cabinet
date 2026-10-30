# -*- coding: utf-8 -*-
"""Раздел «Материалы»: загрузка DOCX/TXT, привязка к проекту, скачивание."""
from __future__ import annotations

import streamlit as st

from ..archive import MAX_MATERIAL_FILE_BYTES, MAX_MATERIAL_TOTAL_BYTES
from ..components import data_placeholder, page_header
from ..models import find_codes, guess_document_kind
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
        "Материалы",
        "Документы сеанса, привязанные к проектам. Оригиналы хранятся только в сеансе.",
    )

    if not ws.projects:
        data_placeholder(
            "Материалы",
            [
                "Загрузка файлов DOCX и TXT (до 5 МБ на файл, до 20 МБ всего) "
                "с привязкой к проекту.",
                "Список документов и скачивание оригинала.",
                "Связи с встречами и задачами распознаются по кодам в имени файла.",
            ],
        )
        return

    total_bytes = ws.materials_total_bytes()
    st.caption(
        f"Материалов: {len(ws.documents)} · занято {_size_label(total_bytes)} "
        f"из {_size_label(MAX_MATERIAL_TOTAL_BYTES)}"
    )

    # --- Загрузка ---------------------------------------------------------------
    with st.expander("Загрузить материалы", expanded=not ws.documents):
        uploads = st.file_uploader(
            "Файлы DOCX или TXT",
            type=["docx", "txt"],
            accept_multiple_files=True,
            key="material_files",
        )
        project_choice = st.selectbox(
            "Привязать к проекту",
            [f"{p.code} — {p.name}" for p in ws.projects],
        )
        project_code = project_choice.split(" — ")[0]
        if uploads and st.button("Загрузить и привязать", type="primary"):
            saved, rejected = 0, []
            for upload in uploads:
                content = upload.getvalue()
                if len(content) > MAX_MATERIAL_FILE_BYTES:
                    rejected.append(f"«{upload.name}» — больше 5 МБ.")
                    continue
                if total_bytes + len(content) > MAX_MATERIAL_TOTAL_BYTES:
                    rejected.append(f"«{upload.name}» — превышен общий лимит 20 МБ.")
                    continue
                codes = find_codes(upload.name)
                ws.add_document(
                    name=upload.name,
                    kind=guess_document_kind(upload.name),
                    project_code=project_code,
                    meeting_code=codes.get("meeting", ""),
                    task_code=codes.get("task", ""),
                    content=content,
                )
                total_bytes += len(content)
                saved += 1
            if saved:
                st.success(f"Загружено материалов: {saved} (проект {project_code}).")
            for message in rejected:
                st.error(f"Не загружено: {message}")
            if saved:
                st.rerun()

    # --- Список и скачивание ------------------------------------------------------
    if not ws.documents:
        data_placeholder(
            "Материалы",
            ["Здесь появятся загруженные файлы и их привязки к проектам."],
        )
        return

    for document in ws.documents:
        with st.container(border=True):
            col_info, col_download = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{document.name}**")
                links = [f"Проект: {ws.project_name(document.project_code)}"]
                if document.meeting_code:
                    links.append(f"Встреча: {document.meeting_code}")
                if document.task_code:
                    links.append(f"Задача: {document.task_code}")
                size = ws.files.get(document.key, b"")
                st.caption(
                    f"{document.kind} · {' · '.join(links)} · {_size_label(len(size))}"
                )
            with col_download:
                if document.key in ws.files:
                    st.download_button(
                        "Скачать",
                        data=ws.files[document.key],
                        file_name=document.name,
                        key=f"download_{document.key}",
                        use_container_width=True,
                    )
                else:
                    st.caption("Файл недоступен")
