import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="user@example.com", password="testpass123")

    assert user.email == "user@example.com"
    assert user.check_password("testpass123")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(email="admin@example.com", password="testpass123")

    assert user.is_staff
    assert user.is_superuser


@pytest.mark.django_db
def test_email_is_normalized():
    user = User.objects.create_user(email="User@EXAMPLE.COM", password="testpass123")

    assert user.email == "User@example.com"


@pytest.mark.django_db
def test_user_without_email_raises_error():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="testpass123")


@pytest.mark.django_db
def test_password_is_hashed():
    user = User.objects.create_user(email="user@example.com", password="testpass123")

    assert user.password != "testpass123"
