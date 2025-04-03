import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import dotenv

dotenv.load_dotenv()


# INFO: block below is just for simplicity
MIN_AMOUNT: int = 1
MAX_AMOUNT: int = 300
CATEGORY_NAME_LENGTH: int = 10
MIN_DATE: datetime = datetime(year=2020, month=1, day=1)
MAX_DATE: datetime = datetime(year=2025, month=12, day=31)
DESCRIPTION_LENGTH: int = 20
SPEND_CREATE_DATE_FORMAT: str = '%m/%d/%Y'
SPEND_SHOW_DATE_FORMAT: str = '%b %d, %Y'


def get_random_date() -> datetime:
    """Get random date between min and max dates"""
    delta_sec: int = int((MAX_DATE - MIN_DATE).total_seconds())
    random_delta_add_time: int = random.randint(0, delta_sec)
    return MIN_DATE + timedelta(seconds=random_delta_add_time)


@dataclass
class User:
    username: str
    password: str


class Currency(Enum):
    RUB = {
        'value': 'RUB',
        'sign': '₽'
    }
    KZT = {
        'value': 'KZT',
        'sign': '₸'
    }
    EUR = {
        'value': 'EUR',
        'sign': '€'
    }
    USD = {
        'value': 'USD',
        'sign': '$'
    }


@dataclass
class Spend:
    amount: float
    currency: Currency
    category: str
    date: str
    description: str


class Settings:
    FRONTEND_URL: str = os.getenv('NIFFLER_FRONTEND_URL')
    AUTH_URL: str = os.getenv('NIFFLER_AUTH_URL')
    AUTH_DB_URL: str = os.getenv('NIFFLER_AUTH_DB_URL')
    CURRENCY_DB_URL: str = os.getenv('NIFFLER_CURRENCY_DB_URL')
    SPEND_DB_URL: str = os.getenv('NIFFLER_SPEND_DB_URL')
    USERDATA_DB_URL: str = os.getenv('NIFFLER_USERDATA_DB_URL')


settings = Settings()
