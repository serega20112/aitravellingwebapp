"""Исключения домена для операций с пользователями (User)."""


class UserServiceError(Exception):
    """Базовое исключение для ошибок User сервиса."""


class UserNotFoundError(UserServiceError):
    """Исключение, когда пользователь не найден."""


class UserAlreadyExistsError(UserServiceError):
    """Исключение, когда пользователь уже существует."""


class AuthenticationError(UserServiceError):
    """Ошибка аутентификации пользователя."""


class AuthorizationError(UserServiceError):
    """Ошибка авторизации (нет прав доступа)."""


class UserValidationError(UserServiceError):
    """Ошибка валидации данных пользователя."""


class InvalidCredentials(UserServiceError):
    """Ошибка: неверный логин или пароль."""
