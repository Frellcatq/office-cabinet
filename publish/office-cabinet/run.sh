#!/bin/zsh
# Запуск рабочего кабинета локально.
# Использование: ./run.sh  (при первом запуске создаёт виртуальное окружение)
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/streamlit run app.py --server.port 8501 --server.headless true
