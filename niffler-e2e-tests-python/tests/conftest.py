from typing import List

import pytest
from string import ascii_lowercase

from playwright.sync_api import Playwright, Locator, expect

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
    page.set_default_timeout(10000)
    yield page
    page.close()


# Page object

@dataclass
class BasePage:
    page: Page

    def check_elements(self):
        raise NotImplementedError('Метод не переопределён')


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
        self.create_account_button = self.page.locator('a[href="/register"]')

        self.check_elements()

    def check_elements(self):
        elements = [
            (self.username_field, "Username field"),
            (self.password_field, "Password field"),
            (self.login_button, "Login button"),
            (self.create_account_button, "Create account button")
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def arrange_login(self, user: User) -> None:
        """Prepare to login without expect"""
        self.page.screenshot(path='0.png')
        self.username_field.fill(user.username)
        self.password_field.fill(user.password)
        self.login_button.click()

    def login(self, user: User) -> 'MainPage':
        self.arrange_login(user)
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

        self.check_elements()

    def check_elements(self):
        elements = [
            (self.username_field, "Username field"),
            (self.password_field, "Password field"),
            (self.confirm_password_field, "Confirm password field"),
            (self.signup_button, "Signup button")
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def arrange_register_user(self, user: User) -> None:
        self.username_field.fill(user.username)
        self.password_field.fill(user.password)
        self.confirm_password_field.fill(user.password)
        self.signup_button.click()

    def register_user(self, user: User) -> LoginPage:
        self.arrange_register_user(user)
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
        self.menu_button = self.page.locator('button[aria-label="Menu"]')
        self.search_field = self.page.locator('input[aria-label="search"]')
        self.delete_button = self.page.locator('#delete')
        self.profile_menu = self.page.locator('ul[role="menu"]')

    def check_elements(self):
        elements = [
            (self.new_spending_button, "New spending button"),
            (self.menu_button, "Menu button"),
            (self.search_field, "Search field"),
            (self.delete_button, "Delete button"),
            *[(spend, "Spend") for spend in self.spend_list],
            (self.profile_menu, "Profile menu"),
            (self.profile_tab, "Profile tab"),
            (self.friends_tab, "Friends tab"),
            (self.all_people_tab, "All people tab"),
            (self.sign_out_tab, "Sign out tab"),
            (self.log_out_button, "Log out button"),
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def go_to_new_spending_page(self) -> 'NewSpendingPage':
        self.new_spending_button.click()
        self.page.wait_for_url(re.compile('spending'))
        return NewSpendingPage(self.page)

    def go_to_profile_page(self) -> 'ProfilePage':
        self.profile_tab.click()
        self.page.wait_for_url(re.compile('profile'))
        return ProfilePage(self.page)

    def go_to_friends_page(self) -> 'FriendsPage':
        self.friends_tab.click()
        self.page.wait_for_url(re.compile('people/friends'))
        return FriendsPage(self.page)

    def go_to_all_people_page(self) -> 'AllPeoplePage':
        self.all_people_tab.click()
        self.page.wait_for_url(re.compile('people/all'))
        return AllPeoplePage(self.page)

    def open_menu(self) -> None:
        if not self.profile_menu.is_visible():
            self.menu_button.click()

    def get_menu_item(self, index: int) -> Locator:
        self.open_menu()
        return self.profile_menu.locator(f'li:nth-child({index})')

    # INFO: computed properties block

    @property
    def spend_list(self):
        return self.page.locator('table tbody tr[role="checkbox"]').all()

    @property
    def profile_tab(self) -> Locator:
        return self.get_menu_item(1)

    @property
    def friends_tab(self) -> Locator:
        return self.get_menu_item(3)

    @property
    def all_people_tab(self) -> Locator:
        return self.get_menu_item(4)

    @property
    def sign_out_tab(self) -> Locator:
        return self.get_menu_item(6)

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

        self.check_elements()

    def check_elements(self):
        elements = [
            (self.amount_field, "Amount field"),
            (self.currency_field, "Currency field"),
            (self.category_field, "Category field"),
            (self.date_field, "Date field"),
            (self.description_field, "Description field"),
            (self.cancel_button, "Cancel button"),
            (self.add_button, "Add button"),
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

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
        self.save_changes_button = self.page.locator('#:r7:')
        self.new_category_field = self.page.locator('#category')

        self.check_elements()

    @property
    def name_field(self) -> Locator:
        return self.page.locator('#name')

    @property
    def categories_list(self) -> List[Locator]:
        return self.page.locator('.css-17u3xlq').all()

    def check_elements(self):
        elements = [
            (self.username_field, "Username field"),
            (self.name_field, "Name field"),
            (self.save_changes_button, "Save changes button"),
            (self.new_category_field, "new category field"),
            *[(category, "Category") for category in self.categories_list],
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def change_name(self, name: str) -> None:
        self.name_field.fill(name)
        self.save_changes_button.click()

    def add_category(self, category: str) -> None:
        self.new_category_field.fill(category)
        self.page.keyboard.press('Enter')


class FriendsPage(BasePage):
    search_field: Locator
    request_list: List[Locator]
    friend_list: List[Locator]

    def __init__(self, page: Page):
        super().__init__(page)

        self.search_field = self.page.locator('input[aria-label="search"]')

        self.check_elements()

    @property
    def request_list(self) -> List[Locator]:
        return self.page.locator('#requests tr').all()

    @property
    def friend_list(self) -> List[Locator]:
        return self.page.locator('#friends tr').all()

    def check_elements(self):
        elements = [
            (self.search_field, "Search field"),
            *[(request, "Request") for request in self.request_list],
            *[(friend, "Friend") for friend in self.friend_list],
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def get_corresponding_request(self, username: str) -> Locator:
        """Получить соответствующий запрос от username"""
        if len(self.request_list) == 0:
            raise AssertionError(f'Request list is empty')

        corresponding_request: Locator | None = next((request for request in self.request_list if request.locator(
            '.MuiTypography-body1').text_content() == username), None)
        if corresponding_request is None:
            raise AssertionError(f'No such user with username {username} in request list')

        return corresponding_request

    def accept_request(self, username: str) -> None:
        """Принять приглашение в друзья от username"""
        corresponding_request: Locator = self.get_corresponding_request(username)
        accept_button: Locator = corresponding_request.locator('button:has-text("Accept")')
        accept_button.click()

        new_friend: Locator | None = next((friend for friend in self.friend_list if friend.locator('.MuiTypography-body1').text_content() == username), None)
        assert new_friend is not None

    def decline_request(self, username: str) -> None:
        """Отклонить приглашение в друзья от username"""
        corresponding_request: Locator = self.get_corresponding_request(username)
        decline_button: Locator = corresponding_request.locator('button:has-text("Decline")')
        decline_button.click()

        decline_confirm_button: Locator = self.page.locator('div[role="dialog"] button:has-text("Decline")')

        # INFO: should the string below be in page class? Answer me plz if there is a better way to handle it...
        expect(decline_confirm_button).to_be_visible()

        decline_confirm_button.click()

    def unfriend(self, username: str) -> None:
        """Удалить username из друзей"""
        if len(self.friend_list) == 0:
            raise AssertionError(f'Friend list is empty')

        corresponding_friend: Locator | None = next((friend for friend in self.friend_list if
                                                     friend.locator('.MuiTypography-body1').text_content() == username),
                                                    None)
        if corresponding_friend is None:
            raise AssertionError(f'No such user with username {username} in friend list')

        unfriend_button: Locator = corresponding_friend.locator('button:has-text("Unfriend")')
        unfriend_button.click()

        confirm_unfriend_button: Locator = self.page.locator('div[role="dialog"] button:has-text("Delete")')

        # INFO: should the string below be in page class? Answer me plz if there is a better way to handle it...
        expect(confirm_unfriend_button).to_be_visible()

        confirm_unfriend_button.click()


class AllPeoplePage(BasePage):
    search_field: Locator
    people_list: List[Locator]

    def __init__(self, page: Page):
        super().__init__(page)

        self.search_field = self.page.locator('input[aria-label="search"]')

        self.check_elements()

    @property
    def people_list(self) -> List[Locator]:
        return self.page.locator('#all tr').all()

    def check_elements(self):
        elements = [
            (self.search_field, "Search field"),
            *[(user, "User") for user in self.people_list],
        ]

        for element, name in elements:
            expect(element, f"{name} should be visible").to_be_visible()

    def get_corresponding_user(self, username: str) -> Locator:
        """Получить пользователя с username для приглашения"""
        if len(self.people_list) == 0:
            raise AssertionError(f'People list is empty')

        self.search_field.fill(username)
        self.page.keyboard.press('Enter')
        self.page.wait_for_load_state('networkidle')

        print(f'People length: {len(self.people_list)}')

        for user in self.people_list:
            current_username = user.locator('.MuiTypography-body1').text_content()
            if current_username == username:
                return user

        raise AssertionError(f'No such user with username {username} in people list')
        # corresponding_user: Locator = next((user for user in self.people_list if user.locator('.MuiTypography-body1').text_content() == username), None)
        # if corresponding_user is None:
        #     raise AssertionError(f'No such user with username {username} in people list')
        #
        # return corresponding_user

    def send_invitation(self, username: str) -> None:
        """Отправить приглашение в друзья пользователю с username"""
        corresponding_user: Locator = self.get_corresponding_user(username)
        add_friend_button: Locator = corresponding_user.locator('button:has-text("Add friend")')
        add_friend_button.click()

        expect(corresponding_user.locator('span:has-text("Waiting...")'))


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
