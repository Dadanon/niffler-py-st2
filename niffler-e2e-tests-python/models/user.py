from sqlalchemy import LargeBinary, Column
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    username: str = Field(unique=True)
    currency: str
    firstname: str | None = Field(nullable=True)
    surname: str | None = Field(nullable=True)
    photo: bytes | None = Field(sa_column=Column(LargeBinary))
    photo_small: bytes | None = Field(sa_column=Column(LargeBinary))
    full_name: str | None = Field(nullable=True)


class UserCreate(SQLModel):
    username: str
    password: str
