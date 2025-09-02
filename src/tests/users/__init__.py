"""
Post-migrate signal handlers for creating initial data for accounts app.
"""

import os
import json
import logging

from accounts.models import CustomUser
from core.settings import config, TESTS_DIR

logger = logging.getLogger(__name__)


def generate_test_users():
    """
    Function to create test users in DEBUG mode.
    """
    if config.DEBUG:
        with open(os.path.join(TESTS_DIR, "users", "users.json"), "r") as f:
            # Load JSON data
            data = json.loads(f.read())
            for user in data["users"]:
                # Check if user already exists
                USER = CustomUser.objects.filter(email=user["email"]).first()
                if not USER:
                    # Create user
                    if user["is_superuser"]:
                        USER = CustomUser.objects.create_superuser(
                            username=user["username"],
                            email=user["email"],
                            password=config.DEBUG_USER_PASSWORD,
                        )
                        print("Created Superuser:", user["email"])
                    else:
                        USER = CustomUser.objects.create_user(
                            username=user["email"],
                            email=user["email"],
                            password=config.DEBUG_USER_PASSWORD,
                        )
                        print("Created User:", user["email"])

                    # Additional user fields not covered by create() methods
                    USER.first_name = user["first_name"]
                    USER.last_name = user["last_name"]
                    USER.is_active = True
                    USER.save()
