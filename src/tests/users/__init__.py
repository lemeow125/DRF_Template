"""
Post-migrate signal handlers for creating initial data for accounts app.
"""

import os
import json
import logging

from accounts.models import CustomUser
from core.settings import config, TESTS_DIR

logger = logging.getLogger(__name__)


def get_users_json():
    """
    Function to read test user data from JSON file
    """
    with open(os.path.join(TESTS_DIR, "users", "users.json"), "r") as f:
        # Load JSON data
        data = json.loads(f.read())
        return data


def generate_test_users():
    """
    Function to create test users.
    """
    data = get_users_json()

    for user in data["users"]:
        # Check if user already exists
        USER = CustomUser.objects.filter(username=user["username"]).first()
        if not USER:
            # Create user
            if user["is_superuser"]:
                USER = CustomUser.objects.create_superuser(
                    username=user["username"],
                    email=user["email"],
                    password=config.DEBUG_USER_PASSWORD,
                )
                logger.info("Created Superuser:", user["username"])
            else:
                USER = CustomUser.objects.create_user(
                    username=user["username"],
                    email=user["email"],
                    password=config.DEBUG_USER_PASSWORD,
                )
                logger.info("Created User:", user["username"])

            # Additional user fields not covered by create() methods
            USER.first_name = user["first_name"]
            USER.last_name = user["last_name"]
            USER.is_active = True
            USER.save()


def remove_test_users():
    """
    Function to remove test users in DEBUG mode.
    """
    if config.DEBUG:
        data = get_users_json()
        for user in data["users"]:
            # Check if user already exists
            USER = CustomUser.objects.filter(username=user["username"]).first()
            if USER:
                USER.delete()
            else:
                logger.warning(
                    f"Skipping user deletion for {user['username']}: Does not exist"
                )
