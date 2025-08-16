from src.backend.use_case.place.place_use_case import PlaceUseCase
from src.backend.domain.exceptions.place_exceptions import PlaceNotFoundError

class PlaceService:
    def __init__(self, place_use_case: PlaceUseCase):
        """Сервис прикладного слоя, оборачивающий сценарии PlaceUseCase.
        Зависимости передаются извне (DI).
        """
        self.place_use_case = place_use_case

    def get_info_for_point(self, latitude: float, longitude: float):
        try:
            return self.place_use_case.get_info_for_point(latitude, longitude)
        except PlaceNotFoundError as e:
            raise e
        except Exception as e:
            raise RuntimeError("Ошибка при получении информации о точке") from e