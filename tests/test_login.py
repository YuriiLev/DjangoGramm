import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def user(db):
    user = User.objects.create_user(email="user@example.com", password="SecurePass123!")
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse("account_login"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_login_with_correct_credentials(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "user@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_with_wrong_password(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "user@example.com", "password": "WrongPassword!"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_logout(client, user):
    client.force_login(user)

    response = client.post(reverse("account_logout"))

    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated
