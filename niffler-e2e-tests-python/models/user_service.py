from sqlmodel import Session, select, exists

from ..config import settings
from .base_service import BaseService
from .user import User
from .friendship import Friendship


class UserService(BaseService):
    def user_exists(self, username: str) -> bool:
        """A fast way to check if user exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            stmt = exists().where(User.username == username)
            return session.execute(stmt).scalar()

    def delete_user(self, username: str) -> str:
        """Delete user from database if exists and return his username (for any purposes)"""
        with Session(self.engine) as session:
            stmt = select(User).where(User.username == username)
            db_user: User | None = session.execute(stmt).first()
            if db_user is None:
                raise ValueError(f'No user with username {username}')
            session.delete(db_user)
            session.commit()
            return username

    def get_user_by_username(self, username: str) -> User:
        with Session(self.engine) as session:
            stmt = select(User).where(User.username == username)
            db_user: User | None = session.execute(stmt).first()
            if db_user is None:
                raise ValueError(f'No user with username {username}')
            return db_user

    def friend_exists(self, requester_username: str, addressee_username: str) -> bool:
        with Session(self.engine) as session:
            requester_id_stmt = select(User.id).where(User.username == requester_username)
            addressee_id_stmt = select(User.id).where(User.username == addressee_username)
            requester_id: str | None = session.execute(requester_id_stmt).first()
            addressee_id: str | None = session.execute(addressee_id_stmt).first()
            if addressee_id is None or requester_id is None:
                raise ValueError(f'No addressee with username {addressee_username} or requester with username {requester_username}')
            friendship_stmt = exists().where(
                Friendship.requester_id == requester_id,
                Friendship.addressee_id == addressee_id,
                Friendship.status == 'ACCEPTED'
            )
            return session.execute(friendship_stmt).scalar()


user_service = UserService(settings.USERDATA_DB_URL)


