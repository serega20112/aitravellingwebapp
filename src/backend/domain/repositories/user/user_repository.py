"""Порт репозитория пользователей для доменного слоя."""

from abc import ABC, abstractmethod

from src.backend.domain.model.user.user_model import User


class UserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    def add(self, user: User) -> User:
        """Добавить пользователя и вернуть его."""

    @abstractmethod
    def find_by_username(self, username: str) -> User | None:
        """Найти пользователя по имени или вернуть None."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        """Найти пользователя по идентификатору или вернуть None."""
