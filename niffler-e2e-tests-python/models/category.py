from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    username: str
    archived: bool = Field(default=False)
