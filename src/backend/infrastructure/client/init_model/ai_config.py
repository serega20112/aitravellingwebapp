"""
Модуль конфигурации модели генерации текста.

Содержит параметры, необходимые для инициализации и настройки модели,
используемой в проекте (например, GPT-OSS, OpenAI, Gemini и др.).

Переменные:
    MODEL_CONFIG (dict): Словарь параметров модели.

Ключи MODEL_CONFIG:
    - provider (str): Название провайдера модели
        (например, "gpt-oss", "gemini", "openai").
    - model_path (str): Hugging Face ID или путь к локальным весам модели.
    - max_new_tokens (int): Максимальное количество новых токенов при генерации.
    - temperature (float): Температура выборки (чем выше, тем креативнее).
    - top_p (float): Порог вероятности для nucleus sampling.
    - do_sample (bool): Использовать ли стохастическую генерацию.
    - use_chat_template (bool): Применять ли шаблон диалога токенизатора.
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
