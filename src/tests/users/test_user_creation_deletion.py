import pytest
import users

from accounts.models import CustomUser


def assert_users_created():
    data = users.get_users_json()

    for user in data["users"]:
        USER = CustomUser.objects.filter(username=user["username"]).first()

        # Assert user exists
        assert USER

        if user["is_superuser"]:
            # Assert is superuser
            assert USER.is_superuser


def assert_users_removed():
    data = users.get_users_json()
    for user in data["users"]:
        USER = CustomUser.objects.filter(username=user["username"]).first()

        # Assert user does not exist
        assert not USER


@pytest.mark.django_db(transaction=True)
def test_user_creation_deletion():
    """
    Test user creation and deletion
    """
    users.generate_test_users()
    assert_users_created()
    users.remove_test_users()
    assert_users_removed()
