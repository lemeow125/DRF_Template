"""
Common service functions and classes imported elsewhere.

For use in the immediate parent app/directory.
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic.fields import FieldInfo

from .models import Config as ConfigModel


class Config:
    """
    Core application config.
    """

    def __init__(self, prefix: Optional[str] = "backend") -> None:
        """
        Initialize the Config class.

        Args:
            prefix (str, optional): Prefix for environment variables. Defaults to "backend".

        """
        load_dotenv(find_dotenv())

        self.prefix = prefix.lower()

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
