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
def test_home_page_loads(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_home_shows_login_links_when_anonymous(client):
    response = client.get(reverse("home"))

    assert reverse("account_login") in response.content.decode()
    assert reverse("account_signup") in response.content.decode()


@pytest.mark.django_db
def test_home_shows_email_when_authenticated(client, user):
    client.force_login(user)

    response = client.get(reverse("home"))

    assert "user@example.com" in response.content.decode()
