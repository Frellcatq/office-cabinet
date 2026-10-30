# -*- coding: utf-8 -*-
"""Раздел «Отчёты»: выгрузка текущей выборки задач в CSV."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ..components import data_placeholder, page_header
from ..models import TASK_STATUSES
from ..store import get_workspace


def render() -> None:
    ws = get_workspace()
    page_header(
        "Рабочий кабинет",
        "Отчёты",
        "Выгрузка выборки задач в CSV (UTF-8 BOM, разделитель «;»)",
    )

    if not ws.tasks:
        data_placeholder(
            "Отчёты",
            [
                "Выборка задач с фильтрами и скачивание файла CSV, "
                "готового для Excel.",
            ],
        )
        return

    project_options = ["Все проекты"] + [f"{p.code} — {p.name}" for p in ws.projects]
    employee_options = ["Все сотрудники"] + [f"{e.code} — {e.name}" for e in ws.employees]
    with st.container(border=True):
        col_project, col_employee, col_status = st.columns(3)
        project_filter = col_project.selectbox("Проект", project_options)
        employee_filter = col_employee.selectbox("Сотрудник", employee_options)
        status_filter = col_status.multiselect("Статус", TASK_STATUSES)

    rows = list(ws.tasks)
    if project_filter != "Все проекты":
        code = project_filter.split(" — ")[0]
        rows = [t for t in rows if t.project_code == code]
    if employee_filter != "Все сотрудники":
        code = employee_filter.split(" — ")[0]
        rows = [t for t in rows if t.assignee_code == code]
    if status_filter:
        rows = [t for t in rows if t.status in status_filter]

    st.caption(f"Задач в выгрузке: {len(rows)} из {len(ws.tasks)}")

    frame = pd.DataFrame([
        {
            "Код задачи": t.code,
            "Код проекта": t.project_code,
            "Название задачи": t.title,
            "Код ответственного": t.assignee_code,
            "Статус": t.status,
            "Приоритет": t.priority,
            "Дата плана": t.planned_date.isoformat() if t.planned_date else "",
            "Начало работы": t.start_time.strftime("%H:%M") if t.start_time else "",
            "План, ч": t.planned_hours if t.planned_hours is not None else "",
            "Срок": t.deadline.isoformat() if t.deadline else "",
            "Дата завершения": t.completed_date.isoformat() if t.completed_date else "",
            "Комментарий": t.comment,
        }
        for t in rows
    ])
    csv_text = frame.to_csv(index=False, sep=";", encoding="utf-8-sig")

    st.download_button(
        "Скачать CSV",
        data=csv_text,
        file_name="задачи_выгрузка.csv",
        mime="text/csv; charset=utf-8",
        type="primary",
    )
