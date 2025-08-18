"""Схемы Pydantic для данных о местах."""

from pydantic import BaseModel, constr


class PointInfoRequestSchema(BaseModel):
    """Запрос информации о точке по широте/долготе."""

    latitude: float
    longitude: float


class LikedPlaceCreateSchema(BaseModel):
    """Создание избранного места."""

    city_name: constr(min_length=1, max_length=100)
    latitude: float
    longitude: float


class LikedPlaceResponseSchema(BaseModel):
    """Ответ с данными избранного места."""

    id: int
    user_id: int
    city_name: str
    latitude: float
    longitude: float

    class Config:
        """Настройки Pydantic для ORM-режима."""

        from_attributes = True
