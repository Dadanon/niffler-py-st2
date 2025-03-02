import os
import random
import re
from datetime import datetime, timedelta
from enum import Enum

import dotenv
from playwright.sync_api import Page

dotenv.load_dotenv()


NIFFLER_FRONTEND_URL = os.getenv("NIFFLER_FRONTEND_URL")
NIFFLER_AUTH_URL = os.getenv("NIFFLER_AUTH_URL")

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


class NifflerUser:
    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


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


class NifflerSpend:
    amount: float
    currency: Currency
    category: str
    date: str
    description: str

    def __init__(self, amount: float, currency: Currency, category: str, date: str, description: str):
        self.amount = amount
        self.currency = currency
        self.category = category
        self.date = date
        self.description = description


def login_with_user(page: Page, user: NifflerUser):
    login_field, password_field = page.get_by_label('Username'), page.get_by_label('Password')
    login_field.fill(user.username)
    password_field.fill(user.password)
    page.get_by_role('button').get_by_text('Log in').click()


def logout_with_user(page: Page):
    page.locator('button[aria-label="Menu"]').click()
    page.locator('ul[role="menu"] li:has-text("Sign out")').click()
    page.locator('button:has-text("Log out")').click()
    page.wait_for_url(re.compile('login'), wait_until='load')
