from typing import List

import pytest
from string import ascii_lowercase

from playwright.sync_api import Playwright, Locator

from .functions import *
from .config import settings, User, Spend, MIN_AMOUNT, MAX_AMOUNT, Currency, CATEGORY_NAME_LENGTH, get_random_date, \
    SPEND_CREATE_DATE_FORMAT


@pytest.fixture
def user():
    def _user(username_length: int = 10, password_length: int = 10):
        user: User = User(
            username=''.join(random.choice(ascii_lowercase) for _ in range(username_length)),
            password=''.join(random.choice(ascii_lowercase) for _ in range(password_length))
        )
        return user

    yield _user


@pytest.fixture(scope='session')
def browser(playwright: Playwright):
    browser = playwright.chromium.launch()
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def main_page(page, user):
    login_page = LoginPage(page)
    registration_page = login_page.go_to_registration_page()
    new_user = user()
    registration_page.register_user(new_user)
    return login_page.login(new_user)


@dataclass
class BasePage:
    page: Page


class LoginPage(BasePage):
    username_field: Locator
    password_field: Locator
    login_button: Locator
    create_account_button: Locator

    def __init__(self, page: Page):
        super().__init__(page)
        self.page.goto(settings.AUTH_URL)

        self.username_field = self.page.locator('input[name="username"]')
        self.password_field = self.page.locator('input[name="password"]')
        self.login_button = self.page.locator('button[type="submit"]')
        self.create_account_button = self.page.locator('a[href="register"]')

    def login(self, user: User) -> 'MainPage':
        self.username_field.fill(user.username)
        self.password_field.fill(user.password)
        self.login_button.click()
        self.page.wait_for_url(re.compile('main'))
        return MainPage(self.page)

    def go_to_registration_page(self) -> 'RegistrationPage':
        self.create_account_button.click()
        self.page.wait_for_url(re.compile('register'))
        return RegistrationPage(self.page)


class RegistrationPage(BasePage):
    username_field: Locator
    password_field: Locator
    confirm_password_field: Locator
    signup_button: Locator

    def __init__(self, page: Page):
        super().__init__(page)

        self.username_field = self.page.locator('#username')
        self.password_field = self.page.locator('#password')
        self.confirm_password_field = self.page.locator('#passwordSubmit')
        self.signup_button = self.page.locator('button[type="submit"]')

    def register_user(self, user: User) -> LoginPage:
        self.username_field.fill(user.username)
        self.password_field.fill(user.password)
        self.confirm_password_field.fill(user.password)
        self.signup_button.click()
        sign_in_button: Locator = self.page.locator('a[class="form_sign-in"]')
        sign_in_button.wait_for()
        sign_in_button.click()
        self.page.wait_for_url(re.compile('login'))
        return LoginPage(self.page)


class MainPage(BasePage):
    new_spending_button: Locator
    menu_button: Locator
    search_field: Locator
    delete_button: Locator
    spend_list: List[Locator]
    profile_menu: Locator

    def __init__(self, page: Page):
        super().__init__(page)

        self.new_spending_button = self.page.locator('a[href="/spending"]')
        self.menu_button = self.page.locator('button[aria-label="menu"]')
        self.search_field = self.page.locator('input[aria-label="search"]')
        self.delete_button = self.page.locator('#delete')
        self.spend_list: List[Locator] = self.page.locator('table tbody tr[role="checkbox"]').all()
        self.profile_menu = self.page.locator('ul[role="menu"]')

    def open_menu(self) -> None:
        if not self.profile_menu.is_visible():
            self.menu_button.click()

    def get_menu_item(self, index: int) -> Locator:
        self.open_menu()
        return self.page.locator(f'ul[role="menu"] li:nth-child({index})')

    @property
    def profile_tab(self) -> Locator:
        return self.get_menu_item(1)

    @property
    def friends_tab(self) -> Locator:
        return self.get_menu_item(2)

    @property
    def all_people_tab(self) -> Locator:
        return self.get_menu_item(3)

    @property
    def sign_out_tab(self) -> Locator:
        return self.get_menu_item(4)


class ProfilePage:
    ...


class SpendingPage:
    ...


@pytest.fixture
def registered_user(envs, user):
    """Get registered Niffler user and page to do not recreate it later"""

    def _registered_user(playwright: Playwright):
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(envs.frontend_url)
        page.get_by_role('link').get_by_text('Create new account').click()

        new_user = user()

        username_field, password_field, password_confirm_field = page.get_by_label('Username'), page.get_by_label(
            'Password').first, page.get_by_label('Submit password')
        username_field.fill(new_user.username)
        password_field.fill(new_user.password)
        password_confirm_field.fill(new_user.password)
        page.get_by_role('button').get_by_text('Sign up').click()
        return new_user, page

    yield _registered_user


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


@pytest.fixture
def niffler_add_spend(envs, registered_user, spend):
    """Create registered user, login and create spend"""

    def _niffler_add_spend(playwright: Playwright):
        new_user, page = registered_user(playwright)
        page.goto(envs.frontend_url)
        login_with_user(page, new_user)
        page.get_by_role('link').get_by_text('New spending').click()

        new_spend: Spend = spend()
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
