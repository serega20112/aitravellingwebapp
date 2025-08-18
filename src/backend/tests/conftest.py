import sys
from pathlib import Path
from types import SimpleNamespace
from typing import List

# Ensure project root is on sys.path so that `from src.backend...` works
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DummyUoW:
    """Minimal UoW test double with context manager support."""

    def __init__(self, user_repo, place_repo):
        self.user_repo = user_repo
        self.place_repo = place_repo
        self._committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False  # don't suppress exceptions

    # Interface methods expected by code
    def commit(self):
        self._committed = True

    def rollback(self):
        self._committed = False


def make_user_repo(existing_user: bool = True):
    repo = SimpleNamespace()
    repo.find_by_id = lambda uid: SimpleNamespace(id=uid) if existing_user else None
    return repo


def make_place_repo(initial_places: List[object] | None = None):
    places = list(initial_places or [])

    def get_liked_places_by_user(user_id: int):
        return [p for p in places if p.user_id == user_id]

    def add_liked_place(place):
        place.id = len(places) + 1
        places.append(place)
        return place

    repo = SimpleNamespace(
        get_liked_places_by_user=get_liked_places_by_user,
        add_liked_place=add_liked_place,
        _places=places,
    )
    return repo


class DummyAI:
    """Simple AI service double for unit tests."""

    def __init__(self, info_response: str = "INFO", rec_prefix: str = "REC:"):
        self.info_response = info_response
        self.rec_prefix = rec_prefix

    def get_place_info(self, latitude: float, longitude: float) -> str:
        return f"{self.info_response} {latitude},{longitude}"

    def get_travel_recommendation(self, liked_places_str: str) -> str:
        return f"{self.rec_prefix} {liked_places_str}"


# -------- Pytest fixtures for integration tests --------
import pytest


@pytest.fixture
def app():
    # Lazily import to ensure sys.path is patched above
    from src.backend.create_app import create_app

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=True,  # simplify routes requiring login for tests where needed
    )
    # Ensure services dict exists
    app.extensions.setdefault("services", {})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class FakePlaceService:
    def __init__(self, response: str = "OK"):
        self.response = response

    def get_info_for_point(self, latitude: float, longitude: float) -> str:
        return f"{self.response} {latitude},{longitude}"
