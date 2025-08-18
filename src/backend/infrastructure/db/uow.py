"""Реализация Unit of Work на базе SQLAlchemy для инфраструктурного слоя."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.backend.domain.uow.uow_port import IUnitOfWork
from src.backend.infrastructure.db.session import SessionLocal
from src.backend.infrastructure.repository import (
    SqlAlchemyPlaceRepository,
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Unit of Work на базе SQLAlchemy.

    Создаёт сессию, предоставляет репозитории и управляет транзакцией.
    """

    def __init__(self) -> None:
        """Инициализировать Unit of Work."""
        self.session: Session | None = None
        self.place_repo = None
        self.user_repo = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        """Войти в контекст и создать сессию."""
        self.session = SessionLocal()
        # Репозитории, привязанные к одной сессии
        self.place_repo = SqlAlchemyPlaceRepository(self.session)
        self.user_repo = SqlAlchemyUserRepository(self.session)
        return self

    def __exit__(
        self, exc_type: type | None, exc: Exception | None, tb: object
    ) -> None:
        """Выйти из контекста с commit/rollback и закрытием сессии."""
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        """Зафиксировать изменения в базе данных."""
        if self.session is None:
            return
        self.session.commit()

    def rollback(self) -> None:
        """Отменить все изменения в текущей транзакции."""
        if self.session is None:
            return
        self.session.rollback()
