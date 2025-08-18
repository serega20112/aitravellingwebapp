"""Сервис геокодинга на базе OpenStreetMap Nominatim API."""

import logging
from typing import Any, Dict, Optional

import requests


class GeocodingService:
    """Сервис реверс‑геокодинга на базе OpenStreetMap Nominatim.

    Возвращает нормализованный адрес по координатам.
    ВАЖНО: согласно политике Nominatim требуется корректный User-Agent и
    желательно email. Настраивается через конфиг: NOMINATIM_BASE_URL,
    NOMINATIM_USER_AGENT, NOMINATIM_EMAIL.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        email: Optional[str] = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Инициализировать сервис геокодинга.

        Args:
            base_url: Базовый URL Nominatim API
            user_agent: User-Agent для запросов
            email: Email для идентификации (рекомендуется)
            logger: Логгер для записи ошибок
        """
        self.base_url = base_url or "https://nominatim.openstreetmap.org"
        self.user_agent = user_agent or "aitravel-app/1.0"
        self.email = email
        self._logger = logger or logging.getLogger(__name__)

    def reverse_geocode(
        self, latitude: float, longitude: float, lang: str = "ru"
    ) -> Dict[str, Any]:
        """Выполняет реверс‑геокодинг по координатам.

        Возвращает словарь с полями:
        - display_name: str | None
        - address: dict | None
        - raw: dict (исходный ответ)
        """
        params = {
            "format": "jsonv2",
            "lat": latitude,
            "lon": longitude,
            "addressdetails": 1,
            "accept-language": lang,
        }
        if self.email:
            params["email"] = self.email

        headers = {
            "User-Agent": self.user_agent,
        }

        url = f"{self.base_url}/reverse"
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {
                "display_name": data.get("display_name"),
                "address": data.get("address"),
                "raw": data,
            }
        except Exception as e:
            self._logger.error(f"Ошибка Nominatim reverse: {e}", exc_info=True)
            return {
                "display_name": None,
                "address": None,
                "raw": {"error": str(e)},
            }

    def search(self, query: str, lang: str = "ru", limit: int = 1) -> Dict[str, Any]:
        """Прямой геокодинг: текстовый запрос -> список совпадений.

        Возвращает первый результат с полями:
        - display_name: str | None
        - lat: float | None
        - lon: float | None
        - raw: dict | None
        """
        params = {
            "format": "jsonv2",
            "q": query,
            "limit": limit,
            "addressdetails": 1,
            "accept-language": lang,
        }
        if self.email:
            params["email"] = self.email

        headers = {
            "User-Agent": self.user_agent,
        }

        url = f"{self.base_url}/search"
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            arr = resp.json() or []
            first = arr[0] if arr else None
            if not first:
                return {
                    "display_name": None,
                    "lat": None,
                    "lon": None,
                    "raw": {"results": []},
                }
            lat = float(first.get("lat")) if first.get("lat") is not None else None
            lon = float(first.get("lon")) if first.get("lon") is not None else None
            return {
                "display_name": first.get("display_name"),
                "lat": lat,
                "lon": lon,
                "raw": first,
            }
        except Exception as e:
            self._logger.error(f"Ошибка Nominatim search: {e}", exc_info=True)
            return {
                "display_name": None,
                "lat": None,
                "lon": None,
                "raw": {"error": str(e)},
            }
