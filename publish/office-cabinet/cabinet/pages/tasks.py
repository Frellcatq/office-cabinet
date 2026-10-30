# -*- coding: utf-8 -*-
"""Раздел «Задачи»: загрузка исходного XLSX, фильтры, таблица, смена статуса."""
from __future__ import annotations

import streamlit as st

from ..components import data_placeholder, page_header
from ..loading import parse_workbook
from ..models import TASK_STATUSES
from ..store import get_workspace


def render() -> None:
    ws = get_workspace()
    page_header(
        "Рабочий кабинет",
        "Задачи",
        "Загрузка плана, фильтры и статусы. Коды записей сохраняются.",
    )

    # --- Загрузка исходного XLSX --------------------------------------------
    with st.expander("Загрузить исходный план (XLSX)", expanded=ws.is_empty()):
        st.caption(
            "Книга с листами «Задачи», «Встречи», «Проекты», «Сотрудники». "
            "Перед заменой данные проверяются: столбцы, даты, уникальность кодов "
            "и ссылки на проекты и сотрудников. Повторная загрузка заменяет набор, "
            "а не добавляет дубли."
        )
        uploaded = st.file_uploader("Файл XLSX", type=["xlsx"], key="plan_xlsx")
        if uploaded is not None:
            if st.button("Проверить и заменить данные", type="primary"):
                datasets, errors = parse_workbook(uploaded.getvalue())
                if errors:
                    st.error("Данные не заменены. Исправьте ошибки в файле:")
                    for error in errors[:30]:
                        st.markdown(f"- {error}")
                    if len(errors) > 30:
                        st.caption(f"…и ещё {len(errors) - 30} ошибок.")
                else:
                    dropped = ws.replace_datasets(
                        employees=datasets["employees"],
                        projects=datasets["projects"],
                        tasks=datasets["tasks"],
                        meetings=datasets["meetings"],
                        source_note=f"Загружен файл {uploaded.name}",
                    )
                    st.success(
                        f"Данные загружены: проектов {len(datasets['projects'])}, "
                        f"сотрудников {len(datasets['employees'])}, "
                        f"задач {len(datasets['tasks'])}, встреч {len(datasets['meetings'])}."
                    )
                    if dropped:
                        st.warning(
                            f"Удалено материалов с исчезнувшими проектами: {dropped}."
                        )
                    st.rerun()

    if not ws.tasks:
        data_placeholder(
            "Задачи",
            [
                "Таблица задач с фильтрами по проекту и сотруднику.",
                "Изменение статуса выбранной задачи с сохранением её кода.",
            ],
        )
        return

    # --- Фильтры --------------------------------------------------------------
    project_options = ["Все проекты"] + [f"{p.code} — {p.name}" for p in ws.projects]
    employee_options = ["Все сотрудники"] + [f"{e.code} — {e.name}" for e in ws.employees]
    with st.container(border=True):
        col_project, col_employee = st.columns(2)
        project_filter = col_project.selectbox("Проект", project_options)
        employee_filter = col_employee.selectbox("Сотрудник", employee_options)

    rows = list(ws.tasks)
    if project_filter != "Все проекты":
        code = project_filter.split(" — ")[0]
        rows = [t for t in rows if t.project_code == code]
    if employee_filter != "Все сотрудники":
        code = employee_filter.split(" — ")[0]
        rows = [t for t in rows if t.assignee_code == code]

    st.caption(f"Задач в выборке: {len(rows)} из {len(ws.tasks)}")
    st.dataframe(
        [
            {
                "Код": t.code,
                "Проект": ws.project_name(t.project_code),
                "Задача": t.title,
                "Ответственный": ws.employee_name(t.assignee_code),
                "Статус": t.status,
                "Приоритет": t.priority,
                "Дата плана": t.planned_date.strftime("%d.%m.%Y") if t.planned_date else "",
                "Срок": t.deadline.strftime("%d.%m.%Y") if t.deadline else "",
                "План, ч": t.planned_hours,
            }
            for t in rows
        ],
        use_container_width=True,
        hide_index=True,
    )

    # --- Изменение статуса ------------------------------------------------------
    with st.container(border=True):
        st.markdown("#### Изменить статус выбранной задачи")
        if not rows:
            st.caption("В выборке нет задач.")
        else:
            choices = {f"{t.code} — {t.title}": t for t in rows}
            choice = st.selectbox("Задача", list(choices.keys()))
            task = choices[choice]
            statuses = list(TASK_STATUSES) if task.status in TASK_STATUSES else [task.status] + TASK_STATUSES
            new_status = st.selectbox("Новый статус", statuses,
                                      index=statuses.index(task.status))
            if st.button("Применить", type="primary"):
                task.status = new_status
                st.success(f"Статус задачи {task.code} изменён: {new_status}.")
                st.rerun()
