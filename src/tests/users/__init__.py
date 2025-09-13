"""
Post-migrate signal handlers for creating initial data for accounts app.
"""

import logging
from faker import Faker

from accounts.models import CustomUser
from core.settings import config

logger = logging.getLogger(__name__)
fake = Faker()


def generate_random_user(active: bool = False):
    """
    Function to generate a single random user

    Args:
        active (bool, optional): User active status. Defaults to False.

    Returns:
        CustomUser: Newly created USER instance
    """
    USER = CustomUser.objects.create_user(
        username=fake.user_name(),
        email=fake.email(),
        password=config.DEBUG_USER_PASSWORD,
    )

    # Additional user fields not covered by create() method
    USER.first_name = fake.first_name()
    USER.last_name = fake.last_name()
    USER.is_active = active
    USER.save()

    return USER


def generate_superuser():
    """
    Function to generate a test superuser account
    """
    USER = CustomUser.objects.filter(is_superuser=True).first()
    if not USER:
        CustomUser.objects.create_superuser(
            username=config.DEBUG_USER_USERNAME,
            email=config.DEBUG_USER_EMAIL,
            password=config.DEBUG_USER_PASSWORD,
        )
    return USER


def generate_test_users(count=3, active: bool = False) -> list[CustomUser]:
    """
    Function to generate a list of test users.

    Args:
        count (int, optional): Number of regular test users to generate. Defaults to 10.

    Returns:
        list[CustomUser]: List containing the test superuser and generated regular users.
    """
    USERS = []

    # Superuser
    USERS.append(generate_superuser())

    # Regular users
    USERS.extend([generate_random_user(active=active) for _ in range(count)])

    return USERS


def remove_test_users(
    USERS: list[CustomUser] = CustomUser.objects.filter(
        is_superuser=False),
):
    """
    Function to remove test users.
    """

    for USER in USERS:
        USER = CustomUser.objects.filter(username=USER.username).first()
        if USER:
            USER.delete()
        else:
            logger.warning(
                f"Skipping user deletion for {USER.username}: Does not exist"
            )
