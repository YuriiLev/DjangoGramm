import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_signup_sends_confirmation_email(client):
    client.post(
        reverse("account_signup"),
        {
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        },
    )

    assert len(mail.outbox) == 1
    assert "newuser@example.com" in mail.outbox[0].to


@pytest.mark.django_db
def test_email_starts_unverified(client):
    client.post(
        reverse("account_signup"),
        {
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        },
    )

    email_address = EmailAddress.objects.get(email="newuser@example.com")
    assert not email_address.verified


@pytest.mark.django_db
def test_unverified_user_cannot_log_in(client):
    user = User.objects.create_user(email="user@example.com", password="SecurePass123!")
    EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)

    response = client.post(
        reverse("account_login"),
        {"login": "user@example.com", "password": "SecurePass123!"},
    )

    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_verified_user_can_log_in(client):
    user = User.objects.create_user(email="user@example.com", password="SecurePass123!")
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

    response = client.post(
        reverse("account_login"),
        {"login": "user@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated
