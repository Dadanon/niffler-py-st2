import pytest
from string import ascii_lowercase

from playwright.sync_api import Playwright
from .pages import *


# Mock data

@pytest.fixture
def user():
    def _user(username_length: int = 10, password_length: int = 10):
        user: User = User(
            username=''.join(random.choice(ascii_lowercase) for _ in range(username_length)),
            password=''.join(random.choice(ascii_lowercase) for _ in range(password_length))
        )
        return user
    yield _user


@pytest.fixture
def spend():
    """Get mock spend data"""
    def _spend():
        spend: Spend = Spend(
            amount=round(random.uniform(MIN_AMOUNT, MAX_AMOUNT), 2),
            currency=random.choice(list(Currency)),
            category=''.join([random.choice(ascii_lowercase) for _ in range(CATEGORY_NAME_LENGTH)]),
            date=get_random_date().strftime(SPEND_CREATE_DATE_FORMAT),
            description=''.join([random.choice(ascii_lowercase) for _ in range(CATEGORY_NAME_LENGTH)]),
        )
        return spend
    yield _spend


# Base fixtures

@pytest.fixture(scope='session', autouse=True)
def browser(playwright: Playwright):
    browser = playwright.chromium.launch()
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    page.set_default_timeout(10000)
    yield page
    page.close()


# Advanced fixtures and also page fixtures

@pytest.fixture
def registered_user(page, user):
    def _registered_user() -> User:
        login_page = LoginPage(page)
        registration_page = login_page.go_to_registration_page()
        new_user = user()
        registration_page.register_user(new_user)
        print(f'New user registered: {new_user.__dict__}')
        return new_user
    yield _registered_user


@pytest.fixture
def login_page(page):
    def _login_page() -> LoginPage:
        return LoginPage(page)
    yield _login_page


@pytest.fixture
def registration_page(login_page):
    def _registration_page() -> RegistrationPage:
        new_login_page = login_page()
        return new_login_page.go_to_registration_page()
    yield _registration_page


@pytest.fixture
def main_page(login_page, registered_user):
    def _main_page() -> MainPage:
        new_user = registered_user()
        new_login_page = login_page()
        return new_login_page.login(new_user)
    yield _main_page


@pytest.fixture
def new_spending_page(main_page):
    def _new_spending_page() -> NewSpendingPage:
        new_main_page = main_page()
        return new_main_page.go_to_new_spending_page()
    yield _new_spending_page


@pytest.fixture
def profile_page(main_page):
    def _profile_page() -> ProfilePage:
        new_main_page = main_page()
        return new_main_page.go_to_profile_page()
    yield _profile_page


@pytest.fixture
def friends_page(main_page):
    def _friends_page() -> FriendsPage:
        new_main_page = main_page()
        return new_main_page.go_to_friends_page()
    yield _friends_page


@pytest.fixture
def all_people_page(main_page):
    def _all_people_page() -> AllPeoplePage:
        new_main_page = main_page()
        return new_main_page.go_to_all_people_page()
    yield _all_people_page
