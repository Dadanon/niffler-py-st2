from typing import List

import pytest
from string import ascii_lowercase

from playwright.sync_api import Playwright, Locator

from .functions import *
from .config import settings, User, Spend, MIN_AMOUNT, MAX_AMOUNT, Currency, CATEGORY_NAME_LENGTH, get_random_date, \
    SPEND_CREATE_DATE_FORMAT


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
    yield page
    page.close()


# Page object

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

    def login_with_error(self, user: User) -> None:
        """Try to login with unregistered credentials"""
        self.username_field.fill(user.username)
        self.password_field.fill(user.password)
        self.login_button.click()

    def login(self, user: User) -> 'MainPage':
        self.login_with_error(user)
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
    new_spending_button: Locator  # Кнопка новой траты
    menu_button: Locator  # Кнопка меню с аватарой
    search_field: Locator  # Поле поиска по тратам
    delete_button: Locator  # Кнопка удаления трат
    spend_list: List[Locator]  # Список трат
    profile_menu: Locator  # Выпадающее меню по нажатию кнопки меню

    def __init__(self, page: Page):
        super().__init__(page)

        self.new_spending_button = self.page.locator('a[href="/spending"]')
        self.menu_button = self.page.locator('button[aria-label="menu"]')
        self.search_field = self.page.locator('input[aria-label="search"]')
        self.delete_button = self.page.locator('#delete')
        self.spend_list: List[Locator] = self.page.locator('table tbody tr[role="checkbox"]').all()
        self.profile_menu = self.page.locator('ul[role="menu"]')

    def go_to_new_spending_page(self) -> 'NewSpendingPage':
        self.new_spending_button.click()
        self.page.wait_for_url(re.compile('spending'))
        return NewSpendingPage(self.page)

    def go_to_profile_page(self) -> 'ProfilePage':
        self.profile_tab.click()
        self.page.wait_for_url(re.compile('profile'))
        return ProfilePage(self.page)

    def open_menu(self) -> None:
        if not self.profile_menu.is_visible():
            self.menu_button.click()

    def get_menu_item(self, index: int) -> Locator:
        self.open_menu()
        return self.profile_menu.locator(f'li:nth-child({index})')

    # INFO: computed properties block

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

    @property
    def log_out_button(self) -> Locator:
        self.sign_out_tab.click()
        return self.page.locator('button:has-text("Log out")')


class NewSpendingPage(BasePage):
    amount_field: Locator
    currency_field: Locator
    category_field: Locator
    date_field: Locator
    description_field: Locator

    cancel_button: Locator
    add_button: Locator

    def __init__(self, page: Page):
        super().__init__(page)

        self.amount_field = self.page.locator('#amount')
        self.currency_field = self.page.locator('#currency')
        self.category_field = self.page.locator('#category')
        self.date_field = self.page.locator('#:re:')
        self.description_field = self.page.locator('#description')
        self.cancel_button = self.page.locator('#cancel')
        self.add_button = self.page.locator('#save')

    def add_spend(self, spend: Spend) -> 'MainPage':
        self.amount_field.fill(str(spend.amount))
        self.currency_field.click()
        self.page.locator(f'ul[role="listbox"] >> li[data-value={spend.currency.value["value"]}').click()
        self.category_field.fill(spend.category)
        self.date_field.fill(spend.date)
        self.description_field.fill(spend.description)
        self.add_button.click()
        self.page.wait_for_url(re.compile('main'))
        return MainPage(self.page)

    def cancel_add_spend(self) -> 'MainPage':
        self.cancel_button.click()
        self.page.wait_for_url(re.compile('main'))
        return MainPage(self.page)


class ProfilePage(BasePage):
    username_field: Locator
    name_field: Locator
    save_changes_button: Locator
    new_category_field: Locator
    categories_list: List[Locator]

    def __init__(self, page: Page):
        super().__init__(page)

        self.username_field = self.page.locator('#username')
        self.name_field = self.page.locator('#name')
        self.save_changes_button = self.page.locator('#:r7:')
        self.new_category_field = self.page.locator('#category')
        self.categories_list = self.page.locator('.css-17u3xlq').all()

    def change_name(self, name: str) -> None:
        self.name_field.fill(name)
        self.save_changes_button.click()

    def add_category(self, category: str) -> None:
        self.new_category_field.fill(category)
        self.page.keyboard.press('Enter')


# Advanced fixtures and also page fixtures

@pytest.fixture
def registered_user(page, user) -> User:
    login_page = LoginPage(page)
    registration_page = login_page.go_to_registration_page()
    new_user = user()
    registration_page.register_user(new_user)
    return new_user


@pytest.fixture
def login_page(page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def registration_page(login_page) -> RegistrationPage:
    return login_page.go_to_registration_page()


@pytest.fixture
def main_page(login_page, registered_user) -> MainPage:
    return login_page.login(registered_user)


@pytest.fixture
def new_spending_page(main_page) -> NewSpendingPage:
    return main_page.go_to_new_spending_page()


@pytest.fixture
def profile_page(main_page) -> ProfilePage:
    return main_page.go_to_profile_page()
