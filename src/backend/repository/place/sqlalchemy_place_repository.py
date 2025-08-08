from src.backend.domain.model.place.liked_place_model import (
    LikedPlace as DomainLikedPlace,
)
from src.backend.domain.repositories.place.place_repository import PlaceRepository
from src.backend.infrastructure.models.liked_place_model import (
    LikedPlace as DbLikedPlace,
)


class SqlAlchemyPlaceRepository(PlaceRepository):
    def __init__(self, session):
        # Сессия внедряется извне (Unit of Work управляет транзакцией)
        self.session = session

    def add_liked_place(self, place: DomainLikedPlace) -> DomainLikedPlace:
        db_place = DbLikedPlace(
            user_id=place.user_id,
            city_name=place.city_name,
            latitude=place.latitude,
            longitude=place.longitude,
        )
        self.session.add(db_place)
        place.id = db_place.id
        return place

    def get_liked_places_by_user(self, user_id: int) -> list[DomainLikedPlace]:
        db_places = (
            self.session.query(DbLikedPlace)
            .filter_by(user_id=user_id)
            .order_by(DbLikedPlace.id.desc())
            .all()
        )
        return [
            DomainLikedPlace(
                id=p.id,
                user_id=p.user_id,
                city_name=p.city_name,
                latitude=p.latitude,
                longitude=p.longitude,
            )
            for p in db_places
        ]
