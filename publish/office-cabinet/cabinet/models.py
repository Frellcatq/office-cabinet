# -*- coding: utf-8 -*-
"""Единая модель данных рабочего кабинета координатора.

Коды записей сохраняются в исходном формате и служат ключами связей:
  PR-XX   — проекты          (PR-01 …)
  EMP-XX  — сотрудники       (EMP-01 …)
  TSK-XXX — задачи           (TSK-001 …)
  MTG-XXX — встречи          (MTG-001 …)

Связи с документами хранятся отдельными записями DocumentLink,
а не вложенными файлами: документ относится к проекту и/или встрече
по кодам, исходное имя файла сохраняется.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time
from typing import Dict, List, Optional

# --- Справочники статусов (по данным компании) ----------------------------

TASK_STATUSES = ["Новая", "В работе", "Ожидает", "Выполнена", "Отменена"]
TASK_PRIORITIES = ["Высокий", "Средний", "Низкий"]
MEETING_STATUSES = ["Запланирована", "Проведена", "Отменена"]
PROJECT_STATUSES = ["В работе", "Завершён", "Приостановлен"]
DOCUMENT_KINDS = ["Паспорт проекта", "Повестка встречи", "Прочее"]


# --- Записи ----------------------------------------------------------------


@dataclass
class Employee:
    code: str                      # EMP-08
    name: str                      # ФИО
    position: str = ""
    department: str = ""


@dataclass
class Project:
    code: str                      # PR-01
    name: str
    owner_code: str = ""           # EMP-XX владельца
    start: Optional[date] = None
    end: Optional[date] = None
    status: str = "В работе"
    goal: str = ""


@dataclass
class Task:
    code: str                      # TSK-009
    project_code: str              # PR-XX
    title: str
    assignee_code: str = ""        # EMP-XX
    status: str = "Новая"
    priority: str = "Средний"
    planned_date: Optional[date] = None
    start_time: Optional[time] = None
    planned_hours: Optional[float] = None
    deadline: Optional[date] = None
    completed_date: Optional[date] = None
    comment: str = ""


@dataclass
class Meeting:
    code: str                      # MTG-033
    project_code: str              # PR-XX
    topic: str
    date: Optional[date] = None
    start: Optional[time] = None
    end: Optional[time] = None
    participant_codes: List[str] = field(default_factory=list)  # [EMP-XX, …]
    place: str = ""
    status: str = "Запланирована"
    agenda: str = ""


@dataclass
class DocumentLink:
    """Связь загруженного пользователем файла с записями модели.

    Файл хранится только в сеансе пользователя; здесь — его описание
    и привязки по кодам записей.
    """
    key: str                       # служебный ключ записи в сеансе
    name: str                      # исходное имя файла, напр. PR-05_Паспорт_проекта.docx
    kind: str = "Прочее"           # Паспорт проекта / Повестка встречи / Прочее
    project_code: str = ""         # PR-XX или ""
    meeting_code: str = ""         # MTG-XXX или ""
    task_code: str = ""            # TSK-XXX или ""
    note: str = ""
    uploaded_at: Optional[datetime] = None


# --- Распознавание кодов и связей из имён файлов ---------------------------

_CODE_PATTERNS = {
    "project": re.compile(r"PR-\d+", re.IGNORECASE),
    "meeting": re.compile(r"MTG-\d+", re.IGNORECASE),
    "task": re.compile(r"TSK-\d+", re.IGNORECASE),
    "employee": re.compile(r"EMP-\d+", re.IGNORECASE),
}


def find_codes(text: str) -> Dict[str, str]:
    """Возвращает первый найденный код каждого типа в строке."""
    found = {}
    for kind, pattern in _CODE_PATTERNS.items():
        match = pattern.search(text)
        if match:
            found[kind] = match.group(0).upper()
    return found


def guess_document_kind(name: str) -> str:
    lowered = name.lower()
    if "паспорт" in lowered:
        return "Паспорт проекта"
    if "повестка" in lowered:
        return "Повестка встречи"
    return "Прочее"


# --- Коды новых записей ----------------------------------------------------

_CODE_TEMPLATES = {
    "PR": ("project", 2),
    "EMP": ("employee", 2),
    "TSK": ("task", 3),
    "MTG": ("meeting", 3),
}


def next_code(existing: List[str], prefix: str) -> str:
    """Следующий свободный код в исходном формате: TSK-251 после TSK-250."""
    _, width = _CODE_TEMPLATES[prefix]
    pattern = re.compile(rf"^{prefix}-(\d+)$", re.IGNORECASE)
    numbers = [
        int(m.group(1))
        for code in existing
        for m in [pattern.match(code.strip())]
        if m
    ]
    return f"{prefix}-{max(numbers, default=0) + 1:0{width}d}"


# --- Сериализация ----------------------------------------------------------


def _iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.strftime("%H:%M")
    return value


def _parse_date(text):
    if not text:
        return None
    if isinstance(text, date):
        return text
    return datetime.fromisoformat(text).date()


def _parse_time(text):
    if not text:
        return None
    if isinstance(text, time):
        return text
    return datetime.strptime(text, "%H:%M").time()


def record_to_dict(record) -> Dict:
    data = asdict(record)
    return {key: _iso(value) for key, value in data.items()}


# Поля-даты и поля-времени по типам записей (у проекта start/end — даты,
# у встречи start/end — время, поэтому разбираем по классу, а не по имени).
_DATE_FIELDS = {
    "Project": {"start", "end"},
    "Task": {"planned_date", "deadline", "completed_date"},
    "Meeting": {"date"},
}
_TIME_FIELDS = {
    "Task": {"start_time"},
    "Meeting": {"start", "end"},
}


def record_from_dict(cls, data: Dict):
    """Восстанавливает запись из словаря снимка (резервной копии)."""
    fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    data = {k: v for k, v in data.items() if k in fields}
    cls_name = cls.__name__
    for name in _DATE_FIELDS.get(cls_name, set()) & set(data):
        data[name] = _parse_date(data.get(name))
    for name in _TIME_FIELDS.get(cls_name, set()) & set(data):
        data[name] = _parse_time(data.get(name))
    if cls is Meeting and isinstance(data.get("participant_codes"), str):
        data["participant_codes"] = [
            c for c in (data["participant_codes"] or "").split(";") if c
        ]
    return cls(**data)
