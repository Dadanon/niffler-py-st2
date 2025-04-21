from datetime import date
from sqlmodel import SQLModel, Field


class Friendship(SQLModel, table=True):
    requester_id: str = Field(primary_key=True)
    addressee_id: str = Field(primary_key=True)
    status: str
    created_date: date
