from sqlalchemy import Engine
from sqlmodel import create_engine


class BaseService:
    engine: Engine
    db_url: str | None

    def __init__(self, db_url: str | None) -> None:
        self.db_url = db_url
        if self.db_url is None:
            raise ValueError(f'DB url is not set for {self.__class__.__name__}')
        self.engine = create_engine(self.db_url)
