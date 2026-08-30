import base64

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.urls import reverse

from profiles.forms import ProfileForm
from profiles.models import Follow, Profile

User = get_user_model()


def make_image():
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    return SimpleUploadedFile("avatar.png", png, content_type="image/png")


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
def test_profiles_ordered_newest_first(user):
    Profile.objects.create(user=user, full_name="Older")
    newer = Profile.objects.create(user=user, full_name="Newer")

    assert Profile.objects.first() == newer


@pytest.mark.django_db
def test_deleting_user_deletes_profiles(user):
    Profile.objects.create(user=user, full_name="Test Person")

    user.delete()

    assert Profile.objects.count() == 0


@pytest.mark.django_db
def test_profile_str(user):
    profile = Profile.objects.create(user=user, full_name="Test Person")

    assert str(profile) == "Test Person (@user@example.com)"


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


@pytest.mark.django_db
def test_profile_form_accepts_avatar(user):
    form = ProfileForm(
        data={"full_name": "Test Person", "bio": ""},
        files={"avatar": make_image()},
    )

    assert form.is_valid()


@pytest.mark.django_db
def test_profile_form_valid_without_avatar(user):
    form = ProfileForm(data={"full_name": "Test Person", "bio": ""})

    assert form.is_valid()


@pytest.mark.django_db
def test_profile_form_requires_full_name(user):
    form = ProfileForm(data={"full_name": "", "bio": ""})

    assert not form.is_valid()
    assert "full_name" in form.errors


@pytest.mark.django_db
def test_avatar_saves_to_storage(user):
    form = ProfileForm(
        data={"full_name": "Test Person", "bio": ""},
        files={"avatar": make_image()},
    )
    assert form.is_valid()

    profile = form.save(commit=False)
    profile.user = user
    profile.save()

    assert profile.avatar.name.endswith(".png")


@pytest.mark.django_db
def test_create_view_requires_login(client):
    response = client.get(reverse("profile-create"))

    assert response.status_code == 302


@pytest.mark.django_db
def test_create_view_sets_owner_from_request(client, user):
    client.force_login(user)

    client.post(reverse("profile-create"), {"full_name": "Test Person", "bio": ""})

    profile = Profile.objects.get(full_name="Test Person")
    assert profile.user == user


@pytest.mark.django_db
def test_owner_can_edit_profile(client, user):
    client.force_login(user)
    profile = Profile.objects.create(user=user, full_name="Original")

    client.post(reverse("profile-update", args=[profile.pk]), {"full_name": "Changed", "bio": ""})

    profile.refresh_from_db()
    assert profile.full_name == "Changed"


@pytest.mark.django_db
def test_non_owner_cannot_edit_profile(client, user, other_user):
    profile = Profile.objects.create(user=user, full_name="Original")
    client.force_login(other_user)

    response = client.post(
        reverse("profile-update", args=[profile.pk]), {"full_name": "Hacked", "bio": ""}
    )

    assert response.status_code == 404
    profile.refresh_from_db()
    assert profile.full_name == "Original"


@pytest.mark.django_db
def test_non_owner_cannot_delete_profile(client, user, other_user):
    profile = Profile.objects.create(user=user, full_name="Original")
    client.force_login(other_user)

    response = client.post(reverse("profile-delete", args=[profile.pk]))

    assert response.status_code == 404
    assert Profile.objects.filter(pk=profile.pk).exists()


@pytest.mark.django_db
def test_any_user_can_view_profile(client, user, other_user):
    profile = Profile.objects.create(user=user, full_name="Test Person")
    client.force_login(other_user)

    response = client.get(reverse("profile-detail", args=[profile.pk]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_list_shows_only_own_profiles(client, user, other_user):
    Profile.objects.create(user=user, full_name="Mine")
    Profile.objects.create(user=other_user, full_name="Theirs")
    client.force_login(user)

    response = client.get(reverse("profile-list"))
    content = response.content.decode()

    assert "Mine" in content
    assert "Theirs" not in content
