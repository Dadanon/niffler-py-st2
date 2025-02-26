import os
import re

import dotenv
from playwright.sync_api import sync_playwright, expect


dotenv.load_dotenv()


NIFFLER_FRONTEND_URL = os.getenv("NIFFLER_FRONTEND_URL")
NIFFLER_AUTH_URL = os.getenv("NIFFLER_AUTH_URL")


def test_login_error(niffler_user):
    """
    1. Go to main page
    2. Check if page is redirected
    2. Enter invalid credentials
    3. Get login error
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(NIFFLER_FRONTEND_URL)

        expect(page).to_have_url(re.compile(NIFFLER_AUTH_URL))  # Check redirection
        new_user = niffler_user()

        login_field, password_field = page.get_by_label('Username'), page.get_by_label('Password')
        login_field.fill(new_user.username)
        password_field.fill(new_user.password)
        page.get_by_role('button').get_by_text('Log in').click()

        expect(page).to_have_url(re.compile('error'))


def test_login_success(niffler_user):
    """
    1. Go to main page
    2. Click register button
    3. Register user and save
    4. Go to main page (it will be redirected, already checked id test_login_error)
    5. Fill fields with valid credentials and enter
    6. Check if page is main now
    """
    ...
