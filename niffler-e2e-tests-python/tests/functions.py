import os
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from playwright.sync_api import Page


def logout_with_user(page: Page):
    page.locator('button[aria-label="Menu"]').click()
    page.locator('ul[role="menu"] li:has-text("Sign out")').click()
    page.locator('button:has-text("Log out")').click()
    page.wait_for_url(re.compile('login'), wait_until='load')
