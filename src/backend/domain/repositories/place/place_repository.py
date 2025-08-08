from abc import ABC, abstractmethod
from src.backend.domain.model.place.liked_place_model import LikedPlace


class PlaceRepository(ABC):
    @abstractmethod
    def add_liked_place(self, place: LikedPlace) -> LikedPlace:
        pass

    @abstractmethod
    def get_liked_places_by_user(self, user_id: int) -> list[LikedPlace]:
        pass
