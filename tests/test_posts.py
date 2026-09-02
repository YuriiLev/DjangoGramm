import base64
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from posts.models import Like, Post, PostImage, Tag
from profiles.models import Profile

User = get_user_model()


def make_image():
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    return SimpleUploadedFile("post.png", png, content_type="image/png")


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="SecurePass123!")


@pytest.fixture
def profile(user):
    return Profile.objects.create(user=user, full_name="Test Person")


@pytest.mark.django_db
def test_create_post(profile):
    post = Post.objects.create(profile=profile, description="Hello")

    assert post.profile == profile
    assert post.description == "Hello"


@pytest.mark.django_db
def test_post_description_can_be_empty(profile):
    post = Post.objects.create(profile=profile)

    assert post.description == ""


@pytest.mark.django_db
def test_posts_ordered_newest_first(profile):
    older = Post.objects.create(profile=profile, description="Older")
    newer = Post.objects.create(profile=profile, description="Newer")

    Post.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))

    assert Post.objects.first() == newer


@pytest.mark.django_db
def test_deleting_profile_deletes_posts(profile):
    Post.objects.create(profile=profile, description="Hello")

    profile.delete()

    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_post_can_have_multiple_images(profile):
    post = Post.objects.create(profile=profile)

    PostImage.objects.create(post=post, image=make_image())
    PostImage.objects.create(post=post, image=make_image())

    assert post.images.count() == 2


@pytest.mark.django_db
def test_images_ordered_oldest_first(profile):
    post = Post.objects.create(profile=profile)
    first = PostImage.objects.create(post=post, image=make_image())

    assert post.images.first() == first


@pytest.mark.django_db
def test_deleting_post_deletes_images(profile):
    post = Post.objects.create(profile=profile)
    PostImage.objects.create(post=post, image=make_image())

    post.delete()

    assert PostImage.objects.count() == 0


@pytest.mark.django_db
def test_tag_is_reusable_across_posts(profile):
    post_a = Post.objects.create(profile=profile, description="A")
    post_b = Post.objects.create(profile=profile, description="B")
    tag = Tag.objects.create(name="travel")

    tag.posts.add(post_a, post_b)

    assert tag.posts.count() == 2
    assert post_a.tags.count() == 1


@pytest.mark.django_db
def test_tag_name_is_unique(profile):
    Tag.objects.create(name="travel")

    with pytest.raises(IntegrityError):
        Tag.objects.create(name="travel")


@pytest.mark.django_db
def test_post_can_have_no_tags(profile):
    post = Post.objects.create(profile=profile)

    assert post.tags.count() == 0


@pytest.mark.django_db
def test_post_create_requires_login(client, profile):
    response = client.get(reverse("post-create", args=[profile.id]))

    assert response.status_code == 302


@pytest.mark.django_db
def test_create_post_with_images_and_tags(client, user, profile):
    client.force_login(user)
    tag = Tag.objects.create(name="travel")

    client.post(
        reverse("post-create", args=[profile.id]),
        {
            "description": "Hello",
            "tags": [tag.id],
            "images": [make_image(), make_image()],
        },
    )

    post = Post.objects.get(description="Hello")
    assert post.profile == profile
    assert post.images.count() == 2
    assert post.tags.count() == 1


@pytest.mark.django_db
def test_create_post_ignores_unknown_tag_id(client, user, profile):
    client.force_login(user)

    client.post(
        reverse("post-create", args=[profile.id]),
        {"description": "Hello", "tags": [9999]},
    )

    post = Post.objects.get(description="Hello")
    assert post.tags.count() == 0


@pytest.mark.django_db
def test_cannot_create_post_on_someone_elses_profile(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    client.force_login(other)

    response = client.post(reverse("post-create", args=[profile.id]), {"description": "Hacked"})

    assert response.status_code == 404
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_owner_can_update_post(client, user, profile):
    client.force_login(user)
    post = Post.objects.create(profile=profile, description="Original")

    client.post(reverse("post-update", args=[post.id]), {"description": "Changed"})

    post.refresh_from_db()
    assert post.description == "Changed"


@pytest.mark.django_db
def test_update_replaces_tags(client, user, profile):
    client.force_login(user)
    old_tag = Tag.objects.create(name="old")
    new_tag = Tag.objects.create(name="new")
    post = Post.objects.create(profile=profile, description="Hello")
    old_tag.posts.add(post)

    client.post(
        reverse("post-update", args=[post.id]),
        {"description": "Hello", "tags": [new_tag.id]},
    )

    assert list(post.tags.all()) == [new_tag]


@pytest.mark.django_db
def test_non_owner_cannot_update_post(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    post = Post.objects.create(profile=profile, description="Original")
    client.force_login(other)

    response = client.post(reverse("post-update", args=[post.id]), {"description": "Hacked"})

    assert response.status_code == 404
    post.refresh_from_db()
    assert post.description == "Original"


@pytest.mark.django_db
def test_owner_can_delete_post(client, user, profile):
    client.force_login(user)
    post = Post.objects.create(profile=profile, description="Hello")

    client.post(reverse("post-delete", args=[post.id]))

    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_non_owner_cannot_delete_post(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    post = Post.objects.create(profile=profile, description="Hello")
    client.force_login(other)

    response = client.post(reverse("post-delete", args=[post.id]))

    assert response.status_code == 404
    assert Post.objects.count() == 1


@pytest.mark.django_db
def test_profile_posts_shows_only_own_profile(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    client.force_login(other)

    response = client.get(reverse("profile-posts", args=[profile.id]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_post_detail_requires_login(client, profile):
    post = Post.objects.create(profile=profile, description="Hello")

    response = client.get(reverse("post-detail", args=[post.id]))

    assert response.status_code == 302


@pytest.mark.django_db
def test_any_user_can_view_post_detail(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    post = Post.objects.create(profile=profile, description="Hello")
    client.force_login(other)

    response = client.get(reverse("post-detail", args=[post.id]))

    assert response.status_code == 200
    assert "Hello" in response.content.decode()


@pytest.mark.django_db
def test_edit_buttons_hidden_from_non_owner(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    post = Post.objects.create(profile=profile, description="Hello")
    client.force_login(other)

    response = client.get(reverse("post-detail", args=[post.id]))

    assert reverse("post-update", args=[post.id]) not in response.content.decode()


@pytest.mark.django_db
def test_create_like(profile):
    post = Post.objects.create(profile=profile, description="Hello")

    like = Like.objects.create(profile=profile, post=post)

    assert like.profile == profile
    assert post.likes.count() == 1


@pytest.mark.django_db
def test_duplicate_like_is_rejected(profile):
    post = Post.objects.create(profile=profile, description="Hello")
    Like.objects.create(profile=profile, post=post)

    with pytest.raises(IntegrityError):
        Like.objects.create(profile=profile, post=post)


@pytest.mark.django_db
def test_different_profiles_can_like_same_post(user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    other_profile = Profile.objects.create(user=other, full_name="Other Person")
    post = Post.objects.create(profile=profile, description="Hello")

    Like.objects.create(profile=profile, post=post)
    Like.objects.create(profile=other_profile, post=post)

    assert post.likes.count() == 2


@pytest.mark.django_db
def test_deleting_post_deletes_likes(profile):
    post = Post.objects.create(profile=profile, description="Hello")
    Like.objects.create(profile=profile, post=post)

    post.delete()

    assert Like.objects.count() == 0


@pytest.mark.django_db
def test_deleting_profile_deletes_likes(user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    other_profile = Profile.objects.create(user=other, full_name="Other Person")
    post = Post.objects.create(profile=other_profile, description="Hello")
    Like.objects.create(profile=profile, post=post)

    profile.delete()

    assert Like.objects.count() == 0
