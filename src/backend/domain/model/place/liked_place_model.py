"""Доменная модель понравившегося места (LikedPlace)."""


class LikedPlace:
    """Сущность понравившегося места пользователя."""

    def __init__(
        self,
        id: int | None,
        user_id: int,
        city_name: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Инициализировать сущность LikedPlace."""
        self.id = id
        self.user_id = user_id
        self.city_name = city_name
        self.latitude = latitude
        self.longitude = longitude
