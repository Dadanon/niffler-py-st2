import re

import pytest
from playwright.sync_api import sync_playwright, expect, Locator
from .functions import *


@pytest.mark.parametrize('invalid_amount', [0, -200])
def test_add_spending_invalid_amount(envs, registered_user, spend, invalid_amount):
    """
    1. Get registered user and page from fixture
    2. Login
    3. Click New spending button
    4. Enter invalid amount
    5. Select currency
    6. Fill new category field
    7. Select date
    8. Fill description field
    9. Click Add button
    10. Check if there is the same page
    11. Check if there is warning message about amount
    """
    with sync_playwright() as p:
        registered_user, page = registered_user(p)
        print(f'username: {registered_user.username}, password: {registered_user.password}')
        page.goto(envs.frontend_url)
        login_with_user(page, registered_user)
        page.get_by_role('link').get_by_text('New spending').click()

        expect(page).to_have_url(re.compile('spending'))  # Check if page url relates to spending create

        new_spend: Spend = spend()
        page.get_by_label('Amount').fill(str(invalid_amount))

        # Выбираем валюту из выпадающего списка
        page.locator('#currency').click()
        page.locator(f'ul[role="listbox"] >> li:has-text("{new_spend.currency.value["value"]}")').click()

        expect(page.locator('input[name="currency"]')).to_have_value(new_spend.currency.value['value'])

        page.locator('#category').fill(new_spend.category)
        page.locator('input[name="date"]').fill(new_spend.date)
        page.get_by_label('Description').fill(new_spend.description)
        page.get_by_role('button').get_by_text('Add').click()

        expect(page).to_have_url(
            re.compile('spending'))

        expect(page.locator('label:has-text("Amount")').locator('..').locator('.input__helper-text')).to_be_visible()


def test_add_spending_absent_category(envs, registered_user, spend):
    """
    1. Get registered user and page from fixture
    2. Login
    3. Click New spending button
    4. Enter amount
    5. Select currency
    6. Do not fill category field
    7. Select date
    8. Fill description field
    9. Click Add button
    10. Check if there is the same page
    11. Check if there is warning message about category
    """
    with sync_playwright() as p:
        registered_user, page = registered_user(p)
        print(f'username: {registered_user.username}, password: {registered_user.password}')
        page.goto(envs.frontend_url)
        login_with_user(page, registered_user)
        page.get_by_role('link').get_by_text('New spending').click()

        expect(page).to_have_url(re.compile('spending'))  # Check if page url relates to spending create

        new_spend: Spend = spend()
        page.get_by_label('Amount').fill(str(new_spend.amount))

        # Выбираем валюту из выпадающего списка
        page.locator('#currency').click()
        page.locator(f'ul[role="listbox"] >> li:has-text("{new_spend.currency.value["value"]}")').click()

        expect(page.locator('input[name="currency"]')).to_have_value(new_spend.currency.value['value'])

        page.locator('input[name="date"]').fill(new_spend.date)
        page.get_by_label('Description').fill(new_spend.description)
        page.get_by_role('button').get_by_text('Add').click()

        expect(page).to_have_url(
            re.compile('spending'))

        expect(page.locator('label:has-text("Category")').locator('..').locator('.input__helper-text')).to_be_visible()


def test_add_spending_success(envs, registered_user, spend):
    """
    1. Get registered user and page from fixture
    2. Login
    3. Click New spending button
    4. Enter amount of spending
    5. Select currency
    6. Fill new category field
    7. Select date
    8. Fill description field
    9. Click Add button
    10. Check if there are only one spend in list
    11. Check if fields of this single spend are equal to entered fields
    """
    with sync_playwright() as p:
        registered_user, page = registered_user(p)
        print(f'username: {registered_user.username}, password: {registered_user.password}')
        page.goto(envs.frontend_url)
        login_with_user(page, registered_user)
        page.get_by_role('link').get_by_text('New spending').click()

        expect(page).to_have_url(re.compile('spending'))  # Check if page url relates to spending create

        new_spend: Spend = spend()
        page.get_by_label('Amount').fill(str(new_spend.amount))

        # Выбираем валюту из выпадающего списка
        page.locator('#currency').click()
        page.locator(f'ul[role="listbox"] >> li:has-text("{new_spend.currency.value["value"]}")').click()

        expect(page.locator('input[name="currency"]')).to_have_value(new_spend.currency.value['value'])

        page.locator('#category').fill(new_spend.category)
        page.locator('input[name="date"]').fill(new_spend.date)
        page.get_by_label('Description').fill(new_spend.description)
        page.get_by_role('button').get_by_text('Add').click()
        page.wait_for_url(re.compile('main'), wait_until='load')
        expect(page).to_have_url(
            re.compile('main'))  # Check if there is redirect to main page after successful spend create

        page.wait_for_selector('table')
        spend_rows = page.locator('table[aria-labelledby="tableTitle"] tbody tr').all()
        assert (len(spend_rows) == 1)

        spend_row: Locator = spend_rows[0]
        spend_row_cells: list[Locator] = spend_row.locator('td').all()
        # INFO: дальше жёстко зависит от порядка, не очень нравится, но каких-то отличающихся атрибутов в html нет(
        expect(spend_row_cells[1].locator('span')).to_have_text(new_spend.category)
        expect(spend_row_cells[2].locator('span')).to_have_text(
            str(new_spend.amount) + ' ' + new_spend.currency.value['sign'])
        expect(spend_row_cells[3].locator('span')).to_have_text(new_spend.description)
        expect(spend_row_cells[4].locator('span')).to_have_text(
            datetime.strptime(new_spend.date, SPEND_CREATE_DATE_FORMAT).strftime(SPEND_SHOW_DATE_FORMAT))


def test_delete_spend(niffler_add_spend):
    """
    1. Create registered user, login and create spend, get page and new spend from fixture
    2. Check if there is only one spend in list
    3. Click by checkbox of first spend in list
    4. Check if Delete button is available now
    5. Click Delete button
    6. Check if there is modal confirmation window
    7. Click Delete button in modal
    8. Wait for modal to close
    9. Check if there are no more spends in list
    """
    with sync_playwright() as p:
        page, new_spend = niffler_add_spend(p)
        spend_rows = page.locator('table[aria-labelledby="tableTitle"] tbody tr').all()
        assert (len(spend_rows) == 1)

        spend_row: Locator = spend_rows[0]
        spend_row_cells: list[Locator] = spend_row.locator('td').all()
        spend_row_cells[0].get_by_role('checkbox').click()

        expect(page.get_by_role('button').get_by_text('Delete')).to_be_enabled()

        page.get_by_role('button').get_by_text('Delete').click()

        expect(page.get_by_role('dialog')).to_be_visible()
        expect(page.get_by_role('dialog').get_by_role('button').get_by_text('Delete')).to_be_visible()

        page.get_by_role('dialog').get_by_role('button').get_by_text('Delete').click()

        expect(page.get_by_role('dialog')).to_have_count(0)  # Wait for modal to close

        spend_rows = page.locator('table[aria-labelledby="tableTitle"] tbody tr').all()
        assert (len(spend_rows) == 0)


def test_edit_spend(niffler_add_spend, spend):
    """
    1. Create registered user, login and create spend, get page and new spend from fixture
    2. Check if there is only one spend in list
    3. Check if Edit button is available now for this record
    4. Click Edit button
    5. Check if page is redirected to edit spend
    6. Save spend uuid
    5. Change amount
    6. Change currency
    7. Change category
    8. Change date
    9. Change description
    10. Check if Save changes button is available
    11. Click Save changes button
    12. Check if there is only one spend in list
    13. Check if this one record fields are equal to entered fields
    """
    with sync_playwright() as p:
        page, new_spend = niffler_add_spend(p)
        spend_rows = page.locator('table[aria-labelledby="tableTitle"] tbody tr').all()
        assert (len(spend_rows) == 1)

        spend_row: Locator = spend_rows[0]
        spend_row_cells: list[Locator] = spend_row.locator('td').all()
        edit_spend_button: Locator = spend_row_cells[-1].locator('button[aria-label="Edit spending"]')

        expect(edit_spend_button).to_be_visible()

        edit_spend_button.click()

        expect(page).to_have_url(re.compile('spending'))  # Check if page url relates to spending edit

        spend_uuid: str = page.url.split('/')[-1]

        edited_spend: Spend = spend()
        page.get_by_label('Amount').fill(str(edited_spend.amount))

        page.locator('#currency').click()
        page.locator(f'ul[role="listbox"] >> li:has-text("{edited_spend.currency.value["value"]}")').click()

        page.locator('#category').fill(edited_spend.category)
        page.locator('input[name="date"]').fill(edited_spend.date)
        page.get_by_label('Description').fill(edited_spend.description)

        expect(page.locator('button[type="submit"]')).to_be_visible()

        page.locator('button[type="submit"]').click()
        page.wait_for_url(re.compile('main'), wait_until='load')

        expect(page).to_have_url(
            re.compile('main'))  # Check if there is redirect to main page after successful spend edit

        page.wait_for_selector('table')
        spend_rows = page.locator('table[aria-labelledby="tableTitle"] tbody tr').all()
        assert (len(spend_rows) == 1)

        spend_row: Locator = spend_rows[0]
        spend_row_cells: list[Locator] = spend_row.locator('td').all()

        expect(spend_row_cells[1].locator('span')).to_have_text(edited_spend.category)
        expect(spend_row_cells[2].locator('span')).to_have_text(
            str(edited_spend.amount) + ' ' + edited_spend.currency.value['sign'])
        expect(spend_row_cells[3].locator('span')).to_have_text(edited_spend.description)
        expect(spend_row_cells[4].locator('span')).to_have_text(
            datetime.strptime(edited_spend.date, SPEND_CREATE_DATE_FORMAT).strftime(SPEND_SHOW_DATE_FORMAT))

        edit_spend_button: Locator = spend_row_cells[-1].locator('button[aria-label="Edit spending"]')

        expect(edit_spend_button).to_be_visible()
        edit_spend_button.click()

        new_spend_uuid: str = page.url.split('/')[-1]
        assert new_spend_uuid == spend_uuid  # Проверка, что это именно старая запись с тем же uuid
