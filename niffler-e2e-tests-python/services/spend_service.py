from typing import Sequence

from sqlalchemy import func
from sqlmodel import Session, exists, select

from config import settings
from models.category import Category
from .base_service import BaseService
from models.spend import Spend


class SpendService(BaseService):
    def get_total_count(self) -> int:
        """Получить общее число трат"""
        with Session(self.engine) as session:
            stmt = select(func.count(Spend.id))
            return session.exec(stmt).first()

    def get_user_spends(self, username: str) -> Sequence[Spend]:
        with Session(self.engine) as session:
            stmt = select(Spend).where(Spend.username == username)
            return session.exec(stmt).all()

    def get_user_spend_count(self, username: str) -> int:
        """Получить количество трат для конкретного юзера"""
        with Session(self.engine) as session:
            stmt = select(func.count(Spend.id)).where(Spend.username == username)
            return session.exec(stmt).first()

    def spend_exists(self, spend_id: str) -> bool:
        """A fast way to check if spend exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            stmt = select(exists().where(Spend.id == spend_id))
            return session.exec(stmt).first()

    def delete_user_spends(self, username: str) -> None:
        """Delete all user spends"""
        with Session(self.engine) as session:
            stmt = select(Spend).where(Spend.username == username)
            db_spends = session.exec(stmt).all()
            for db_spend in db_spends:
                session.delete(db_spend)
            session.commit()

    def delete_user_categories(self, username: str) -> None:
        """Delete all user spend categories"""
        with Session(self.engine) as session:
            stmt = select(Category).where(Category.username == username)
            db_categories = session.exec(stmt).all()
            for db_category in db_categories:
                session.delete(db_category)
            session.commit()


spend_service = SpendService(settings.SPEND_DB_URL)
