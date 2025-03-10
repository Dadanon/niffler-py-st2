import re

from playwright.sync_api import sync_playwright, expect
from .functions import *
from .config import settings


def test_login_error(envs, user):
    """
    1. Go to main page
    2. Check if page is redirected
    2. Enter invalid credentials
    3. Get login error
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(envs.frontend_url)

        expect(page).to_have_url(re.compile(settings.AUTH_URL))  # Check redirection
        new_user = user()

        login_with_user(page, new_user)

        expect(page).to_have_url(re.compile('error'))


def test_register_success(envs, user):
    """
    1. Go to main page
    2. Click register button
    3. Register with valid credentials (username field length 10, password field length 10)
    4. Click submit button
    5. Check if sign in button is visible - it means successful registration
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(envs.frontend_url)
        page.get_by_role('link').get_by_text('Create new account').click()

        new_user = user()

        username_field, password_field, password_confirm_field = page.get_by_label('Username'), page.get_by_label('Password').first, page.get_by_label('Submit password')
        username_field.fill(new_user.username)
        password_field.fill(new_user.password)
        password_confirm_field.fill(new_user.password)
        page.get_by_role('button').get_by_text('Sign up').click()

        expect(page.get_by_role('link').get_by_text('Sign in')).to_be_visible()


def test_register_error(envs, user):
    """
    1. Go to main page
    2. Click register button
    3. Register with invalid credentials (username field length 2, password field length 2)
    4. Click submit button
    5. Check if sign in button is visible - it means successful registration
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(envs.frontend_url)
        page.get_by_role('link').get_by_text('Create new account').click()

        new_user = user(username_length=2, password_length=2)

        username_field, password_field, password_confirm_field = page.get_by_label('Username'), page.get_by_label('Password').first, page.get_by_label('Submit password')
        username_field.fill(new_user.username)
        password_field.fill(new_user.password)
        password_confirm_field.fill(new_user.password)
        page.get_by_role('button').get_by_text('Sign up').click()

        expect(page.get_by_role('link').get_by_text('Sign in')).not_to_be_visible()


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
