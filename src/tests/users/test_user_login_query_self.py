import pytest
from core.settings import config
import users


from rest_framework.test import APIClient

client = APIClient()


@pytest.mark.django_db(transaction=True)
def test_user_login():
    """
    Test login
    """

    data = users.get_users_json()

    # Generate test users
    users.generate_test_users()

    for user in data["users"]:
        login_response = client.post(
            "/api/v1/accounts/jwt/create/",
            {"username": user["username"], "password": config.DEBUG_USER_PASSWORD},
            format="json",
        ).json()

        # Check if login contains JWT data
        assert {"access", "refresh"}.issubset(login_response)

        access_token = login_response["access"]

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        # GET user info
        user_response = client.get("/api/v1/accounts/users/me/")

        assert user_response.json()  # Ensure there's response data
