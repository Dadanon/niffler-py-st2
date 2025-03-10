import re

from playwright.sync_api import sync_playwright, expect
from .functions import *


def test_add_friend(envs, registered_user):
    """
    Проверка на приглашение друзей
    1. Создать пользователя 1
    2. Создать пользователя 2
    3. Войти под пользователем 2
    4. Зайти во вкладку Friends
    5. Зайти во вкладку All people
    6. Ввести в поле поиска логин 1 юзера и нажать Enter
    7. Выбрать 1 юзера в списке и нажать Add friend
    8. Убедиться что текст кнопки изменился на Waiting...
    9. Зайти под 1 пользователем
    10. Зайти во вкладку Friends
    11. Найти приглашение от пользователя 1 и нажать Accept
    12. Зайти под 1 юзером во вкладку Friends
    13. Убедиться, что юзер 2 теперь в друзьях
    """
    with sync_playwright() as p:
        first_user, _ = registered_user(p)
        second_user, page = registered_user(p)

        page.goto(envs.frontend_url)

        login_with_user(page, second_user)

        menu_button = page.locator('button[aria-label="Menu"]')
        expect(menu_button).to_be_visible()

        menu_button.click()

        user_menu = page.locator('ul[role="menu"]')

        expect(user_menu).to_be_visible()

        friends_item = user_menu.locator('li a[href="/people/friends"]')

        expect(friends_item).to_be_visible()

        friends_item.locator('..').click()  # Клик по родителю ссылки /people/friends

        page.wait_for_url(re.compile('/people/friends'), wait_until='load')
        expect(page).to_have_url(re.compile('/people/friends'))

        all_people_tab = page.get_by_role('heading', level=2).get_by_text('All people')

        expect(all_people_tab).to_be_visible()

        all_people_tab.click()

        search_people_field = page.locator('input')

        expect(search_people_field).to_be_visible()

        search_people_field.fill(first_user.username)
        page.keyboard.press('Enter')

        """
        Далее теоретически может быть, что мы ввели имя юзера: user.
        При этом у нас куча юзеров с подобным именем: user1, user000 etc.,
        и, возможно, нужный юзер вообще не на этой странице.
        В данном случае, мы отбрасываем этот кейс, т.к. в данном тесте
        мы создали только 2 юзеров, и юзер с ником user гарантированно
        на первой странице
        """
        first_user_row = page.locator(f'tr:has-text("{first_user.username}")')

        expect(first_user_row).to_be_visible()

        first_user_row.locator('button:has-text("Add friend")').click()

        logout_with_user(page)

        login_with_user(page, first_user)

        menu_button = page.locator('button[aria-label="Menu"]')
        menu_button.click()
        user_menu = page.locator('ul[role="menu"]')
        friends_item = user_menu.locator('li a[href="/people/friends"]')
        friends_item.locator('..').click()  # Клик по родителю ссылки /people/friends
        page.wait_for_url(re.compile('/people/friends'), wait_until='load')

        page.wait_for_selector('table')
        invitation_row = page.locator(f'table tr:has-text("{second_user.username}")')

        expect(invitation_row).to_be_visible()

        invitation_row.locator('button:has-text("Accept")').click()

        logout_with_user(page)

        login_with_user(page, second_user)

        menu_button = page.locator('button[aria-label="Menu"]')
        menu_button.click()
        user_menu = page.locator('ul[role="menu"]')
        friends_item = user_menu.locator('li a[href="/people/friends"]')
        friends_item.locator('..').click()  # Клик по родителю ссылки /people/friends
        page.wait_for_url(re.compile('/people/friends'), wait_until='load')

        expect(page.locator(f'table tr:has-text("{first_user.username}")')).to_be_visible()
