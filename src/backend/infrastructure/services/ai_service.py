from typing import List, Dict
from flask import current_app
from huggingface_hub import InferenceClient

from src.backend.domain.services.ai.ai_port import IAIService


class AIService(IAIService):
    """
    Сервис ИИ на базе Hugging Face Inference API для туристического ассистента.
    Поддерживает краткие описания мест, рекомендации и чат-диалоги.
    """

    def __init__(self, config: dict | None = None):
        """
        Инициализирует клиента Inference и параметры модели из конфигурации.
        Ожидает ключи: HF_TOKEN, HF_PROVIDER, HF_MODEL.
        """
        self._cfg = config
        self._client: InferenceClient | None = None
        self._model: str | None = None

    def _ensure_client(self) -> InferenceClient:
        """
        Возвращает готовый клиент InferenceClient, создавая его при первом обращении.
        """
        if self._client is not None:
            return self._client
        cfg = self._cfg or current_app.config
        token = cfg.get("HF_TOKEN")
        provider = cfg.get("HF_PROVIDER", "fireworks-ai")
        model = cfg.get("HF_MODEL", "openai/gpt-oss-120b")
        if not token:
            raise RuntimeError("HF_TOKEN не задан в конфигурации")
        self._client = InferenceClient(provider=provider, api_key=token)
        self._model = model
        return self._client

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Возвращает ответ ассистента на список сообщений чата без тематических ограничений.
        """
        if not messages:
            return "Пожалуйста, задайте вопрос."
        client = self._ensure_client()
        system_preamble = {
            "role": "system",
            "content": (
                "Ты — вежливый, лаконичный и полезный помощник. Отвечай по-русски,"
                " будь точен и старайся давать практичные ответы."
            ),
        }
        payload = [system_preamble] + messages
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=payload,
            )
            return completion.choices[0].message["content"] if completion.choices else ""
        except Exception as e:
            current_app.logger.error(f"Ошибка чата ИИ: {e}", exc_info=True)
            return "Не удалось получить ответ. Попробуйте позже."

    def get_place_info(self, latitude: float, longitude: float) -> str:
        """
        Возвращает краткое описание места по координатам на русском языке.
        """
        prompt = (
            f"Координаты: широта {latitude}, долгота {longitude}. "
            f"Дай краткое, интересное и полезное описание для туриста (до 100 слов)."
        )
        client = self._ensure_client()
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты туристический ассистент. Пиши кратко и по делу на русском.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = completion.choices[0].message["content"] if completion.choices else ""
            if not text:
                current_app.logger.warning("Пустой ответ от модели на get_place_info")
                return "Не удалось получить информацию о месте."
            return text
        except Exception as e:
            current_app.logger.error(f"Ошибка генерации get_place_info: {e}", exc_info=True)
            return "Произошла ошибка сервиса ИИ."

    def get_travel_recommendation(self, liked_places_str: str) -> str:
        """
        Возвращает рекомендацию нового места на основе списка понравившихся мест.
        """
        client = self._ensure_client()
        prompt = (
            "Мне нравятся следующие места: "
            + liked_places_str
            + ". Предложи новое направление и кратко объясни выбор (100–150 слов)."
        )
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по путешествиям. Учитывай предпочтения пользователя.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = completion.choices[0].message["content"] if completion.choices else ""
            if not text:
                current_app.logger.warning("Пустой ответ от модели на get_travel_recommendation")
                return "Не удалось получить рекомендации."
            return text
        except Exception as e:
            current_app.logger.error(
                f"Ошибка генерации get_travel_recommendation: {e}", exc_info=True
            )
            return "Произошла ошибка сервиса ИИ."
