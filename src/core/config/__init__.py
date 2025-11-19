"""
Common service functions and classes imported elsewhere.

For use in the immediate parent app/directory.
"""

import os
from datetime import timedelta
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from faker import Faker
from pydantic.fields import FieldInfo

from .models import Config as ConfigModel

fake = Faker()


class Config:
    """
    Core application config.
    """

    def __init__(
        self, prefix: Optional[str] = "backend", test: Optional[bool] = False
    ) -> None:
        """
        Initialize the Config class.

        Args:
            prefix (str, optional): Prefix for environment variables. Defaults to "backend".
            test (bool, optional): Generate test config. Defaults to False.
        """
        load_dotenv(find_dotenv())

        self.prefix = prefix.upper()

        if test:
            for field_name, field_info in ConfigModel.model_fields.items():
                setattr(
                    self, field_name, self._generate_faker_data(
                        field_name, field_info)
                )
        else:
            for field in ConfigModel.model_fields.items():
                setattr(self, field[0], self.set_env_var(field))

    def set_env_var(self, field: tuple):
        """
        Retrieve and sets an environment variable.

        Args:
            field (tuple): A tuple containing the field name and its FieldInfo.

        Returns:
            str: The value of the environment variable.

        Raises:
            RuntimeError: If required is True and the variable is not set.
        """

        # Unpack field info
        field_key = f"{self.prefix}_{field[0]}".upper()
        field_info: FieldInfo = field[1]

        # Fetch value, return field default value if not found
        field_value = os.getenv(field_key, field_info.default)

        return field_value

    def get_config(self) -> ConfigModel:
        """
        Get the config model.

        Returns:
            ConfigModel: The config model instance.
        """
        return ConfigModel(**self.__dict__)

    def _generate_faker_data(self, field_name: str, field_info) -> any:
        """
        Generate placeholder data using faker based on field name and type.

        Args:
            field_name (str): The name of the field.
            field_info: The pydantic field info object.

        Returns:
            any: Generated placeholder data.
        """
        field_type = field_info.annotation

        # Handle specific field names
        if field_name == "SECRET_KEY":
            return fake.sha256()
        elif field_name == "DEBUG":
            return False
        elif field_name == "TIMEZONE":
            return "Asia/Manila"
        elif field_name == "CORS_ORIGINS":
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        elif field_name == "ALLOWED_HOSTS":
            return ["localhost", "127.0.0.1"]
        elif field_name == "USE_TZ":
            return True
        elif field_name == "DJANGO_LOG_LEVEL":
            return "INFO"
        elif field_name == "SERVE_MEDIA_LOCALLY":
            return True
        elif field_name == "SMTP_HOST":
            return "smtp.gmail.com"
        elif field_name == "SMTP_PORT":
            return 587
        elif field_name == "SMTP_USE_TLS":
            return True
        elif field_name == "SMTP_AUTH_USERNAME":
            return fake.user_name()
        elif field_name == "SMTP_AUTH_PASSWORD":
            return fake.password(length=16, special_chars=True)
        elif field_name == "SMTP_FROM_ADDRESS":
            return fake.email()
        elif field_name == "ACCESS_TOKEN_LIFETIME_MINUTES":
            return timedelta(minutes=240)
        elif field_name == "REFRESH_TOKEN_LIFETIME_DAYS":
            return timedelta(days=3)
        elif field_name == "DEBUG_USER_EMAIL":
            return fake.email()
        elif field_name == "DEBUG_USER_USERNAME":
            return fake.user_name()
        elif field_name == "DEBUG_USER_PASSWORD":
            return fake.password(length=16, special_chars=True)
        elif field_name == "CACHE_USERNAME":
            return fake.user_name()
        elif field_name == "CACHE_PASSWORD":
            return fake.password(length=16, special_chars=True)
        elif field_name == "CACHE_HOST":
            return "localhost"
        elif field_name == "CACHE_PORT":
            return 6379

        # Fallback based on type hints
        if field_type is str:
            return fake.word()
        elif field_type is int:
            return fake.random_int(min=1, max=65535)
        elif field_type is bool:
            return fake.boolean()
        elif field_type is list:
            return []

        return None
