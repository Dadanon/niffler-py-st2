from sqlmodel import Session, select, exists

from config import settings
from .base_service import BaseService
from models.user import User
from models.friendship import Friendship
from models.spend import Spend
from models.category import Category


class UserService(BaseService):
    def user_exists(self, username: str) -> bool:
        """A fast way to check if user exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            stmt = exists().where(User.username == username)
            return session.execute(stmt).scalar()

    def delete_user(self, username: str) -> str:
        """Delete user from database if exists and return his username (for any purposes)."""
        with Session(self.engine) as session:
            # INFO: we do not know anything about cascade delete rules in DB so we delete related entities by hand :)
            # Remove all user spends
            self.delete_user_spends(username)
            # Remove all user categories
            self.delete_user_categories(username)
            # Finally remove user
            stmt = select(User).where(User.username == username)
            db_user: User | None = session.execute(stmt).first()
            if db_user is None:
                raise ValueError(f'No user with username {username}')
            session.delete(db_user)
            session.commit()
            return username

    def delete_user_spends(self, username: str) -> None:
        """Delete all user spends"""
        with Session(self.engine) as session:
            stmt = select(Spend).where(Spend.username == username)
            db_spends = session.execute(stmt).all()
            for db_spend in db_spends:
                session.delete(db_spend)
            session.commit()

    def delete_user_categories(self, username: str) -> None:
        """Delete all user spend categories"""
        with Session(self.engine) as session:
            stmt = select(Category).where(Category.username == username)
            db_categories = session.execute(stmt).all()
            for db_category in db_categories:
                session.delete(db_category)
            session.commit()

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


