import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from profiles.models import Follow, Profile

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="SecurePass123!")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="SecurePass123!")


@pytest.fixture
def mine(user):
    return Profile.objects.create(user=user, full_name="Mine")


@pytest.fixture
def theirs(other_user):
    return Profile.objects.create(user=other_user, full_name="Theirs")


@pytest.mark.django_db
def test_toggle_follow_creates_follow(client, user, mine, theirs):
    client.force_login(user)

    client.get(reverse("toggle-follow", args=[theirs.id, mine.id]))

    assert theirs.followers.count() == 1
    assert mine.following.count() == 1


@pytest.mark.django_db
def test_toggle_follow_twice_unfollows(client, user, mine, theirs):
    client.force_login(user)

    client.get(reverse("toggle-follow", args=[theirs.id, mine.id]))
    client.get(reverse("toggle-follow", args=[theirs.id, mine.id]))

    assert theirs.followers.count() == 0


@pytest.mark.django_db
def test_cannot_follow_as_someone_elses_profile(client, other_user, mine, theirs):
    client.force_login(other_user)

    response = client.get(reverse("toggle-follow", args=[theirs.id, mine.id]))

    assert response.status_code == 404
    assert theirs.followers.count() == 0


@pytest.mark.django_db
def test_self_follow_is_ignored(client, user, mine):
    client.force_login(user)

    client.get(reverse("toggle-follow", args=[mine.id, mine.id]))

    assert Follow.objects.count() == 0


@pytest.mark.django_db
def test_ajax_returns_json(client, user, mine, theirs):
    client.force_login(user)

    response = client.get(
        reverse("toggle-follow", args=[theirs.id, mine.id]),
        headers={"x-requested-with": "XMLHttpRequest"},
    )

    assert response.json() == {"following": True, "count": 1}


@pytest.mark.django_db
def test_toggle_follow_requires_login(client, mine, theirs):
    response = client.get(reverse("toggle-follow", args=[theirs.id, mine.id]))

    assert response.status_code == 302
    assert Follow.objects.count() == 0
