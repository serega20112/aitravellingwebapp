"""SQLAlchemy-модель пользователя приложения."""

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.Base import Base


class User(UserMixin, Base):
    """Таблица ``users`` с отношением к понравившимся местам."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

    liked_places = relationship(
        "LikedPlace", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User {self.username}>"

    def check_password(self, plain_password: str) -> bool:
        """Проверить пароль пользователя по хэшу."""
        from src.backend.utils.security.password_utils import verify_password

        return verify_password(plain_password, self.password_hash)
