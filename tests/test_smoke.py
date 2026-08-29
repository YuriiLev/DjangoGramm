import pytest


@pytest.mark.django_db
def test_database_connection():
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_settings_loaded():
    from django.conf import settings

    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"