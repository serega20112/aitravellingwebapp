from abc import ABC, abstractmethod


class IAIService(ABC):
    """
    Порт сервиса ИИ для туристического ассистента.
    Предоставляет методы получения краткой информации о месте,
    рекомендаций для путешествий и диалогового чата.
    """

    @abstractmethod
    def get_place_info(self, latitude: float, longitude: float) -> str:
        """Возвращает краткую информацию о месте по координатам."""
        raise NotImplementedError

    @abstractmethod
    def get_travel_recommendation(self, liked_places_str: str) -> str:
        """Возвращает рекомендацию для путешествий на основе списка понравившихся мест."""
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Ведёт диалог в формате чата. На вход список сообщений вида
        {"role": "user|assistant|system", "content": "..."}. Возвращает ответ ассистента.
        """
        raise NotImplementedError
