import random

import pytest
from string import ascii_lowercase


class NifflerUser:
    username: str
    password: str

    def __init__(self, username, password):
        self.username = username
        self.password = password


@pytest.fixture
def niffler_user():
    def _niffler_user(username_length: int = 10, password_length: int = 10):
        niffler_user: NifflerUser = NifflerUser(
            username=''.join(random.choice(ascii_lowercase) for i in range(username_length)),
            password=''.join(random.choice(ascii_lowercase) for i in range(password_length))
        )
        return niffler_user
    yield _niffler_user

