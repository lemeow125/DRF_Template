"""
Signal handlers for accounts app.
"""

import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from core.settings import config
from tests import users

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def generate_test_users(sender, **kwargs):
    """
    Post-migrate signal to create test users in DEBUG mode.
    """
    if sender.name == "accounts" and config.DEBUG:
        try:
            users.generate_test_users()
        except Exception as e:
            logger.error(f"Error creating test users post-migration: {e}")
