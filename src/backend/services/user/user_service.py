import logging
from typing import Dict

from src.backend.use_case.user.user_use_case import UserUseCase
from src.backend.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.backend.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentials,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserService:
    def __init__(self):
        # Без заранее созданного репозитория: работаем через Unit of Work на каждый вызов
        pass

    def register_user(self, username: str, password: str):
        """Регистрация пользователя через UoW и UserUseCase."""
        try:
            with SqlAlchemyUnitOfWork() as uow:
                use_case = UserUseCase(user_repo=uow.user_repo)
                user = use_case.register_user(username, password)
                logger.info(f"User registered: {username}")
                return user
        except UserAlreadyExistsError as e:
            logger.warning(f"Registration failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during user registration")
            raise RuntimeError("Ошибка регистрации. Попробуйте позже.") from e

    def authenticate_user(self, username: str, password: str):
        """Аутентификация пользователя через UoW и UserUseCase."""
        try:
            with SqlAlchemyUnitOfWork() as uow:
                use_case = UserUseCase(user_repo=uow.user_repo)
                user = use_case.authenticate_user(username, password)
                logger.info(f"User authenticated: {username}")
                return user
        except (UserNotFoundError, InvalidCredentials) as e:
            logger.warning(f"Authentication failed for user '{username}': {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during authentication")
            raise RuntimeError("Ошибка аутентификации. Попробуйте позже.") from e
