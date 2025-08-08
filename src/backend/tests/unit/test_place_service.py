from src.backend.services.place.place_service import PlaceService


class DummyUC:
    def __init__(self, info: str = "INFO"):
        self.info = info
        self.called_with = None

    def get_info_for_point(self, lat: float, lon: float) -> str:
        self.called_with = (lat, lon)
        return f"{self.info} {lat},{lon}"


def test_place_service_delegates_to_use_case():
    uc = DummyUC(info="OK")
    svc = PlaceService(place_use_case=uc)

    res = svc.get_info_for_point(1.5, 2.5)

    assert res.startswith("OK")
    assert uc.called_with == (1.5, 2.5)


def test_place_service_wraps_exceptions():
    class ErrUC:
        def get_info_for_point(self, lat, lon):
            raise RuntimeError("boom")

    svc = PlaceService(place_use_case=ErrUC())

    try:
        svc.get_info_for_point(0, 0)
        assert False, "Expected exception"
    except Exception as e:
        assert isinstance(e, RuntimeError)
        assert "Ошибка при получении информации" in str(e)
