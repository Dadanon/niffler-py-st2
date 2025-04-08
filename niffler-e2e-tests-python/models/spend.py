from datetime import date
from sqlmodel import SQLModel, Field


class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    username: str
    spend_date: date
    currency: str
    amount: float
    description: str
    category_id: str


class SpendCreate(SQLModel):
    amount: float
    currency: str
    category: str
    spend_date: str
    description: str = Field(default='')


class SpendListed(SpendCreate):
    pass
