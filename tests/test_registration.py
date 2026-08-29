import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_signup_page_loads(client):
    response = client.get(reverse("account_signup"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_creates_user(client):
    response = client.post(
        reverse("account_signup"),
        {
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        },
    )

    assert response.status_code == 302
    assert User.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
def test_signup_rejects_mismatched_passwords(client):
    client.post(
        reverse("account_signup"),
        {
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "DifferentPass456!",
        },
    )

    assert not User.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
def test_signup_rejects_duplicate_email(client):
    User.objects.create_user(email="taken@example.com", password="SecurePass123!")

    client.post(
        reverse("account_signup"),
        {
            "email": "taken@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        },
    )

    assert User.objects.filter(email="taken@example.com").count() == 1
