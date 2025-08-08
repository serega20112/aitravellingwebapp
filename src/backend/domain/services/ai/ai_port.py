from abc import ABC, abstractmethod


class IAIService(ABC):
    """
    Порт (абстракция) для AI-сервиса генерации текста/рекомендаций.
    Реализации должны располагаться во внешних слоях (infrastructure/services).
    """

    @abstractmethod
    def get_place_info(self, latitude: float, longitude: float) -> str:
        """Возвращает краткую информацию о месте по координатам."""
        raise NotImplementedError

    @abstractmethod
    def get_travel_recommendation(self, liked_places_str: str) -> str:
        """Возвращает рекомендацию для путешествий на основе списка понравившихся мест."""
        raise NotImplementedError
