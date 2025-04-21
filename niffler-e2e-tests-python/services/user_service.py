from sqlmodel import Session, select, exists, and_, or_

from config import settings
from .base_service import BaseService
from models.user import User
from models.friendship import Friendship
from .spend_service import spend_service


class UserService(BaseService):
    def user_exists(self, username: str) -> bool:
        """A fast way to check if user exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            stmt = select(exists().where(User.username == username))
            result = session.execute(stmt).scalar()
            print(f'User with username {username} exists: {result}')
            return result

    def get_user_id_by_username(self, username: str) -> str:
        """Получить UUID пользователя по его нику"""
        with Session(self.engine) as session:
            stmt = select(User.id).where(User.username == username)
            user_id = session.exec(stmt).first()
            if not user_id:
                raise ValueError(f'User with username {username} does not have UUID!!!')
            return user_id

    def delete_user(self, username: str) -> str:
        """Delete user from database if exists and return his username (for any purposes)."""
        with Session(self.engine) as session:
            stmt = select(User).where(User.username == username)
            db_user: User | None = session.exec(stmt).first()
            if db_user is None:
                print(f'For some purposes user with username {username} does not exist')
                return username
            # INFO: we do not know anything about cascade delete rules in DB so we delete related entities by hand :)
            # Remove all user spends
            spend_service.delete_user_spends(username)
            # Remove all user categories
            spend_service.delete_user_categories(username)
            # Remove friendships
            self.delete_user_friendships(db_user.id)
            # Finally remove user
            session.delete(db_user)
            session.commit()
            return username

    def delete_user_friendships(self, user_id: str) -> None:
        """Удалить все имеющиеся дружбы и запросы в друзья"""
        with Session(self.engine) as session:
            stmt = select(Friendship).where(or_(
                Friendship.requester_id == user_id,
                Friendship.addressee_id == user_id
            ))
            friendships = session.execute(stmt).all()
            print(f'Friendships: {friendships}')
            for friendship in session.exec(stmt).all():
                session.delete(friendship)
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
            requester_id: str | None = session.exec(requester_id_stmt).first()
            addressee_id: str | None = session.exec(addressee_id_stmt).first()
            if addressee_id is None or requester_id is None:
                raise ValueError(f'No addressee with username {addressee_username} or requester with username {requester_username}')
            friendship_stmt = select(exists().where(and_(
                Friendship.requester_id == requester_id,
                Friendship.addressee_id == addressee_id,
                Friendship.status == 'ACCEPTED'
            )))
            return session.exec(friendship_stmt).first()


user_service = UserService(settings.USERDATA_DB_URL)


