import pytest

from services.user_service import user_service


@pytest.mark.active
def test_add_friend(registered_user, friend_user, login_page):
    # Arrange
    main_user = registered_user
    friend = friend_user
    first_main_page = login_page().login(main_user)

    # Act
    first_all_people_page = first_main_page.go_to_all_people_page()  # Go to all people page from 1st user
    first_all_people_page.send_invitation(friend.username)  # Send invitation to 2nd user

    second_main_page = login_page().login(friend)
    second_friends_page = second_main_page.go_to_friends_page()
    second_friends_page.accept_request(main_user.username)

    # Asserts in database
    assert user_service.friend_exists(main_user.username, friend.username) is True
    # Remove friendship from db
    user_id = user_service.get_user_id_by_username(main_user.username)
    user_service.delete_user_friendships(user_id)
