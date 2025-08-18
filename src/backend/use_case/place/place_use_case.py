"""Place use case module for managing user's favorite places and recommendations.

This module implements the core business logic for place-related operations
following Domain-Driven Design principles.
"""

from typing import List

from src.backend.domain.exceptions.user_exceptions import UserNotFoundError
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.domain.services.ai.ai_port import IAIService
from src.backend.domain.uow.uow_port import IUnitOfWork


class PlaceUseCase:
    """Use case for managing user's favorite places and AI-powered recommendations.

    This class encapsulates all business logic related to places, including
    adding liked places, retrieving user preferences, and generating
    AI-powered travel recommendations.

    Attributes:
        uow: Unit of Work for managing database transactions
        ai_service: AI service for generating place information and recommendations
    """

    def __init__(self, uow: IUnitOfWork, ai_service: IAIService) -> None:
        """Initialize PlaceUseCase with required dependencies.

        Args:
            uow: Unit of Work implementation for data persistence
            ai_service: AI service implementation for place information
        """
        self.uow = uow
        self.ai_service = ai_service

    def get_info_for_point(self, latitude: float, longitude: float) -> str:
        """Get AI-generated information about a specific location.

        Args:
            latitude: Geographic latitude coordinate
            longitude: Geographic longitude coordinate

        Returns:
            AI-generated description of the location
        """
        return self.ai_service.get_place_info(latitude, longitude)

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
            added = uow.place_repo.add_liked_place(new_place)
            return added

    def get_liked_places_by_user(self, user_id: int) -> List[LikedPlace]:
        """Retrieve all places liked by a specific user.

        Args:
            user_id: ID of the user whose liked places to retrieve

        Returns:
            List of liked places for the user
        """
        with self.uow as uow:
            return uow.place_repo.get_liked_places_by_user(user_id)

    def generate_recommendations_for_user(self, user_id: int) -> str:
        """Generate AI-powered travel recommendations based on user preferences.

        Args:
            user_id: ID of the user to generate recommendations for

        Returns:
            AI-generated travel recommendations as text
        """
        liked_places = self.get_liked_places_by_user(user_id)
        if not liked_places:
            return "Сначала отметьте любимые места, чтобы получить рекомендации."

        liked_places_names = [place.city_name for place in liked_places]
        liked_places_str = ", ".join(liked_places_names)
        return self.ai_service.get_travel_recommendation(liked_places_str)
