"""Profile use case module for managing user profiles and preferences.

This module implements the core business logic for user profile operations
following Domain-Driven Design principles.
"""

from typing import List

from src.backend.domain.exceptions.user_exceptions import UserNotFoundError
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.domain.services.ai.ai_port import IAIService
from src.backend.domain.uow.uow_port import IUnitOfWork


class ProfileUseCase:
    """Use case for managing user profiles and travel preferences.

    This class encapsulates all business logic related to user profiles,
    including managing liked places and generating personalized recommendations.

    Attributes:
        uow: Unit of Work for managing database transactions
        ai_service: AI service for generating recommendations
    """

    def __init__(self, uow: IUnitOfWork, ai_service: IAIService) -> None:
        """Initialize ProfileUseCase with required dependencies.

        Args:
            uow: Unit of Work implementation for data persistence
            ai_service: AI service implementation for recommendations
        """
        self.uow = uow
        self.ai_service = ai_service

    def get_liked_places(self, user_id: int) -> List[LikedPlace]:
        """Retrieve all places liked by a specific user.

        Args:
            user_id: ID of the user whose liked places to retrieve

        Returns:
            List of liked places for the user

        Raises:
            UserNotFoundError: If user with given ID doesn't exist
        """
        with self.uow as uow:
            user = uow.user_repo.find_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            return uow.place_repo.get_liked_places_by_user(user_id)

    def get_recommendations(self, user_id: int) -> str:
        """Generate AI-powered travel recommendations for a user.

        Args:
            user_id: ID of the user to generate recommendations for

        Returns:
            AI-generated travel recommendations as text
        """
        liked_places = self.get_liked_places(user_id)
        if not liked_places:
            return "Сначала отметьте любимые места, чтобы получить рекомендации."
        liked_places_names = [p.city_name for p in liked_places]
        liked_places_str = ", ".join(liked_places_names)
        return self.ai_service.get_travel_recommendation(liked_places_str)

    def add_liked_place(
        self, user_id: int, city_name: str, latitude: float, longitude: float
    ) -> LikedPlace:
        """Add a place to user's favorites or return existing if already added.

        Args:
            user_id: ID of the user adding the place
            city_name: Name or description of the place
            latitude: Geographic latitude coordinate
            longitude: Geographic longitude coordinate

        Returns:
            The liked place object (new or existing)

        Raises:
            UserNotFoundError: If user with given ID doesn't exist
        """
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
            return uow.place_repo.add_liked_place(new_place)
