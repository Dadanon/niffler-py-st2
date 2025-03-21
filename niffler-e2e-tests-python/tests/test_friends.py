import pytest


@pytest.mark.single
def test_add_friend(registered_user, login_page):
    # Arrange
    first_user = registered_user()
    second_user = registered_user()
    first_main_page = login_page.login(first_user)

    # Act
    first_all_people_page = first_main_page.go_to_all_people_page()  # Go to all people page from 1st user
    first_all_people_page.send_invitation(second_user.username)  # Send invitation to 2nd user

    second_main_page = login_page.login(second_user)
    second_friends_page = second_main_page.go_to_friends_page()
    second_friends_page.accept_request(first_user.username)

    # TODO: закончить 210325
