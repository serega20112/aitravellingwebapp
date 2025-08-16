from typing import List, Dict
import logging
from huggingface_hub import InferenceClient

from src.backend.domain.services.ai.ai_port import IAIService


class AIService(IAIService):
    """
    ИИ‑сервис на Hugging Face Inference API для туристического ассистента.
    Даёт ответы в чате, краткие описания локаций и рекомендации.
    """

    def __init__(self, config: dict | None = None, logger: logging.Logger | None = None):
        """
        Инициализация с конфигом приложения. Используются ключи: HF_TOKEN,
        HF_PROVIDER, HF_MODEL.
        """
        self._cfg = config or {}
        self._client: InferenceClient | None = None
        self._model: str | None = None
        self._logger = logger or logging.getLogger(__name__)

    def _ensure_client(self) -> InferenceClient:
        """Лениво создаёт и возвращает InferenceClient."""
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
        """Ответ ассистента на список сообщений чата."""
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
                            "Ты помощник, который выделяет краткий поисковый запрос по локации. "
                            "Верни только название места/города/региона/адреса на русском или латиницей, "
                            "без дополнительных слов, до 50 символов."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )
            query = completion.choices[0].message["content"].strip() if completion.choices else ""
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
                        "content": "Ты туристический ассистент. Пиши кратко и по делу на русском.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = completion.choices[0].message["content"] if completion.choices else ""
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
                    f"Учитывая, что вам нравятся: {liked_places_str}. "
                    f"{base_text}"
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
            text = completion.choices[0].message["content"] if completion.choices else ""
            if not text:
                self._logger.warning(
                    "Пустой ответ от модели на get_place_info_with_address_and_prefs"
                )
                return "Не удалось получить информацию о месте."
            return text
        except Exception as e:
            self._logger.error(
                f"Ошибка генерации get_place_info_with_address_and_prefs: {e}", exc_info=True
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
            text = completion.choices[0].message["content"] if completion.choices else ""
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
                        "content": "Ты эксперт по путешествиям. Учитывай предпочтения пользователя.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            text = completion.choices[0].message["content"] if completion.choices else ""
            if not text:
                self._logger.warning("Пустой ответ от модели на get_travel_recommendation")
                return "Не удалось получить рекомендации."
            return text
        except Exception as e:
            self._logger.error(
                f"Ошибка генерации get_travel_recommendation: {e}", exc_info=True
            )
            return "Произошла ошибка сервиса ИИ."
