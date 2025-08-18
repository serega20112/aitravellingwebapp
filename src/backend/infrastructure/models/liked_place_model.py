"""SQLAlchemy-модель для понравившихся мест пользователя."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String

from src.backend.infrastructure.db.Base import Base


class LikedPlace(Base):
    """Таблица ``liked_places`` с привязкой к пользователю."""

    __tablename__ = "liked_places"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __repr__(self) -> str:
        """Строковое представление записи места."""
        return f"<LikedPlace {self.city_name} by User ID {self.user_id}>"
