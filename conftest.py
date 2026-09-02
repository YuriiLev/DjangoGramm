import pytest


@pytest.fixture(autouse=True)
def use_local_file_storage(settings, tmp_path):
    """Keep tests off Cloudinary — every run would otherwise upload real files."""
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    settings.MEDIA_ROOT = tmp_path
