from src.backend.use_case.place.place_use_case import PlaceUseCase
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.tests.conftest import DummyUoW, make_user_repo, make_place_repo, DummyAI
import pytest


def test_get_info_for_point_uses_ai():
    uow = DummyUoW(make_user_repo(), make_place_repo())
    ai = DummyAI(info_response="OK")
    uc = PlaceUseCase(uow=uow, ai_service=ai)

    res = uc.get_info_for_point(10.0, 20.0)

    assert res.startswith("OK")
    assert "10.0,20.0" in res


def test_add_liked_place_happy_path_creates_new():
    user_repo = make_user_repo(existing_user=True)
    place_repo = make_place_repo([])
    uow = DummyUoW(user_repo, place_repo)
    ai = DummyAI()
    uc = PlaceUseCase(uow=uow, ai_service=ai)

    created = uc.add_liked_place(1, "City", 1.1, 2.2)

    assert isinstance(created, LikedPlace)
    assert created.id == 1
    assert created.city_name == "City"
    assert uow._committed is True


def test_add_liked_place_idempotent_by_coordinates():
    existing = LikedPlace(id=1, user_id=1, city_name="X", latitude=1.1, longitude=2.2)
    user_repo = make_user_repo(existing_user=True)
    place_repo = make_place_repo([existing])
    uow = DummyUoW(user_repo, place_repo)
    ai = DummyAI()
    uc = PlaceUseCase(uow=uow, ai_service=ai)

    result = uc.add_liked_place(1, "City", 1.1, 2.2)

    assert result is existing
    assert len(place_repo._places) == 1


def test_add_liked_place_raises_if_user_not_found():
    user_repo = make_user_repo(existing_user=False)
    place_repo = make_place_repo([])
    uow = DummyUoW(user_repo, place_repo)
    ai = DummyAI()
    uc = PlaceUseCase(uow=uow, ai_service=ai)

    with pytest.raises(Exception):
        uc.add_liked_place(999, "City", 1.1, 2.2)


def test_generate_recommendations_from_ai_with_liked_places():
    existing = [
        LikedPlace(id=1, user_id=1, city_name="Paris", latitude=0, longitude=0),
        LikedPlace(id=2, user_id=1, city_name="Berlin", latitude=0, longitude=1),
    ]
    uow = DummyUoW(make_user_repo(), make_place_repo(existing))
    ai = DummyAI(rec_prefix="REC:")
    uc = PlaceUseCase(uow=uow, ai_service=ai)

    rec = uc.generate_recommendations_for_user(1)

    assert rec.startswith("REC:")
    assert "Paris" in rec and "Berlin" in rec
