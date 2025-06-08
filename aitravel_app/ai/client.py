import google.generativeai as genai
from flask import current_app

def get_google_ai_model():
    api_key = current_app.config.get('GOOGLE_API_KEY')
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_PLACEHOLDER": # Пример плейсхолдера
        current_app.logger.error("Google API key is not configured or is a placeholder.")
        raise ValueError("GOOGLE_API_KEY not configured or is a placeholder. Please set it in your .env file.")
    
    try:
        genai.configure(api_key=api_key)
        # Вы можете выбрать конкретную модель здесь, если это необходимо,
        # или передать имя модели в сервисные функции.
        # Например, model = genai.GenerativeModel('gemini-pro')
        # Для простоты, пока возвращаем сконфигурированный модуль genai.
        # Сервисы будут вызывать genai.GenerativeModel() сами.
        return genai # Возвращаем сконфигурированный модуль
    except Exception as e:
        current_app.logger.error(f"Failed to configure Google AI SDK: {e}")
        raise ValueError(f"Failed to configure Google AI SDK: {e}")

