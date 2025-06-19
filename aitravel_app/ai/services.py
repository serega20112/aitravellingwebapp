from .client import get_google_ai_model
from flask import current_app


DEFAULT_GOOGLE_MODEL_NAME = 'gemini-1.5-flash-latest'


def get_place_info_from_ai(latitude: float, longitude: float) -> str:
    try:
        genai_configured_module = get_google_ai_model() # Получаем сконфигурированный модуль
        model = genai_configured_module.GenerativeModel(DEFAULT_GOOGLE_MODEL_NAME)
        
        prompt = f"You are a helpful travel assistant. Provide concise and interesting information about the location at latitude {latitude}, longitude {longitude}. Keep it under 100 words. You will give me an answer on Russian language(на русском отвечаешь без уточнения на каком языке говоришь)"
        
        response = model.generate_content(prompt)
        
        # Проверка на наличие блокировок или ошибок в ответе
        if not response.candidates or not response.candidates[0].content.parts:
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                current_app.logger.warning(f"Google AI content generation blocked for place info. Reason: {block_reason}")
                return f"Could not retrieve information: Content generation was blocked (Reason: {block_reason}). Please try a different query or location."
             current_app.logger.warning("Google AI returned an empty response for place info.")
             return "Could not retrieve information: AI returned an empty response."

        return response.text.strip()
    except ValueError as ve: # Ошибка конфигурации ключа
        current_app.logger.error(f"AI Service (Google) Configuration Error: {ve}")
        return "AI service is not configured. Please check API key."
    except Exception as e:
        current_app.logger.error(f"Google AI API error for place info: {e}", exc_info=True)
        # Попытка извлечь более детальную информацию об ошибке, если это google.api_core.exceptions
        error_message = str(e)
        if hasattr(e, 'message'): # Для некоторых ошибок Google
            error_message = e.message
        return f"Could not retrieve information at this time due to an AI service error: {error_message}"

def get_travel_recommendation_from_ai(liked_places_str: str) -> str:
    try:
        genai_configured_module = get_google_ai_model() # Получаем сконфигурированный модуль
        model = genai_configured_module.GenerativeModel(DEFAULT_GOOGLE_MODEL_NAME)
        
        prompt = f"You are a travel recommendation expert. Based on the list of liked places: {liked_places_str}. Can you recommend a new travel destination for me and briefly explain why (around 100-150 words)?Прошу тебя писать на русском языке"
        
        response = model.generate_content(prompt)

        if not response.candidates or not response.candidates[0].content.parts:
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                current_app.logger.warning(f"Google AI content generation blocked for recommendations. Reason: {block_reason}")
                return f"Could not generate recommendations: Content generation was blocked (Reason: {block_reason}). Please try adjusting your liked places."
            current_app.logger.warning("Google AI returned an empty response for recommendations.")
            return "Could not generate recommendations: AI returned an empty response."

        return response.text.strip()
    except ValueError as ve: # Ошибка конфигурации ключа
        current_app.logger.error(f"AI Service (Google) Configuration Error: {ve}")
        return "AI service is not configured. Please check API key."
    except Exception as e:
        current_app.logger.error(f"Google AI API error for recommendation: {e}", exc_info=True)
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        return f"Could not generate recommendations at this time due to an AI service error: {error_message}"
