from src.backend.use_case.user.profile_use_case import ProfileUseCase
from src.backend.domain.model.place.liked_place_model import LikedPlace
from src.backend.tests.conftest import DummyUoW, make_user_repo, make_place_repo, DummyAI
import pytest


def test_get_liked_places_user_not_found():
    uow = DummyUoW(make_user_repo(existing_user=False), make_place_repo([]))
    ai = DummyAI()
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    with pytest.raises(Exception):
        uc.get_liked_places(999)


def test_get_liked_places_returns_list():
    places = [LikedPlace(1, 1, "City", 1.1, 2.2)]
    uow = DummyUoW(make_user_repo(existing_user=True), make_place_repo(places))
    ai = DummyAI()
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    res = uc.get_liked_places(1)

    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].city_name == "City"


def test_get_recommendations_empty_liked_places():
    uow = DummyUoW(make_user_repo(existing_user=True), make_place_repo([]))
    ai = DummyAI(rec_prefix="REC:")
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    msg = uc.get_recommendations(1)

    assert "Сначала отметьте любимые места" in msg


def test_get_recommendations_from_ai():
    places = [
        LikedPlace(1, 1, "Paris", 0, 0),
        LikedPlace(2, 1, "Berlin", 1, 1),
    ]
    uow = DummyUoW(make_user_repo(existing_user=True), make_place_repo(places))
    ai = DummyAI(rec_prefix="REC:")
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    rec = uc.get_recommendations(1)

    assert rec.startswith("REC:")
    assert "Paris" in rec and "Berlin" in rec


def test_add_liked_place_creates_new():
    uow = DummyUoW(make_user_repo(existing_user=True), make_place_repo([]))
    ai = DummyAI()
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    created = uc.add_liked_place(1, "City", 1.1, 2.2)

    assert isinstance(created, LikedPlace)
    assert created.id == 1


def test_add_liked_place_idempotent():
    existing = LikedPlace(1, 1, "City", 1.1, 2.2)
    uow = DummyUoW(make_user_repo(existing_user=True), make_place_repo([existing]))
    ai = DummyAI()
    uc = ProfileUseCase(uow=uow, ai_service=ai)

    result = uc.add_liked_place(1, "City", 1.1, 2.2)

    assert result is existing
