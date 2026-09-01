import base64
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.utils import timezone

from posts.models import Post, PostImage, Tag
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
