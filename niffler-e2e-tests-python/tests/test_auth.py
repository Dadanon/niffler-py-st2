import re

import pytest
from playwright.sync_api import expect


@pytest.mark.active
def test_login_error(login_page, user):
    """
    Try to login with unregistered credentials and get error
    """
    # Arrange
    new_user = user()
    new_login_page = login_page()

    # Act
    new_login_page.arrange_login(new_user)

    # Assert
    expect(new_login_page.page).to_have_url(re.compile('error'))


@pytest.mark.active
def test_register_success(registration_page, user):
    """
    Try to register successfully
    """
    # Arrange
    new_user = user()
    new_registration_page = registration_page()

    # Act
    new_registration_page.register_user(new_user)


@pytest.mark.active
def test_register_error(registration_page, user):
    """
    Try to register unsuccessfully
    """
    # Arrange
    new_user = user(username_length=2, password_length=2)
    new_registration_page = registration_page()

    # Act
    new_registration_page.arrange_register_user(new_user)

    # Assert
    expect(new_registration_page.page.get_by_role('link').get_by_text('Sign in')).not_to_be_visible()


@pytest.mark.active
def test_login_success(login_page, registered_user):
    """
    Try to login successfully with registered credentials
    """
    # Arrange
    new_login_page = login_page()
    new_user = registered_user()

    # Act
    new_login_page.login(new_user)
