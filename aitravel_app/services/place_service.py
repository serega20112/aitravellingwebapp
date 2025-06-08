from aitravel_app.models import LikedPlace, User
from aitravel_app.core.db import db
from aitravel_app.ai.services import get_place_info_from_ai, get_travel_recommendation_from_ai
from aitravel_app.schemas.place_schemas import LikedPlaceCreateSchema
from flask import current_app

class PlaceServiceError(Exception):
    pass

class UserNotFoundError(PlaceServiceError):
    pass

class PlaceService:
    @staticmethod
    def get_info_for_point(latitude: float, longitude: float) -> str:
        return get_place_info_from_ai(latitude, longitude)

    @staticmethod
    def add_liked_place(user_id: int, place_data: LikedPlaceCreateSchema) -> LikedPlace:
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        existing_liked_place = LikedPlace.query.filter_by(
            user_id=user_id,
            latitude=place_data.latitude,
            longitude=place_data.longitude
        ).first()

        if existing_liked_place:
            current_app.logger.info(f"Place {place_data.city_name} at {place_data.latitude},{place_data.longitude} already liked by user {user_id}.")
            return existing_liked_place

        new_liked_place = LikedPlace(
            user_id=user_id,
            city_name=place_data.city_name,
            latitude=place_data.latitude,
            longitude=place_data.longitude
        )
        db.session.add(new_liked_place)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding liked place: {e}")
            raise PlaceServiceError(f"Could not add liked place: {e}")
        return new_liked_place

    @staticmethod
    def get_liked_places_by_user(user_id: int) -> list[LikedPlace]:
        return LikedPlace.query.filter_by(user_id=user_id).order_by(LikedPlace.id.desc()).all()

    @staticmethod
    def generate_recommendations_for_user(user_id: int) -> str:
        liked_places = PlaceService.get_liked_places_by_user(user_id)
        if not liked_places:
            return "Not enough liked places to generate recommendations. Please like some places first!"

        liked_places_names = [place.city_name for place in liked_places]
        liked_places_str = ", ".join(liked_places_names)

        return get_travel_recommendation_from_ai(liked_places_str)
