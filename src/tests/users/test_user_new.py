import pytest
from users import generate_test_users, remove_test_users

from accounts.models import CustomUser


def assert_users_exist(USERS: list[CustomUser] = []):
    """
    Asserts that each user in the provided list exists in the database.

    Args:
        USERS (list[CustomUser], optional): A list of CustomUser instances to check for existence. Defaults to an empty list.

    Raises:
        AssertionError: If any user in the list does not exist in the database.
    """

    for USER in USERS:
        assert CustomUser.objects.filter(username=USER.username).first()


def assert_users_new(USERS: list[CustomUser] = []):
    """
    Asserts that each user in the provided list is new.

    Args:
        USERS (list[CustomUser], optional): A list of CustomUser instances to check. Defaults to an empty list.

    Raises:
        AssertionError: If any user in the list is not new
    """

    for USER in USERS:
        assert CustomUser.objects.filter(username=USER.username).first().is_new


@pytest.mark.django_db(transaction=True)
def test_user_creation_deletion():
    """
    Test multiple instances of user creations and deletions
    """
    USERS = generate_test_users()
    assert_users_exist(USERS)
    assert_users_new(USERS)
    remove_test_users(USERS)
