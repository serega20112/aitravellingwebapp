"""Сервис для работы с пользователями (прикладной слой)."""

import logging

from src.backend.domain.exceptions.user_exceptions import (
    InvalidCredentials,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.backend.domain.model.user.user_model import User
from src.backend.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.backend.use_case.user.user_use_case import UserUseCase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserService:
    """Сервис прикладного слоя для работы с пользователями.

    Оборачивает сценарии UserUseCase и обрабатывает исключения.
    """

    def __init__(self) -> None:
        """Инициализировать сервис пользователей.

        Использует Unit of Work для каждого вызова.
        """
        # Без заранее созданного репозитория: работаем через Unit of Work на каждый вызов
        pass

    def register_user(self, username: str, password: str) -> User:
        """Зарегистрировать нового пользователя.

        Args:
            username: Имя пользователя
            password: Пароль пользователя

        Returns:
            Зарегистрированная доменная модель пользователя

        Raises:
            UserAlreadyExistsError: Пользователь уже существует
            RuntimeError: Ошибка регистрации
        """
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

    def authenticate_user(self, username: str, password: str) -> User:
        """Аутентифицировать пользователя.

        Args:
            username: Имя пользователя
            password: Пароль пользователя

        Returns:
            Аутентифицированная доменная модель пользователя

        Raises:
            UserNotFoundError: Пользователь не найден
            InvalidCredentials: Неверные учетные данные
            RuntimeError: Ошибка аутентификации
        """
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
