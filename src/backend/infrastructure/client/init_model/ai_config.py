"""
Минимальная конфигурация модели генерации текста.

Содержит параметры провайдера и модели по умолчанию, а также базовые
настройки генерации. Может быть переопределена переменными окружения
или конфигом приложения.
"""

MODEL_CONFIG = {
    "provider": "gpt-oss",
    "model_path": "openai/gpt-oss-120b",
    "temperature": 0.7,
    "top_p": 0.95,
    "do_sample": True,
    "use_chat_template": True,
    "early_stopping": True,
}
