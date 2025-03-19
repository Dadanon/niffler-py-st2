import re

import pytest
from playwright.sync_api import sync_playwright, expect
from .functions import *
from .config import settings


@pytest.mark.active
def test_login_error(login_page, user):
    """
    Try to login with unregistered credentials and get error
    """
    # Arrange
    new_user = user()
    new_login_page = login_page

    # Act
    new_login_page.login_with_error(new_user)

    # Assert
    expect(new_login_page.page).to_have_url(re.compile('error'))


@pytest.mark.active
def test_register_success(registration_page, user):
    """
    Try to register successfully
    """
    # Arrange
    new_user = user()
    new_registration_page = registration_page

    # Act
    new_registration_page.register_user(new_user)


@pytest.mark.active
def test_register_error(registration_page, user):
    """
    Try to register unsuccessfully
    """
    # Arrange
    new_user = user(username_length=2, password_length=2)
    new_registration_page = registration_page

    # Act
    new_registration_page.arrange_register_user(new_user)

    # Assert
    expect(new_registration_page.page.get_by_role('link').get_by_text('Sign in')).not_to_be_visible()


def test_login_success(envs, registered_user):
    """
    1. Get registered user and page from fixture
    2. Go to main page (it will be redirected, already checked id test_login_error)
    3. Fill fields with valid credentials and enter
    4. Check if page is main now
    """
    # INFO: we have already tested registration in other test so we only have to use already registered user from fixture
    with sync_playwright() as p:
        registered_user, page = registered_user(p)
        page.goto(envs.frontend_url)

        login_with_user(page, registered_user)

        expect(page).to_have_url(re.compile('main'))
