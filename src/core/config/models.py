"""
Common model schemas
"""

import re
from datetime import timedelta
from typing import Literal

from pydantic import (BaseModel, EmailStr, Field, StrictStr, field_validator,
                      model_validator)
from pydantic_extra_types.timezone_name import TimeZoneName


class Config(BaseModel):
    """
    Pydantic Configuration model for Django
    """

    SECRET_KEY: StrictStr = Field(
        min_length=32,
        description="Secret key for the API",
        json_schema_extra={"required": True},
    )
    DEBUG: bool = Field(default=False, description="API debug mode")
    TIMEZONE: TimeZoneName = "UTC"
    CORS_ORIGINS: list[StrictStr] = Field(
        description="Allowed CORS origins for API.", default_factory=list
    )
    ALLOWED_HOSTS: list[StrictStr] = Field(
        description="Allowed hosts by the API.", default_factory=list
    )
    USE_TZ: bool = Field(
        json_schema_extra={"required": True},
        default=True,
        description="Whether the backend API defaults to using timezone-aware datetimes.",
    )
    DJANGO_LOG_LEVEL: Literal["INFO", "DEBUG"] = "INFO"
    SERVE_MEDIA_LOCALLY: bool = Field(
        default=False,
        description="Whether to serve media files locally as oppossed to using a cloud storage solution.",
    )
    SMTP_HOST: StrictStr = Field(
        json_schema_extra={"required": True}, description="SMTP server address"
    )
    SMTP_PORT: int = Field(default=587, description="SMTP server port (default: 587)")
    SMTP_USE_TLS: bool = Field(
        default=True, description="Whether to use TLS for SMTP connections"
    )
    SMTP_AUTH_USERNAME: StrictStr = Field(
        json_schema_extra={"required": True}, description="SMTP authentication username"
    )
    SMTP_AUTH_PASSWORD: StrictStr = Field(
        json_schema_extra={"required": True}, description="SMTP authentication password"
    )
    SMTP_FROM_ADDRESS: EmailStr = Field(
        json_schema_extra={"required": True}, description="SMTP from email address"
    )
    ACCESS_TOKEN_LIFETIME_MINUTES: timedelta = Field(
        default=timedelta(minutes=240),
        description="Access token lifetime in minutes",
    )
    REFRESH_TOKEN_LIFETIME_DAYS: timedelta = Field(
        default=timedelta(days=3), description="Refresh token lifetime in days"
    )
    DEBUG_USER_PASSWORD: StrictStr = Field(
        json_schema_extra={"required": True},
        description="Password for test users created during development",
    )
    CACHE_USERNAME: StrictStr = Field(
        json_schema_extra={"required": True},
        description="Cache server authentication username",
    )
    CACHE_PASSWORD: StrictStr = Field(
        json_schema_extra={"required": True},
        description="Cache server authentication password",
    )
    CACHE_HOST: StrictStr = Field(
        json_schema_extra={"required": True}, description="Server host used for caching"
    )
    CACHE_PORT: int = Field(
        json_schema_extra={"required": True}, description="Server port used for caching"
    )

    @field_validator("CORS_ORIGINS", "ALLOWED_HOSTS", mode="before")
    def parse_list(cls, v):
        """
        Splits a comma-separated string into a list.
        """
        if isinstance(v, str):
            return v.split(",")
        return v

    @field_validator("ACCESS_TOKEN_LIFETIME_MINUTES", mode="before")
    def parse_timedelta_minutes(cls, v):
        """
        Parse integer values into timedelta objects.
        """
        if isinstance(v, str):
            return timedelta(minutes=int(v))
        return v

    @field_validator("REFRESH_TOKEN_LIFETIME_DAYS", mode="before")
    def parse_timedelta_days(cls, v):
        """
        Parse integer values into timedelta objects.
        """
        if isinstance(v, str):
            return timedelta(days=int(v))
        return v

    @model_validator(mode="after")
    def derive_token_lifetimes(cls, v):
        """
        Sets the appropriate log level based on the DEBUG setting.
        """
        if v.DEBUG:
            v.DJANGO_LOG_LEVEL = "DEBUG"
        else:
            v.DJANGO_LOG_LEVEL = "INFO"
        return v

    @model_validator(mode="after")
    def derive_allowed_hosts(cls, v):
        """
        Extracts additional hostnames from CORS_ORIGINS to append to ALLOWED_HOSTS.
        """

        cors_origins = v.CORS_ORIGINS
        allowed_hosts = set(v.ALLOWED_HOSTS or [])

        for origin in cors_origins:
            match = re.match(r"https?://([^/]+)", origin)
            if match and match.group(1):  # Ensure match.group(1) is not empty
                allowed_hosts.add(match.group(1))

        v.ALLOWED_HOSTS = list(allowed_hosts)
        return v

    @model_validator(mode="after")
    def derive_log_level(cls, v):
        """
        Sets the appropriate log level based on the DEBUG setting.
        """
        if v.DEBUG:
            v.DJANGO_LOG_LEVEL = "DEBUG"
        else:
            v.DJANGO_LOG_LEVEL = "INFO"
        return v
