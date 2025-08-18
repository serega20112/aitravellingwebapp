"""Доменная модель пользователя (User)."""

from src.backend.utils.security.password_utils import verify_password


class User:
    """Сущность пользователя доменного уровня."""

    def __init__(
        self,
        user_id: int | None,
        username: str,
        password_hash: str,
        is_active: bool = True,
    ) -> None:
        """Инициализировать сущность User."""
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self._is_active = is_active

    def __repr__(self) -> str:
        """Строковое представление пользователя для отладки."""
        return f"<User {self.username}>"

    def check_password(self, password: str) -> bool:
        """Проверить пароль, сравнив с сохранённым хэшем."""
        return verify_password(password, self.password_hash)

    def get_id(self) -> str:
        """Вернуть идентификатор пользователя как строку (требование Flask-Login)."""
        return str(self.id)  # Flask-Login требует строку

    @property
    def is_active(self) -> bool:
        """Показывает, активен ли пользователь."""
        return self._is_active

    @property
    def is_authenticated(self) -> bool:
        """Флаг аутентифицированного пользователя (совместимость с Flask-Login)."""
        return True  # если пользователь прошёл проверку

    @property
    def is_anonymous(self) -> bool:
        """Пользователь не является анонимным (совместимость с Flask-Login)."""
        return False  # у тебя явно не анонимный юзер
