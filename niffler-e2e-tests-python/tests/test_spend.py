import re

import pytest
from playwright.sync_api import expect

from services.spend_service import spend_service
from .conftest import NewSpendingPage
from config import *


@pytest.mark.active
@pytest.mark.parametrize('invalid_amount', [0, -200])
def test_add_spending_invalid_amount(new_spending_page, spend, invalid_amount):
    # Arrange
    spending_page: NewSpendingPage = new_spending_page()
    new_spend = spend()
    new_spend.amount = invalid_amount

    # Act
    spending_page.arrange_add_spend(new_spend)

    # Assert
    expect(spending_page.page).to_have_url(re.compile('spending'))
    expect(spending_page.amount_helper).to_be_visible()
    # Проверяем что в БД нет записей
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 0


@pytest.mark.active
def test_add_spending_absent_category(new_spending_page, spend):
    # Arrange
    spending_page: NewSpendingPage = new_spending_page()
    new_spend = spend()
    new_spend.category = ""

    # Act
    spending_page.arrange_add_spend(new_spend)

    # Assert
    expect(spending_page.page).to_have_url(re.compile('spending'))
    expect(spending_page.category_helper).to_be_visible()
    # Проверяем что в БД нет записей
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 0


@pytest.mark.active
def test_add_spending_success(new_spending_page, spend):
    # Arrange
    spending_page: NewSpendingPage = new_spending_page()
    new_spend = spend()

    # Act
    new_main_page = spending_page.add_spend(new_spend)

    # Assert
    assert len(new_main_page.spend_list) == 1
    first_spend = new_main_page.get_nth_spend(0)

    assert first_spend.category == new_spend.category
    assert first_spend.amount == new_spend.amount
    assert first_spend.currency == new_spend.currency
    assert first_spend.description == new_spend.description
    assert first_spend.spend_date == datetime.strptime(new_spend.spend_date, SPEND_CREATE_DATE_FORMAT).strftime(SPEND_SHOW_DATE_FORMAT)
    # Проверяем, что в БД появились записи
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 1
    # Remove user spends from db
    spend_service.delete_user_spends(settings.REGISTERED_USERNAME)


@pytest.mark.active
def test_delete_spend(new_spending_page, spend):
    # Arrange
    spending_page: NewSpendingPage = new_spending_page()
    new_spend = spend()

    # Act
    new_main_page = spending_page.add_spend(new_spend)
    assert len(new_main_page.spend_list) == 1
    # Проверяем что в БД появилась трата
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 1

    new_main_page.select_spend_in_list(0)
    
    expect(new_main_page.delete_button).to_be_enabled()
    
    new_main_page.delete_button.click()
    
    expect(new_main_page.delete_confirm_dialog).to_be_visible()
    expect(new_main_page.delete_confirm_button).to_be_visible()

    new_main_page.delete_confirm_button.click()

    expect(new_main_page.delete_confirm_dialog).not_to_be_visible()
    assert len(new_main_page.spend_list) == 0
    # Проверяем, что в БД больше нет трат
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 0


@pytest.mark.active
def test_edit_spend(new_spending_page, spend):
    # Arrange
    spending_page: NewSpendingPage = new_spending_page()
    new_spend = spend()
    new_spend_edited = spend()

    # Act
    new_main_page = spending_page.add_spend(new_spend)

    assert len(new_main_page.spend_list) == 1
    # Проверяем что в БД появилась трата
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 1

    new_edit_spending_page = new_main_page.edit_spend_in_list(0)
    new_spend_uuid = new_edit_spending_page.spend_uuid

    new_main_page_after_edit = new_edit_spending_page.edit_spend(new_spend_edited)

    assert len(new_main_page_after_edit.spend_list) == 1
    # Проверяем что в БД до сих пор одна трата
    assert spend_service.get_user_spend_count(settings.REGISTERED_USERNAME) == 1

    new_spend_edited_in_list = new_main_page_after_edit.get_nth_spend(0)

    assert new_spend_edited_in_list.category == new_spend_edited.category
    assert new_spend_edited_in_list.amount == new_spend_edited.amount
    assert new_spend_edited_in_list.description == new_spend_edited.description
    assert new_spend_edited_in_list.currency == new_spend_edited.currency
    assert new_spend_edited_in_list.spend_date == datetime.strptime(new_spend_edited.spend_date, SPEND_CREATE_DATE_FORMAT).strftime(SPEND_SHOW_DATE_FORMAT)

    new_edit_spending_page_after_edit = new_main_page_after_edit.edit_spend_in_list(0)

    assert new_spend_uuid == new_edit_spending_page_after_edit.spend_uuid
    # Проверяем что в БД появилась трата
    assert spend_service.spend_exists(new_spend_uuid)
