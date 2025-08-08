from src.backend.utils.security.password_utils import verify_password


class User:
    def __init__(
        self,
        user_id: int | None,
        username: str,
        password_hash: str,
        is_active: bool = True,
    ):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self._is_active = is_active

    def __repr__(self):
        return f"<User {self.username}>"

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def get_id(self) -> str:
        return str(self.id)  # Flask-Login требует строку

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_authenticated(self) -> bool:
        return True  # если пользователь прошёл проверку

    @property
    def is_anonymous(self) -> bool:
        return False  # у тебя явно не анонимный юзер
