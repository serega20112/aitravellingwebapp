from abc import ABC, abstractmethod
from src.backend.domain.model.user.user_model import User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass
