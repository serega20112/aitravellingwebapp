from src.backend.domain.repositories.user.user_repository import UserRepository
from src.backend.domain.model.user.user_model import User
from src.backend.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentials,
)
from src.backend.utils.security.password_utils import hash_password


class UserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, username: str, password: str) -> User:
        if self.user_repo.find_by_username(username):
            raise UserAlreadyExistsError("Пользователь с таким именем уже существует")

        password_hash = hash_password(password)
        user = User(user_id=None, username=username, password_hash=password_hash)
        return self.user_repo.add(user)

    def authenticate_user(self, username: str, password: str) -> User:
        user = self.user_repo.find_by_username(username)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        if not user.check_password(password):
            raise InvalidCredentials("Неверный пароль")

        return user
