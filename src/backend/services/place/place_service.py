from src.backend.use_case.place.place_use_case import PlaceUseCase
from src.backend.domain.exceptions.place_exceptions import PlaceNotFoundError
from src.backend.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.backend.infrastructure.services.ai_service import AIService

class PlaceService:
    def __init__(self, place_use_case=None):
        # Композиция зависимостей: внедряем UoW и AI адаптер
        self.place_use_case = place_use_case or PlaceUseCase(
            uow=SqlAlchemyUnitOfWork(),
            ai_service=AIService(),
        )

    def get_info_for_point(self, latitude: float, longitude: float):
        try:
            return self.place_use_case.get_info_for_point(latitude, longitude)
        except PlaceNotFoundError as e:
            raise e
        except Exception as e:
            raise RuntimeError("Ошибка при получении информации о точке") from e