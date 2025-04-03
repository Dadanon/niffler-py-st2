from sqlmodel import Session, select, exists

from config import settings
from .base_service import BaseService
from .user import User


class UserService(BaseService):
    def user_exists(self, username: str) -> bool:
        """A fast way to check if user exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            statement = exists().where(User.username == username)
            return session.execute(statement).scalar()

    def delete_user(self, username: str) -> str:
        """Delete user from database if exists and return his username (for any purposes)"""
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            db_user: User | None = session.execute(statement).first()
            if db_user is None:
                raise ValueError(f'No user with username {username}')
            session.delete(db_user)
            session.commit()
            return username


user_service = UserService(settings.USERDATA_DB_URL)


