# -*- coding: utf-8 -*-
"""Раздел «Обзор»: три показателя по отфильтрованным задачам."""
from __future__ import annotations

from datetime import date

import streamlit as st

from ..components import data_placeholder, metric_card, page_header
from ..store import get_workspace

DEFAULT_CHECK_DATE = date(2026, 11, 9)


def render() -> None:
    ws = get_workspace()
    page_header(
        "Рабочий кабинет",
        "Обзор",
        "Показатели задач по проекту и сотруднику",
    )

    if not ws.tasks:
        data_placeholder(
            "Обзор",
            [
                "Три показателя по отфильтрованным задачам: всего, выполнено, просрочено. "
                "Контрольная дата выбирается пользователем.",
            ],
        )
        return

    project_options = ["Все проекты"] + [f"{p.code} — {p.name}" for p in ws.projects]
    employee_options = ["Все сотрудники"] + [f"{e.code} — {e.name}" for e in ws.employees]
    with st.container(border=True):
        col_project, col_employee, col_date = st.columns(3)
        project_filter = col_project.selectbox("Проект", project_options)
        employee_filter = col_employee.selectbox("Сотрудник", employee_options)
        check_date = col_date.date_input("Контрольная дата", value=DEFAULT_CHECK_DATE)

    rows = list(ws.tasks)
    if project_filter != "Все проекты":
        code = project_filter.split(" — ")[0]
        rows = [t for t in rows if t.project_code == code]
    if employee_filter != "Все сотрудники":
        code = employee_filter.split(" — ")[0]
        rows = [t for t in rows if t.assignee_code == code]

    total = len(rows)
    done = sum(1 for t in rows if t.status == "Выполнена")
    overdue = sum(
        1 for t in rows
        if t.status not in ("Выполнена", "Отменена")
        and t.deadline is not None
        and t.deadline < check_date
    )

    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Всего задач", str(total), "В выбранной области данных")
    with col2:
        metric_card("Выполнено задач", str(done), "Статус «Выполнена»")
    with col3:
        metric_card(
            "Просрочено задач",
            str(overdue),
            f"Срок строго раньше {check_date.strftime('%d.%m.%Y')}",
        )
