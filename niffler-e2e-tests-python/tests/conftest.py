import random
import re

import pytest
from string import ascii_lowercase

from playwright.sync_api import Playwright

from .functions import *


@pytest.fixture
def niffler_user():
    def _niffler_user(username_length: int = 10, password_length: int = 10):
        niffler_user: NifflerUser = NifflerUser(
            username=''.join(random.choice(ascii_lowercase) for _ in range(username_length)),
            password=''.join(random.choice(ascii_lowercase) for _ in range(password_length))
        )
        return niffler_user
    yield _niffler_user


@pytest.fixture
def niffler_registered_user(niffler_user):
    """Get registered Niffler user and page to do not recreate it later"""
    def _niffler_registered_user(playwright: Playwright):
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(NIFFLER_FRONTEND_URL)
        page.get_by_role('link').get_by_text('Create new account').click()

        new_user = niffler_user()

        username_field, password_field, password_confirm_field = page.get_by_label('Username'), page.get_by_label(
            'Password').first, page.get_by_label('Submit password')
        username_field.fill(new_user.username)
        password_field.fill(new_user.password)
        password_confirm_field.fill(new_user.password)
        page.get_by_role('button').get_by_text('Sign up').click()
        return new_user, page

    yield _niffler_registered_user


@pytest.fixture
def niffler_spend():
    """Get mock spend data"""
    def _niffler_spend():
        spend: NifflerSpend = NifflerSpend(
            amount=round(random.uniform(MIN_AMOUNT, MAX_AMOUNT), 2),
            currency=random.choice(list(Currency)),
            category=''.join([random.choice(ascii_lowercase) for _ in range(CATEGORY_NAME_LENGTH)]),
            date=get_random_date().strftime(SPEND_CREATE_DATE_FORMAT),
            description=''.join([random.choice(ascii_lowercase) for _ in range(CATEGORY_NAME_LENGTH)]),
        )
        return spend

    yield _niffler_spend


@pytest.fixture
def niffler_add_spend(niffler_registered_user, niffler_spend):
    """Create registered user, login and create spend
    :return: current page and NifflerSpend object
    """
    def _niffler_add_spend(playwright: Playwright):
        registered_user, page = niffler_registered_user(playwright)
        page.goto(NIFFLER_FRONTEND_URL)
        login_with_user(page, registered_user)
        page.get_by_role('link').get_by_text('New spending').click()

        new_spend: NifflerSpend = niffler_spend()
        page.get_by_label('Amount').fill(str(new_spend.amount))

        page.locator('#currency').click()
        page.locator(f'ul[role="listbox"] >> li:has-text("{new_spend.currency.value["value"]}")').click()

        page.locator('#category').fill(new_spend.category)
        page.locator('input[name="date"]').fill(new_spend.date)
        page.get_by_label('Description').fill(new_spend.description)
        page.locator('button:has-text("Add")').click()
        page.wait_for_url(re.compile('main'), wait_until='load')
        page.wait_for_selector('table')
        return page, new_spend

    yield _niffler_add_spend
