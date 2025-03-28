from sqlmodel import SQLModel


class User(SQLModel):
    pass


class SuperUser(SQLModel, table=True):
    pass
