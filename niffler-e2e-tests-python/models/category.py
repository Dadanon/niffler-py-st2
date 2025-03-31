from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    id: str
    name: str
    username: str
    archived: bool = Field(default=False)
