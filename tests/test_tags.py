import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Tag
from profiles.models import Profile

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="SecurePass123!")


@pytest.fixture
def profile(user):
    return Profile.objects.create(user=user, full_name="Test Person")


@pytest.mark.django_db
def test_tag_list_requires_login(client):
    response = client.get(reverse("tag-list"))

    assert response.status_code == 302


@pytest.mark.django_db
def test_tag_list_shows_post_count(client, user, profile):
    tag = Tag.objects.create(name="travel")
    tag.posts.add(
        Post.objects.create(profile=profile, description="A"),
        Post.objects.create(profile=profile, description="B"),
    )
    Tag.objects.create(name="empty")
    client.force_login(user)

    response = client.get(reverse("tag-list"))

    counts = {t.name: t.post_count for t in response.context["tags"]}
    assert counts == {"empty": 0, "travel": 2}


@pytest.mark.django_db
def test_tag_detail_shows_only_tagged_posts(client, user, profile):
    tag = Tag.objects.create(name="travel")
    tagged = Post.objects.create(profile=profile, description="Tagged post")
    Post.objects.create(profile=profile, description="Untagged post")
    tag.posts.add(tagged)
    client.force_login(user)

    response = client.get(reverse("tag-detail", args=[tag.id]))
    content = response.content.decode()

    assert "Tagged post" in content
    assert "Untagged post" not in content


@pytest.mark.django_db
def test_tag_detail_shows_posts_from_any_profile(client, user, profile):
    other = User.objects.create_user(email="other@example.com", password="SecurePass123!")
    other_profile = Profile.objects.create(user=other, full_name="Other")
    tag = Tag.objects.create(name="travel")
    tag.posts.add(Post.objects.create(profile=other_profile, description="Their post"))
    client.force_login(user)

    response = client.get(reverse("tag-detail", args=[tag.id]))

    assert "Their post" in response.content.decode()


@pytest.mark.django_db
def test_unknown_tag_returns_404(client, user):
    client.force_login(user)

    response = client.get(reverse("tag-detail", args=[9999]))

    assert response.status_code == 404
