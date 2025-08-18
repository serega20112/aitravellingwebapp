"""AI service implementation using Hugging Face Inference API.

This module provides AI-powered functionality for the travel application,
including chat responses, location descriptions, and travel recommendations.
"""

import logging
from typing import Dict, List, Optional

from huggingface_hub import InferenceClient

from src.backend.domain.services.ai.ai_port import IAIService


class AIService(IAIService):
    """AI service implementation using Hugging Face Inference API.

    This service provides AI-powered functionality for travel assistance,
    including chat responses, location information, and personalized
    travel recommendations.

    Attributes:
        _cfg: Configuration dictionary containing API credentials
        _client: Hugging Face InferenceClient instance
        _model: Model name to use for inference
        _logger: Logger instance for error tracking
    """

    def __init__(
        self, config: Optional[Dict] = None, logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize AIService with configuration and logger.

        Args:
            config: Configuration dictionary with HF_TOKEN, HF_PROVIDER, HF_MODEL
            logger: Logger instance for error tracking
        """
        self._cfg = config or {}
        self._client: Optional[InferenceClient] = None
        self._model: Optional[str] = None
        self._logger = logger or logging.getLogger(__name__)

    def _ensure_client(self) -> InferenceClient:
        """Lazily create and return InferenceClient instance.

        Returns:
            Configured InferenceClient instance

        Raises:
            RuntimeError: If HF_TOKEN is not configured
        """
        if self._client is not None:
            return self._client
        cfg = self._cfg
        token = cfg.get("HF_TOKEN")
        provider = cfg.get("HF_PROVIDER", "fireworks-ai")
        model = cfg.get("HF_MODEL", "openai/gpt-oss-120b")
        if not token:
            raise RuntimeError("HF_TOKEN не задан в конфигурации")
        self._client = InferenceClient(provider=provider, api_key=token)
        self._model = model
        return self._client

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate AI assistant response to chat messages.

        Args:
            messages: List of chat messages with role and content

        Returns:
            AI-generated response text
        """
        if not messages:
            return "Пожалуйста, задайте вопрос."
        client = self._ensure_client()
        system_preamble = {
            "role": "system",
            "content": (
                "Ты — вежливый, лаконичный и полезный помощник. "
                "Отвечай по-русски, будь точен и старайся давать "
                "практичные ответы."
            ),
        }
        payload = [system_preamble] + messages
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=payload,
            )
            if completion.choices:
                return completion.choices[0].message["content"]
            return ""
        except Exception as e:
            self._logger.error(f"Ошибка чата ИИ: {e}", exc_info=True)
            return "Не удалось получить ответ. Попробуйте позже."

    def normalize_location_query(self, user_text: str) -> str:
        """Кратко нормализует запрос о локации для геокодинга (до 50 символов)."""
        text = (user_text or "").strip()
        if not text:
            return ""
        client = self._ensure_client()
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты помощник, который выделяет краткий поисковый запрос по "
                            "локации. Верни только название места/города/региона/адреса "
                            "на русском или латиницей, без дополнительных слов, до 50 "
                            "символов."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )
            query = (
                completion.choices[0].message["content"].strip()
                if completion.choices
                else ""
            )
            return query[:50]
        except Exception as e:
            self._logger.error(f"Ошибка normalize_location_query: {e}", exc_info=True)
            return ""

    def get_place_info(self, latitude: float, longitude: float) -> str:
        """Краткое описание места по координатам (на русском)."""
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
                        "content": (
                            "Ты туристический ассистент. Пиши кратко и по делу на "
                            "русском."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = (
                completion.choices[0].message["content"] if completion.choices else ""
            )
            if not text:
                self._logger.warning("Пустой ответ от модели на get_place_info")
                return "Не удалось получить информацию о месте."
            return text
        except Exception as e:
            self._logger.error(f"Ошибка генерации get_place_info: {e}", exc_info=True)
            return "Произошла ошибка сервиса ИИ."

    def get_place_info_with_address_and_prefs(
        self,
        address: str | None,
        latitude: float,
        longitude: float,
        liked_places_str: str | None = None,
    ) -> str:
        """Описание места по адресу OSM и координатам с учётом предпочтений."""
        if not address:
            base_text = self.get_place_info(latitude, longitude)
            if liked_places_str:
                return (
                    f"Учитывая, что вам нравятся: {liked_places_str}. " f"{base_text}"
                )
            return base_text

        client = self._ensure_client()
        sys = "Ты туристический ассистент. Пиши по-русски, лаконично, без воды."
        if liked_places_str:
            sys += (
                " Учитывай предпочтения пользователя (ему нравятся: "
                + liked_places_str
                + ") при выборе акцентов: климат, активности, стиль места."
            )
        user_prompt = (
            "Вот данные о месте. Сначала используй адрес, затем координаты. "
            "Сформируй краткое, содержательное описание для туриста (до 100 слов), "
            "упомяни ориентиры, район/город и чем интересно это место.\n\n"
            f"Адрес (OSM): {address}\n"
            f"Координаты: широта {latitude}, долгота {longitude}"
        )
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = (
                completion.choices[0].message["content"] if completion.choices else ""
            )
            if not text:
                self._logger.warning(
                    "Пустой ответ от модели на get_place_info_with_address_and_prefs"
                )
                return "Не удалось получить информацию о месте."
            return text
        except Exception as e:
            self._logger.error(
                f"Ошибка генерации get_place_info_with_address_and_prefs: {e}",
                exc_info=True,
            )
            return "Произошла ошибка сервиса ИИ."

    def get_place_info_with_address(
        self, address: str | None, latitude: float, longitude: float
    ) -> str:
        """Краткое описание места по адресу OSM и координатам."""
        if not address:
            return self.get_place_info(latitude, longitude)

        client = self._ensure_client()
        user_prompt = (
            "Вот данные о месте. Сначала используй адрес, затем координаты. "
            "Сформируй краткое, содержательное описание для туриста (до 100 слов), "
            "упомяни ключевые ориентиры, район/город и чем интересно это место.\n\n"
            f"Адрес (OSM): {address}\n"
            f"Координаты: широта {latitude}, долгота {longitude}"
        )
        try:
            completion = client.chat.completions.create(
                model=self._model or "openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты туристический ассистент. Пиши по-русски, лаконично, "
                            "без воды. Если адрес точный — опирайся на него."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = (
                completion.choices[0].message["content"] if completion.choices else ""
            )
            if not text:
                self._logger.warning(
                    "Пустой ответ от модели на get_place_info_with_address"
                )
                return "Не удалось получить информацию о месте."
            return text
        except Exception as e:
            self._logger.error(
                f"Ошибка генерации get_place_info_with_address: {e}", exc_info=True
            )
            return "Произошла ошибка сервиса ИИ."

    def get_travel_recommendation(self, liked_places_str: str) -> str:
        """Рекомендация направления на основе понравившихся мест."""
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
                        "content": (
                            "Ты эксперт по путешествиям. Учитывай предпочтения "
                            "пользователя."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = (
                completion.choices[0].message["content"] if completion.choices else ""
            )
            if not text:
                self._logger.warning(
                    "Пустой ответ от модели на get_travel_recommendation"
                )
                return "Не удалось получить рекомендации."
            return text
        except Exception as e:
            self._logger.error(
                f"Ошибка генерации get_travel_recommendation: {e}", exc_info=True
            )
            return "Произошла ошибка сервиса ИИ."
