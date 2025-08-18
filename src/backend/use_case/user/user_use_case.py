"""User use case module for managing user authentication and registration.

This module implements the core business logic for user operations
following Domain-Driven Design principles.
"""

from typing import Optional

from src.backend.domain.exceptions.user_exceptions import (
    InvalidCredentials,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.backend.domain.model.user.user_model import User
from src.backend.domain.repositories.user.user_repository import UserRepository
from src.backend.utils.security.password_utils import hash_password


class UserUseCase:
    """Use case for managing user authentication and registration.

    This class encapsulates all business logic related to user management,
    including user registration, authentication, and validation.

    Attributes:
        user_repo: Repository for user data persistence
    """

    def __init__(self, user_repo: UserRepository) -> None:
        """Initialize UserUseCase with required dependencies.

        Args:
            user_repo: User repository implementation for data persistence
        """
        self.user_repo = user_repo

    def register_user(self, username: str, password: str) -> User:
        """Register a new user with username and password.

        Args:
            username: Unique username for the new user
            password: Plain text password (will be hashed)

        Returns:
            The newly created user object

        Raises:
            UserAlreadyExistsError: If username is already taken
        """
        existing_user: Optional[User] = self.user_repo.find_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError("Пользователь с таким именем уже существует")

        password_hash = hash_password(password)
        user = User(user_id=None, username=username, password_hash=password_hash)
        return self.user_repo.add(user)

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password.

        Args:
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            The authenticated user object

        Raises:
            UserNotFoundError: If user with given username doesn't exist
            InvalidCredentials: If password is incorrect
        """
        user: Optional[User] = self.user_repo.find_by_username(username)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        if not user.check_password(password):
            raise InvalidCredentials("Неверный пароль")

        return user
