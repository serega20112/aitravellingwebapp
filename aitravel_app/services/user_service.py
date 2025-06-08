from aitravel_app.models import User
from aitravel_app.core.db import db
from aitravel_app.core.security import hash_password, verify_password
from aitravel_app.schemas.user_schemas import UserCreateSchema
from sqlalchemy.exc import IntegrityError

class UserServiceError(Exception):
    pass

class UserAlreadyExistsError(UserServiceError):
    pass

class UserService:
    @staticmethod
    def create_user(user_data: UserCreateSchema) -> User:
        if User.query.filter_by(username=user_data.username).first():
            raise UserAlreadyExistsError("Username already exists")

        hashed_pw = hash_password(user_data.password)
        new_user = User(username=user_data.username, password_hash=hashed_pw)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise UserAlreadyExistsError("Username already exists (database integrity error)")
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Could not create user: {e}")
        return new_user

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.query.get(user_id)

    @staticmethod
    def check_user_credentials(username: str, password_plaintext: str) -> User | None:
        user = UserService.get_user_by_username(username)
        if user and verify_password(user.password_hash, password_plaintext):
            return user
        return None
