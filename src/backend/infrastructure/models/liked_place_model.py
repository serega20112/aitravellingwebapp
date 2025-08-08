from src.backend.infrastructure.db.Base import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey


class LikedPlace(Base):
    __tablename__ = "liked_places"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __repr__(self):
        return f"<LikedPlace {self.city_name} by User ID {self.user_id}>"
