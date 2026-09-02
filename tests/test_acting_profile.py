import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from profiles.models import Profile
from profiles.views import get_acting_profile

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="SecurePass123!")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="SecurePass123!")


def make_request(user, query=""):
    request = RequestFactory().get(f"/?{query}")
    request.user = user
    return request


@pytest.mark.django_db
def test_returns_none_when_user_has_no_profiles(user):
    assert get_acting_profile(make_request(user)) is None


@pytest.mark.django_db
def test_returns_first_profile_without_as_param(user):
    Profile.objects.create(user=user, full_name="Older")
    newest = Profile.objects.create(user=user, full_name="Newer")

    assert get_acting_profile(make_request(user)) == newest


@pytest.mark.django_db
def test_as_param_selects_that_profile(user):
    first = Profile.objects.create(user=user, full_name="First")
    Profile.objects.create(user=user, full_name="Second")

    assert get_acting_profile(make_request(user, f"as={first.id}")) == first


@pytest.mark.django_db
def test_cannot_act_as_another_users_profile(user, other_user):
    mine = Profile.objects.create(user=user, full_name="Mine")
    theirs = Profile.objects.create(user=other_user, full_name="Theirs")

    assert get_acting_profile(make_request(user, f"as={theirs.id}")) == mine


@pytest.mark.django_db
def test_invalid_as_param_falls_back(user):
    mine = Profile.objects.create(user=user, full_name="Mine")

    assert get_acting_profile(make_request(user, "as=9999")) == mine
