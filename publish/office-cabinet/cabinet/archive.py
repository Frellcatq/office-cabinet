# -*- coding: utf-8 -*-
"""Резервная копия сеанса: ZIP с манифестом и оригиналами материалов.

Архив собирается и читается полностью в памяти, без извлечения на диск.
"""
from __future__ import annotations

import io
import json
import zipfile
from typing import Dict, List, Optional, Tuple

from .store import Workspace

MANIFEST_NAME = "manifest.json"
MATERIALS_DIR = "materials"
APP_NAME = "Рабочий кабинет «Северная линия»"

MAX_MATERIAL_FILE_BYTES = 5 * 1024 * 1024    # 5 МБ на файл
MAX_MATERIAL_TOTAL_BYTES = 20 * 1024 * 1024  # 20 МБ всего
MAX_ARCHIVE_BYTES = 60 * 1024 * 1024         # защитный предел для самого архива


def build_zip(workspace: Workspace) -> bytes:
    """Собирает резервную копию: манифест + оригиналы материалов.

    Включает все данные и материалы независимо от фильтров.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            MANIFEST_NAME,
            json.dumps(workspace.to_snapshot(), ensure_ascii=False, indent=2),
        )
        for document in workspace.documents:
            content = workspace.files.get(document.key, b"")
            if content:
                archive.writestr(
                    f"{MATERIALS_DIR}/{document.key}/{document.name}", content
                )
    return buffer.getvalue()


def validate_workspace(workspace: Workspace) -> List[str]:
    """Проверяет коды, уникальность и связи записей рабочего пространства."""
    errors: List[str] = []

    def check_unique(codes: List[str], label: str) -> None:
        seen = set()
        for code in codes:
            if code in seen:
                errors.append(f"Код {code} встречается в разделе «{label}» больше одного раза.")
            seen.add(code)

    check_unique([e.code for e in workspace.employees], "Сотрудники")
    check_unique([p.code for p in workspace.projects], "Проекты")
    check_unique([t.code for t in workspace.tasks], "Задачи")
    check_unique([m.code for m in workspace.meetings], "Встречи")

    employee_codes = {e.code for e in workspace.employees}
    project_codes = {p.code for p in workspace.projects}
    meeting_codes = {m.code for m in workspace.meetings}
    task_codes = {t.code for t in workspace.tasks}

    for project in workspace.projects:
        if project.owner_code and project.owner_code not in employee_codes:
            errors.append(f"Проект {project.code}: владелец {project.owner_code} не найден.")
    for task in workspace.tasks:
        if task.project_code not in project_codes:
            errors.append(f"Задача {task.code}: проект {task.project_code} не найден.")
        if task.assignee_code and task.assignee_code not in employee_codes:
            errors.append(f"Задача {task.code}: ответственный {task.assignee_code} не найден.")
    for meeting in workspace.meetings:
        if meeting.project_code not in project_codes:
            errors.append(f"Встреча {meeting.code}: проект {meeting.project_code} не найден.")
        for participant in meeting.participant_codes:
            if participant not in employee_codes:
                errors.append(f"Встреча {meeting.code}: участник {participant} не найден.")
    for document in workspace.documents:
        if document.project_code and document.project_code not in project_codes:
            errors.append(f"Материал «{document.name}»: проект {document.project_code} не найден.")
        if document.meeting_code and document.meeting_code not in meeting_codes:
            errors.append(f"Материал «{document.name}»: встреча {document.meeting_code} не найдена.")
        if document.task_code and document.task_code not in task_codes:
            errors.append(f"Материал «{document.name}»: задача {document.task_code} не найдена.")
    return errors


def read_zip(data: bytes) -> Tuple[Optional[dict], Dict[str, bytes], List[str]]:
    """Читает архив в памяти и проверяет структуру, коды, связи и лимиты.

    Возвращает (манифест, файлы материалов, ошибки). При ошибках манифест
    равен None — вызывающий код оставляет текущие данные без изменений.
    """
    if len(data) > MAX_ARCHIVE_BYTES:
        return None, {}, ["Архив больше 60 МБ — проверьте, что это резервная копия кабинета."]
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return None, {}, ["Не удалось открыть файл: ожидается ZIP-архив резервной копии."]

    names = archive.namelist()
    if MANIFEST_NAME not in names:
        return None, {}, ["В архиве нет manifest.json — это не резервная копия кабинета."]
    try:
        manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, {}, ["manifest.json повреждён или имеет неверный формат."]

    if manifest.get("app") != APP_NAME:
        return None, {}, ["Это архив другого приложения: манифест не совпадает с кабинетом."]
    if manifest.get("format_version") != 1:
        return None, {}, ["Неизвестная версия формата резервной копии."]

    candidate = Workspace()
    try:
        candidate.load_snapshot(manifest)
    except Exception as error:  # повреждённые записи манифеста
        return None, {}, [f"Манифест содержит некорректные записи: {error}."]

    errors = validate_workspace(candidate)

    files: Dict[str, bytes] = {}
    for document in candidate.documents:
        prefix = f"{MATERIALS_DIR}/{document.key}/"
        members = [n for n in names if n.startswith(prefix) and not n.endswith("/")]
        if not members:
            errors.append(f"В архиве нет файла материала «{document.name}».")
            continue
        if len(members) > 1:
            errors.append(f"Для материала «{document.name}» в архиве несколько файлов.")
            continue
        content = archive.read(members[0])
        if len(content) > MAX_MATERIAL_FILE_BYTES:
            errors.append(f"Материал «{document.name}» больше 5 МБ.")
            continue
        files[document.key] = content

    total = sum(len(content) for content in files.values())
    if total > MAX_MATERIAL_TOTAL_BYTES:
        errors.append("Суммарный размер материалов в архиве больше 20 МБ.")

    if errors:
        return None, {}, errors
    return manifest, files, []
