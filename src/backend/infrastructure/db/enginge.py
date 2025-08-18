"""Создание engine и фабрики сессий SQLAlchemy (простая обёртка)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.config.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
