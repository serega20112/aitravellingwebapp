# Зависимости и кроссплатформенная установка

## Файлы зависимостей
- `requirements.dev.txt` — зависимости для разработки и запуска проекта (Flask, SQLAlchemy, Pydantic, pytest и т.д.).
- `requirements.lint.txt` — зависимости для линтинга и форматирования (black, flake8, isort, ruff).

Мы избегаем жёсткой фиксации версий, чтобы упростить локальную установку и совместимость. При желании можно заморозить через `pip freeze > requirements.lock.txt`.

## PyTorch/transformers
Библиотека `torch` не входит в `requirements.dev.txt`, потому что её колёса различаются для Windows/Linux и для разных версий CUDA. Устанавливайте отдельно:

- CPU only (Windows/Linux):
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
- CUDA 12.1:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
После этого `transformers` и `huggingface-hub` из dev-зависимостей будут работать корректно.

## Быстрый старт
```
python -m venv .venv
# Win (PowerShell)
. .venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.dev.txt
# (опционально) линтеры
pip install -r requirements.lint.txt

# затем поставьте torch по инструкции выше
```

## Советы для Windows
- Используйте PowerShell от имени администратора при установке крупных библиотек.
- Если столкнулись с ошибками сборки, поставьте билд-инструменты Visual C++.
- Для CUDA убедитесь, что версия драйверов совместима с выбранным колесом.

## Советы для Linux
- Пакетные зависимости (devel headers) для psycopg2 могут потребоваться, если будете использовать системный PostgreSQL клиент.
- При необходимости используйте `python3-venv`, `build-essential`, `libffi-dev`, `libssl-dev`.
