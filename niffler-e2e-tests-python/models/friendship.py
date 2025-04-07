from datetime import date
from sqlmodel import SQLModel, Field


class Friendship(SQLModel, table=True):
    requester_id: str
    addressee_id: str
    status: str
    created_date: date
