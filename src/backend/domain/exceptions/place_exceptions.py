"""Исключения домена для операций с местами (Place)."""


class PlaceServiceError(Exception):
    """Базовое исключение для ошибок Place сервиса."""


class PlaceNotFoundError(PlaceServiceError):
    """Исключение, когда место не найдено."""


class PlaceAlreadyExistsError(PlaceServiceError):
    """Исключение, когда место уже существует."""


class PlaceValidationError(PlaceServiceError):
    """Ошибка валидации данных для Place."""
