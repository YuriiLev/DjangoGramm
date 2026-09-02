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
def test_root_redirects_anonymous_to_login(client):
    response = client.get(reverse("home"))

    assert response.status_code == 302
    assert reverse("account_login") in response.url


@pytest.mark.django_db
def test_root_shows_feed_when_logged_in(client, user):
    client.force_login(user)

    response = client.get(reverse("home"))

    assert response.status_code == 200
