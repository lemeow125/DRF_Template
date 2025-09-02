"""
Post-migrate signal handlers for creating initial data for accounts app.
"""

import logging

from django.core.management.base import BaseCommand

from tests.users import generate_test_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate debug admin and test user accounts."

    def handle(self, *args, **kwargs):
        """
        Command handling
        """
        generate_test_users()
