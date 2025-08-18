"""Порт Unit of Work для доменного слоя."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IUnitOfWork(ABC):
    """Порт Unit of Work. Управляет транзакцией и предоставляет репозитории.

    Реализации находятся во внешних слоях (infrastructure/db).
    """

    # Репозитории, работающие внутри текущей транзакции

    @abstractmethod
    def commit(self) -> None:
        """Завершить транзакцию."""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Откатить транзакцию."""
        raise NotImplementedError

    def __enter__(self) -> IUnitOfWork:
        """Войти в контекст Unit of Work."""
        return self

    def __exit__(
        self, exc_type: type | None, exc: Exception | None, tb: object
    ) -> None:
        """Выйти из контекста Unit of Work с автоматическим commit/rollback."""
        if exc:
            self.rollback()
        else:
            self.commit()
