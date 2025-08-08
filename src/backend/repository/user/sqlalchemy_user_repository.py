from src.backend.domain.model.user.user_model import User as DomainUser
from src.backend.domain.repositories.user.user_repository import UserRepository
from src.backend.infrastructure.models.user_model import User as DbUser


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        # Сессия внедряется извне (Unit of Work управляет транзакцией)
        self.session = session

    def add(self, user: DomainUser) -> DomainUser:
        db_user = DbUser(username=user.username, password_hash=user.password_hash)
        self.session.add(db_user)
        user.id = db_user.id
        return user

    def find_by_username(self, username: str) -> DomainUser | None:
        db_user = self.session.query(DbUser).filter_by(username=username).first()
        if not db_user:
            return None
        return DomainUser(
            user_id=db_user.id,
            username=db_user.username,
            password_hash=db_user.password_hash,
        )

    def find_by_id(self, user_id: int) -> DomainUser | None:
        db_user = self.session.get(DbUser, user_id)
        if not db_user:
            return None
        return DomainUser(
            user_id=db_user.id,
            username=db_user.username,
            password_hash=db_user.password_hash,
        )
