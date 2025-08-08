from src.backend.domain.exceptions.user_exceptions import UserNotFoundError
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.domain.uow.uow_port import IUnitOfWork
from src.backend.domain.services.ai.ai_port import IAIService


class ProfileUseCase:
    def __init__(self, uow: IUnitOfWork, ai_service: IAIService):
        self.uow = uow
        self.ai_service = ai_service

    def get_liked_places(self, user_id: int) -> list[LikedPlace]:
        with self.uow as uow:
            user = uow.user_repo.find_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            return uow.place_repo.get_liked_places_by_user(user_id)

    def get_recommendations(self, user_id: int) -> str:
        liked_places = self.get_liked_places(user_id)
        if not liked_places:
            return "Сначала отметьте любимые места, чтобы получить рекомендации."
        liked_places_names = [p.city_name for p in liked_places]
        liked_places_str = ", ".join(liked_places_names)
        return self.ai_service.get_travel_recommendation(liked_places_str)

    def add_liked_place(
        self, user_id: int, city_name: str, latitude: float, longitude: float
    ):
        # Делегируем добавление в рамках транзакции UoW
        with self.uow as uow:
            # Проверка пользователя
            user = uow.user_repo.find_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            # Идемпотентность по координатам
            liked_places = uow.place_repo.get_liked_places_by_user(user_id)
            for place in liked_places:
                if place.latitude == latitude and place.longitude == longitude:
                    return place
            # Создание
            from src.backend.domain.model.place.liked_place_model import LikedPlace as LP
            new_place = LP(None, user_id, city_name, latitude, longitude)
            return uow.place_repo.add_liked_place(new_place)
