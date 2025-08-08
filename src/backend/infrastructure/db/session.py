from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.backend.config.config import Config

# Настройки БД
# DATABASE_URL = "postgresql://hub:hubpass@localhost:5432/travelling" commented for test
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Создаём engine с пулом соединений
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # количество соединений в пуле
    max_overflow=20,  # сколько можно создать сверх пула
    pool_pre_ping=True,  # проверка соединения перед использованием
    pool_recycle=3600,  # пересоздание соединений каждые 3600 сек
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


# Управление сессией через генератор
def get_db_session():
    """
    Генератор сессий. Используется как зависимость.
    """
    session = SessionLocal(bind=engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
