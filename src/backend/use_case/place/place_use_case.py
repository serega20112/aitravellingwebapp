from src.backend.domain.exceptions.user_exceptions import UserNotFoundError
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.domain.uow.uow_port import IUnitOfWork
from src.backend.domain.services.ai.ai_port import IAIService


class PlaceUseCase:
    def __init__(self, uow: IUnitOfWork, ai_service: IAIService):
        self.uow = uow
        self.ai_service = ai_service

    def get_info_for_point(self, latitude: float, longitude: float) -> str:
        # Внешний сервис внедрён по интерфейсу (порт)
        return self.ai_service.get_place_info(latitude, longitude)

    def add_liked_place(
        self, user_id: int, city_name: str, latitude: float, longitude: float
    ) -> LikedPlace:
        with self.uow as uow:
            user = uow.user_repo.find_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")

            liked_places = uow.place_repo.get_liked_places_by_user(user_id)
            for place in liked_places:
                if place.latitude == latitude and place.longitude == longitude:
                    return place

            new_place = LikedPlace(
                id=None,
                user_id=user_id,
                city_name=city_name,
                latitude=latitude,
                longitude=longitude,
            )
            added = uow.place_repo.add_liked_place(new_place)
            return added

    def get_liked_places_by_user(self, user_id: int) -> list[LikedPlace]:
        # Чтение вне явной транзакции допустимо, но при необходимости можно обернуть в uow
        with self.uow as uow:
            return uow.place_repo.get_liked_places_by_user(user_id)

    def generate_recommendations_for_user(self, user_id: int) -> str:
        liked_places = self.get_liked_places_by_user(user_id)
        if not liked_places:
            return "Сначала отметьте любимые места, чтобы получить рекомендации."

        liked_places_names = [place.city_name for place in liked_places]
        liked_places_str = ", ".join(liked_places_names)
        return self.ai_service.get_travel_recommendation(liked_places_str)
