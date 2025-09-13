import pytest
import users
from django.contrib.auth.tokens import default_token_generator
from django.test.client import RequestFactory
from djoser.utils import encode_uid

from accounts.views import CustomUserViewSet

factory = RequestFactory()


@pytest.mark.django_db(transaction=True)
def test_user_activation():
    """
    Test activation
    """
    # Generate test user
    USER = users.generate_random_user(active=False)

    uid = encode_uid(USER.pk)
    token = default_token_generator.make_token(USER)

    view = CustomUserViewSet.as_view(actions={"post": "activation"})

    request = factory.post(
        "/accounts/users/activation/", data={"uid": uid, "token": token}
    )

    response = view(request)
    response.render()

    assert response.status_code == 204
