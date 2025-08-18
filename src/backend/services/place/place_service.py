"""Сервис для работы с местами (прикладной слой)."""

from src.backend.domain.exceptions.place_exceptions import PlaceNotFoundError
from src.backend.use_case.place.place_use_case import PlaceUseCase


class PlaceService:
    """Сервис прикладного слоя для работы с местами.

    Оборачивает сценарии PlaceUseCase и обрабатывает исключения.
    """

    def __init__(self, place_use_case: PlaceUseCase) -> None:
        """Инициализировать сервис с сценарием PlaceUseCase.

        Args:
            place_use_case: Сценарий для работы с местами
        """
        self.place_use_case = place_use_case

    def get_info_for_point(self, latitude: float, longitude: float) -> str:
        """Получить информацию о месте по координатам.

        Args:
            latitude: Широта
            longitude: Долгота

        Returns:
            Описание места от ИИ-сервиса

        Raises:
            PlaceNotFoundError: Место не найдено
            RuntimeError: Ошибка при получении информации
        """
        try:
            return self.place_use_case.get_info_for_point(latitude, longitude)
        except PlaceNotFoundError as e:
            raise e
        except Exception as e:
            raise RuntimeError("Ошибка при получении информации о точке") from e
