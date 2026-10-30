# -*- coding: utf-8 -*-
"""Хранилище данных пользователя в его сеансе.

Все записи живут в st.session_state — общей папки с файлами и внешней
базы нет. Исходные данные не загружаются автоматически: рабочее
пространство создаётся пустым и наполняется вручную (загрузкой снимка
или, в дальнейшем, файлов пользователя).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import streamlit as st

from . import models
from .models import (
    DocumentLink,
    Employee,
    Meeting,
    Project,
    Task,
    next_code,
    record_from_dict,
    record_to_dict,
)

WORKSPACE_KEY = "cabinet_workspace"

DEFAULT_SETTINGS = {
    "coordinator_name": "Марина Соколова",
    "coordinator_role": "Координатор проектов",
    "timezone": "Europe/Minsk",
    "default_period": "Текущая неделя",
}


@dataclass
class Workspace:
    """Рабочее пространство одного сеанса."""

    projects: List[Project] = field(default_factory=list)
    employees: List[Employee] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    meetings: List[Meeting] = field(default_factory=list)
    documents: List[DocumentLink] = field(default_factory=list)
    files: Dict[str, bytes] = field(default_factory=dict)  # key документа -> оригинал
    settings: Dict = field(default_factory=lambda: dict(DEFAULT_SETTINGS))
    loaded_at: str = ""            # когда пространство было наполнено/восстановлено
    source_note: str = ""          # откуда пришли данные (снимок, файлы…)

    # --- состояние ---------------------------------------------------------

    def is_empty(self) -> bool:
        return not (self.projects or self.employees or self.tasks or self.meetings)

    # --- доступ ------------------------------------------------------------

    def employee_name(self, code: str) -> str:
        for employee in self.employees:
            if employee.code == code:
                return employee.name
        return code

    def project_name(self, code: str) -> str:
        for project in self.projects:
            if project.code == code:
                return project.name
        return code

    def documents_for(self, project_code: str = "", meeting_code: str = "") -> List[DocumentLink]:
        result = []
        for document in self.documents:
            if project_code and document.project_code != project_code:
                continue
            if meeting_code and document.meeting_code != meeting_code:
                continue
            result.append(document)
        return result

    # --- новые записи (коды существующих не меняются) ----------------------

    def add_task(self, **kwargs) -> Task:
        task = Task(code=next_code([t.code for t in self.tasks], "TSK"), **kwargs)
        self.tasks.append(task)
        return task

    def add_meeting(self, **kwargs) -> Meeting:
        meeting = Meeting(
            code=next_code([m.code for m in self.meetings], "MTG"), **kwargs
        )
        self.meetings.append(meeting)
        return meeting

    def add_project(self, **kwargs) -> Project:
        project = Project(
            code=next_code([p.code for p in self.projects], "PR"), **kwargs
        )
        self.projects.append(project)
        return project

    def add_employee(self, **kwargs) -> Employee:
        employee = Employee(
            code=next_code([e.code for e in self.employees], "EMP"), **kwargs
        )
        self.employees.append(employee)
        return employee

    def add_document(self, name: str, kind: str = "Прочее", note: str = "",
                     project_code: str = "", meeting_code: str = "",
                     task_code: str = "", content: bytes = b"") -> DocumentLink:
        document = DocumentLink(
            key=uuid.uuid4().hex[:12],
            name=name,
            kind=kind,
            project_code=project_code,
            meeting_code=meeting_code,
            task_code=task_code,
            note=note,
            uploaded_at=datetime.now(),
        )
        self.documents.append(document)
        if content:
            self.files[document.key] = content
        return document

    def materials_total_bytes(self) -> int:
        return sum(len(content) for content in self.files.values())

    def replace_datasets(self, employees: List[Employee], projects: List[Project],
                         tasks: List[Task], meetings: List[Meeting],
                         source_note: str) -> int:
        """Заменяет наборы данных целиком (без дублей при повторной загрузке).

        Материалы, привязанные к исчезнувшим проектам, удаляются;
        возвращается их количество.
        """
        self.employees = employees
        self.projects = projects
        self.tasks = tasks
        self.meetings = meetings
        project_codes = {p.code for p in projects}
        kept = [d for d in self.documents if not d.project_code or d.project_code in project_codes]
        dropped = len(self.documents) - len(kept)
        self.documents = kept
        self.loaded_at = datetime.now().isoformat(timespec="seconds")
        self.source_note = source_note
        return dropped

    # --- снимок (резервная копия сеанса) -----------------------------------

    def to_snapshot(self) -> Dict:
        return {
            "app": "Рабочий кабинет «Северная линия»",
            "format_version": 1,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "source_note": self.source_note,
            "loaded_at": self.loaded_at,
            "settings": self.settings,
            "projects": [record_to_dict(item) for item in self.projects],
            "employees": [record_to_dict(item) for item in self.employees],
            "tasks": [record_to_dict(item) for item in self.tasks],
            "meetings": [record_to_dict(item) for item in self.meetings],
            "documents": [record_to_dict(item) for item in self.documents],
        }

    def load_snapshot(self, snapshot: Dict, files: Dict[str, bytes] = None) -> None:
        """Заменяет содержимое пространства данными снимка.

        Коды записей снимка сохраняются как есть.
        """
        collections = {
            Project: "projects",
            Employee: "employees",
            Task: "tasks",
            Meeting: "meetings",
            DocumentLink: "documents",
        }
        for cls, attr in collections.items():
            records = [record_from_dict(cls, item) for item in snapshot.get(attr, [])]
            setattr(self, attr, records)
        settings = dict(DEFAULT_SETTINGS)
        settings.update(snapshot.get("settings") or {})
        self.settings = settings
        self.loaded_at = snapshot.get("saved_at") or datetime.now().isoformat(timespec="seconds")
        self.source_note = snapshot.get("source_note") or "Восстановлено из резервной копии"
        if files is not None:
            self.files = files


def get_workspace() -> Workspace:
    """Возвращает рабочее пространство сеанса, создавая при первом обращении."""
    if WORKSPACE_KEY not in st.session_state:
        st.session_state[WORKSPACE_KEY] = Workspace()
    return st.session_state[WORKSPACE_KEY]
