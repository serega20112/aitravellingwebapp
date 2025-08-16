from __future__ import annotations

from sqlalchemy.orm import Session

from src.backend.domain.uow.uow_port import IUnitOfWork
from src.backend.infrastructure.repository.place import SqlAlchemyPlaceRepository
from src.backend.infrastructure.repository.user import SqlAlchemyUserRepository
from src.backend.infrastructure.db.session import SessionLocal


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Unit of Work на базе SQLAlchemy.
    Создаёт сессию, предоставляет репозитории и управляет транзакцией.
    """

    def __init__(self) -> None:
        self.session: Session | None = None
        self.place_repo = None
        self.user_repo = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        self.session = SessionLocal()
        # Репозитории, привязанные к одной сессии
        self.place_repo = SqlAlchemyPlaceRepository(self.session)
        self.user_repo = SqlAlchemyUserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
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
        if self.session is None:
            return
        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            return
        self.session.rollback()
