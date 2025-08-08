from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol

from src.backend.domain.repositories.place.place_repository import PlaceRepository
from src.backend.domain.repositories.user.user_repository import UserRepository


class IUnitOfWork(ABC):
    """Порт Unit of Work. Управляет транзакцией и предоставляет репозитории.
    Реализации находятся во внешних слоях (infrastructure/db).
    """

    # Репозитории, работающие внутри текущей транзакции
    place_repo: PlaceRepository
    user_repo: UserRepository

    @abstractmethod
    def commit(self) -> None:  # завершить транзакцию
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:  # откатить транзакцию
        raise NotImplementedError

    def __enter__(self) -> IUnitOfWork:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.rollback()
        else:
            self.commit()
