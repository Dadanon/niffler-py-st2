from sqlmodel import Session, exists

from config import settings
from .base_service import BaseService
from models.spend import Spend


class SpendService(BaseService):
    def spend_exists(self, spend_id: str) -> bool:
        """A fast way to check if spend exists in database without fetching the entire model"""
        with Session(self.engine) as session:
            stmt = exists().where(Spend.id == spend_id)
            return session.execute(stmt).scalar()


spend_service = SpendService(settings.SPEND_DB_URL)
