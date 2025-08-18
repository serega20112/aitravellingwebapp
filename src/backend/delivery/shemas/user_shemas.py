"""Схемы Pydantic для данных о пользователях."""

from pydantic import BaseModel, constr


class UserCreateSchema(BaseModel):
    """Данные для создания пользователя."""

    username: constr(min_length=3, max_length=80)
    password: constr(min_length=6)


class UserResponseSchema(BaseModel):
    """Ответ с краткими данными пользователя."""

    id: int
    username: str

    class Config:
        """Настройки Pydantic для ORM-режима."""

        from_attributes = True
