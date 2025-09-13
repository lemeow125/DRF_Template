import pytest
from rest_framework.test import APIClient
from users import generate_test_users

from core.settings import config

client = APIClient()


@pytest.mark.django_db(transaction=True)
def test_user_login():
    """
    Test login with multiple user accounts
    """

    USERS = generate_test_users(active=True)

    for USER in USERS:
        login_response = client.post(
            "/api/v1/accounts/jwt/create/",
            {"username": USER.username, "password": config.DEBUG_USER_PASSWORD},
            format="json",
        ).json()

        # Check if login contains JWT data
        assert {"access", "refresh"}.issubset(login_response)

        access_token = login_response["access"]

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        # GET user info
        user_response = client.get("/api/v1/accounts/users/me/")

        assert user_response.json()  # Ensure there's response data
