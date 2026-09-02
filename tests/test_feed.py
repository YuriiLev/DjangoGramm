import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Like, Post
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
def test_feed_shows_own_posts(client, user, mine):
    Post.objects.create(profile=mine, description="My post")
    client.force_login(user)

    response = client.get(reverse("feed"))

    assert "My post" in response.content.decode()


@pytest.mark.django_db
def test_feed_shows_followed_posts(client, user, mine, theirs):
    Follow.objects.create(follower=mine, followed=theirs)
    Post.objects.create(profile=theirs, description="Their post")
    client.force_login(user)

    response = client.get(reverse("feed"))

    assert "Their post" in response.content.decode()


@pytest.mark.django_db
def test_feed_hides_unfollowed_posts(client, user, mine, theirs):
    Post.objects.create(profile=theirs, description="Their post")
    client.force_login(user)

    response = client.get(reverse("feed"))

    assert "Their post" not in response.content.decode()


@pytest.mark.django_db
def test_feed_annotates_user_liked(client, user, mine):
    post = Post.objects.create(profile=mine, description="My post")
    Like.objects.create(profile=mine, post=post)
    client.force_login(user)

    response = client.get(reverse("feed"))

    assert response.context["posts"][0].user_liked is True


@pytest.mark.django_db
def test_feed_annotates_likes_count(client, user, mine, theirs):
    post = Post.objects.create(profile=mine, description="My post")
    Like.objects.create(profile=mine, post=post)
    Like.objects.create(profile=theirs, post=post)
    client.force_login(user)

    response = client.get(reverse("feed"))

    assert response.context["posts"][0].likes_count == 2


@pytest.mark.django_db
def test_feed_empty_without_profile(client, user):
    response = client.get(reverse("feed"))

    client.force_login(user)
    response = client.get(reverse("feed"))

    assert list(response.context["posts"]) == []


@pytest.mark.django_db
def test_feed_requires_login(client):
    response = client.get(reverse("feed"))

    assert response.status_code == 302
