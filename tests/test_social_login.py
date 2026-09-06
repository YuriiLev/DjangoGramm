import pytest
from allauth.socialaccount import providers
from django.urls import reverse


def test_github_provider_is_registered():
    assert "github" in [p.id for p in providers.registry.get_class_list()]


@pytest.mark.django_db
def test_github_button_on_login_page(client):
    response = client.get(reverse("account_login"))

    assert "Continue with GitHub" in response.content.decode()


@pytest.mark.django_db
def test_github_button_on_signup_page(client):
    response = client.get(reverse("account_signup"))

    assert "Continue with GitHub" in response.content.decode()


@pytest.mark.django_db
def test_github_login_url_resolves(client):
    response = client.get(reverse("github_login"))

    assert response.status_code in (200, 302)


def test_google_provider_is_registered():
    assert "google" in [p.id for p in providers.registry.get_class_list()]


@pytest.mark.django_db
def test_google_button_on_login_page(client):
    response = client.get(reverse("account_login"))

    assert "Continue with Google" in response.content.decode()


@pytest.mark.django_db
def test_google_button_on_signup_page(client):
    response = client.get(reverse("account_signup"))

    assert "Continue with Google" in response.content.decode()


@pytest.mark.django_db
def test_google_login_url_resolves(client):
    response = client.get(reverse("google_login"))

    assert response.status_code in (200, 302)
