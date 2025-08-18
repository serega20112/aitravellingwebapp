"""Фабрика Flask-приложения и регистрация зависимостей/маршрутов."""

import os
import time

from dotenv import load_dotenv
from flask import Flask, Response, g, request
from flask_login import LoginManager

from src.backend.config import _config
from src.backend.delivery.routes import (
    auth_router,
    chat_router,
    logs_router,
    map_router,
    profile_router,
)
from src.backend.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.backend.infrastructure.logging.es_query_service import (
    ElasticsearchLogService,
)
from src.backend.infrastructure.services.ai_service import AIService
from src.backend.infrastructure.services.geocoding_service import GeocodingService
from src.backend.repository.chat.memory_chat_repository import ChatMemoryRepository
from src.backend.services.place.place_service import PlaceService
from src.backend.use_case.place.place_use_case import PlaceUseCase
from src.backend.use_case.user.profile_use_case import ProfileUseCase
from src.backend.utils.logging_setup import setup_logging


def create_app(config_class: object | None = None) -> Flask:
    """Создать и сконфигурировать Flask-приложение."""
    load_dotenv()

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
    )
    static_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
    )
    app = Flask(
        __name__,
        template_folder=base_dir,
        static_folder=static_path,
        instance_relative_config=True,
    )

    # Загружаем конфиг
    if config_class is None:
        app.config.from_object(_config)
    else:
        app.config.from_object(config_class)

    # Инициализация логирования (консоль/файл/Elasticsearch + middleware)
    setup_logging(app)

    # Простейший security-middleware: логируем IP, метод, путь, UA и длительность запроса
    @app.before_request
    def _start_timer() -> None:
        """Запомнить время начала запроса для последующего логирования."""
        g._req_start = time.perf_counter()

    @app.after_request
    def _log_request_info(response: Response) -> Response:
        """Логировать краткую информацию о запросе/ответе."""
        try:
            duration_ms = None
            if hasattr(g, "_req_start"):
                duration_ms = round((time.perf_counter() - g._req_start) * 1000, 2)
            # если есть прокси — берём первый IP из X-Forwarded-For
            forwarded_for = request.headers.get("X-Forwarded-For")
            ip = (
                forwarded_for.split(",")[0].strip()
                if forwarded_for
                else request.remote_addr
            )
            ua = request.headers.get("User-Agent", "-")
            app.logger.info(
                "SECURITY: %s %s -> %s | ip=%s | ua=%s | t=%sms",
                request.method,
                request.path,
                response.status_code,
                ip,
                ua,
                duration_ms if duration_ms is not None else "-",
            )
        except Exception:
            app.logger.exception("Security logging failed")
        return response

    # Неболтливые стартовые сообщения (без секретов)
    print("Templates folder:", base_dir)
    print("Contains index.html:", os.path.exists(os.path.join(base_dir, "index.html")))
    print("DB configured:", bool(app.config.get("SQLALCHEMY_DATABASE_URI")))

    # Убеждаемся, что SECRET_KEY задан
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Please set it in your config or .env"
        )

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Инициализация LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> object | None:
        """Загрузить пользователя по идентификатору для flask-login."""
        # Создаём отдельную сессию для загрузки пользователя (вне UoW)
        from src.backend.infrastructure.db.session import SessionLocal
        from src.backend.repository.user.sqlalchemy_user_repository import (
            SqlAlchemyUserRepository,
        )

        session = SessionLocal()
        try:
            user_repo = SqlAlchemyUserRepository(session)
            return user_repo.find_by_id(int(user_id))
        finally:
            session.close()

    # Регистрация блюпринтов
    with app.app_context():
        app.register_blueprint(auth_router.auth_router)
        app.register_blueprint(map_router.bp)
        app.register_blueprint(profile_router.bp)
        app.register_blueprint(logs_router.bp)
        app.register_blueprint(chat_router.bp)

    # Композиция зависимостей приложения (DI)
    # Общий AI сервис (тяжёлый объект) создаём один раз и переиспользуем
    ai_service = AIService(config=app.config, logger=app.logger)
    app.extensions.setdefault("services", {})
    app.extensions["services"]["ai_service"] = ai_service
    # Geocoding (OSM Nominatim) — создаём из app.config, без current_app
    cfg = app.config
    app.extensions["services"]["geocoding_service"] = GeocodingService(
        base_url=cfg.get("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org"),
        user_agent=cfg.get("NOMINATIM_USER_AGENT", "aitravel-app/1.0"),
        email=cfg.get("NOMINATIM_EMAIL"),
        logger=app.logger,
    )
    app.extensions["services"]["chat_repo"] = ChatMemoryRepository(max_messages=30)
    # PlaceService на базе UoW и AI
    app.extensions["services"]["place_service"] = PlaceService(
        place_use_case=PlaceUseCase(
            uow=SqlAlchemyUnitOfWork(),
            ai_service=ai_service,
        )
    )
    # ProfileUseCase для профиля пользователя
    app.extensions["services"]["profile_use_case"] = ProfileUseCase(
        uow=SqlAlchemyUnitOfWork(),
        ai_service=ai_service,
    )

    # Сервис для чтения логов из Elasticsearch (для веб-дашборда)
    app.extensions["services"]["log_service"] = ElasticsearchLogService(
        host=app.config.get("ELASTICSEARCH_HOST"),
        index_name=app.config.get("ES_INDEX_NAME", "logs-app"),
        username=app.config.get("ES_USERNAME"),
        password=app.config.get("ES_PASSWORD"),
        verify_certs=bool(app.config.get("ES_VERIFY_CERTS", False)),
        ca_certs=app.config.get("ES_CA_CERTS"),
        request_timeout=int(app.config.get("ES_REQUEST_TIMEOUT", 5)),
    )

    # Логируем зарегистрированные маршруты
    with app.app_context():
        print("Registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule}")

    return app
