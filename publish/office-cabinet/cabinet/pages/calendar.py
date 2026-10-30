# -*- coding: utf-8 -*-
"""Раздел «Календарь»: встречи выбранной недели по дням."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from ..components import data_placeholder, empty_state, page_header
from ..store import get_workspace

WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def render() -> None:
    ws = get_workspace()
    page_header(
        "Рабочий кабинет",
        "Календарь",
        "Встречи координатора по дням выбранной недели",
    )

    if not ws.meetings:
        data_placeholder(
            "Календарь",
            [
                "Выбор недели и список встреч по дням: время, проект, тема, место и участники.",
            ],
        )
        return

    any_day = st.date_input(
        "Неделя (выберите любой её день)",
        value=date(2026, 11, 9),
    )
    monday = any_day - timedelta(days=any_day.weekday())
    week_days = [monday + timedelta(days=offset) for offset in range(7)]

    st.caption(
        f"Неделя: {monday.strftime('%d.%m.%Y')} — "
        f"{(monday + timedelta(days=6)).strftime('%d.%m.%Y')}"
    )

    week_meetings = [m for m in ws.meetings if m.date in week_days]
    if not week_meetings:
        empty_state("📅", "Встреч на этой неделе нет", "Выберите другую неделю.")
        return

    for day in week_days:
        day_meetings = sorted(
            (m for m in week_meetings if m.date == day),
            key=lambda m: (m.start or m.end),
        )
        if not day_meetings:
            continue
        with st.container(border=True):
            st.markdown(
                f"#### {WEEKDAYS[day.weekday()]}, {day.strftime('%d.%m.%Y')}"
            )
            for meeting in day_meetings:
                participants = ", ".join(
                    ws.employee_name(code) for code in meeting.participant_codes
                ) or "Участники не указаны"
                start = meeting.start.strftime("%H:%M") if meeting.start else "--:--"
                end = meeting.end.strftime("%H:%M") if meeting.end else "--:--"
                st.markdown(
                    f"**{start}–{end} · {ws.project_name(meeting.project_code)}**  \n"
                    f"{meeting.topic}  \n"
                    f'<span style="color:#758093;">{meeting.place} · {participants} · '
                    f"{meeting.code} · {meeting.status}</span>",
                    unsafe_allow_html=True,
                )
