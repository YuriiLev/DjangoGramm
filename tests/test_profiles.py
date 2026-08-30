import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from profiles.models import Follow, Profile

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="SecurePass123!")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="SecurePass123!")


@pytest.mark.django_db
def test_create_profile(user):
    profile = Profile.objects.create(user=user, full_name="Test Person")

    assert profile.full_name == "Test Person"
    assert profile.user == user
    assert profile.bio == ""


@pytest.mark.django_db
def test_user_can_own_multiple_profiles(user):
    Profile.objects.create(user=user, full_name="First")
    Profile.objects.create(user=user, full_name="Second")

    assert user.profiles.count() == 2


@pytest.mark.django_db
def test_deleting_user_deletes_profiles(user):
    Profile.objects.create(user=user, full_name="Test Person")

    user.delete()

    assert Profile.objects.count() == 0


@pytest.mark.django_db
def test_follow_creates_relationship(user, other_user):
    a = Profile.objects.create(user=user, full_name="A")
    b = Profile.objects.create(user=other_user, full_name="B")

    Follow.objects.create(follower=a, followed=b)

    assert a.following.count() == 1
    assert b.followers.count() == 1


@pytest.mark.django_db
def test_profile_cannot_follow_itself(user):
    a = Profile.objects.create(user=user, full_name="A")

    with pytest.raises(ValidationError):
        Follow.objects.create(follower=a, followed=a)


@pytest.mark.django_db
def test_duplicate_follow_is_rejected(user, other_user):
    a = Profile.objects.create(user=user, full_name="A")
    b = Profile.objects.create(user=other_user, full_name="B")

    Follow.objects.create(follower=a, followed=b)

    with pytest.raises((ValidationError, IntegrityError)):
        Follow.objects.create(follower=a, followed=b)
