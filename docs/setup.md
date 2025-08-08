# Развертывание и запуск (Windows/Linux)

## Предварительные требования
- Python 3.11+
- Git
- Виртуальное окружение (рекомендуется): venv/virtualenv/conda/poetry — на ваш выбор
- Переменные окружения (см. `.env.example`):
  - SECRET_KEY — секрет Flask
  - GOOGLE_API_KEY — если используете google-generativeai

## 1. Клонирование и создание окружения
```
git clone https://github.com/<your-org>/aitravelling_ddd_structure.git
cd atravelling_ddd_structure
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
```

## 2. Установка зависимостей

### 2.1 Базовые dev-зависимости
```
pip install -r requirements.dev.txt
```

### 2.2 PyTorch (по платформе)
PyTorch не зафиксирован в requirements.dev.txt из-за кроссплатформенных различий. Устанавливайте отдельно:
- CPU (Windows/Linux):
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
- CUDA 12.1 (пример):
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2.3 Зависимости для линтинга (опционально)
```
pip install -r requirements.lint.txt
```

## 3. Миграции БД
```
flask db upgrade
```

## 4. Запуск приложения
```
python main.py
```

После запуска API будет доступен по адресу, указанному в main.py/конфигурации Flask.

## 5. Тесты
```
pytest -q
```

## 6. Полезные параметры
- DEBUG/LOGGING настраиваются через переменные окружения и конфигурацию Flask.
- Для быстрой демонстрации AI-функций можно заменить реальный AIService на «Dummy» через DI в `create_app.py`.
