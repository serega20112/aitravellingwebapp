"""Порт репозитория мест (Place) для доменного слоя."""

from abc import ABC, abstractmethod

from src.backend.domain.model.place.liked_place_model import LikedPlace


class PlaceRepository(ABC):
    """Интерфейс репозитория для работы с понравившимися местами."""

    @abstractmethod
    def add_liked_place(self, place: LikedPlace) -> LikedPlace:
        """Добавить понравившееся место и вернуть его."""

    @abstractmethod
    def get_liked_places_by_user(self, user_id: int) -> list[LikedPlace]:
        """Вернуть список понравившихся мест пользователя."""
