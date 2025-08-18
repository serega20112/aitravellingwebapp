"""SQLAlchemy-реализация репозитория мест."""

from sqlalchemy.orm import Session

from src.backend.domain.model.place.liked_place_model import (
    LikedPlace as DomainLikedPlace,
)
from src.backend.domain.repositories import PlaceRepository
from src.backend.infrastructure.models.liked_place_model import (
    LikedPlace as DbLikedPlace,
)


class SqlAlchemyPlaceRepository(PlaceRepository):
    """Репозиторий для работы с понравившимися местами через SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Инициализировать репозиторий с сессией SQLAlchemy.

        Args:
            session: Сессия SQLAlchemy для выполнения запросов к БД
        """
        # Сессия внедряется извне (Unit of Work управляет транзакцией)
        self.session = session

    def add_liked_place(self, place: DomainLikedPlace) -> DomainLikedPlace:
        """Добавить понравившееся место в базу данных.

        Args:
            place: Доменная модель понравившегося места

        Returns:
            Сохранённая доменная модель с присвоенным ID
        """
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
        """Получить все понравившиеся места пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Список доменных моделей понравившихся мест
        """
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
