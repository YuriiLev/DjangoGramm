from config.images import AVATAR_THUMB, transform

CLOUDINARY_URL = "https://res.cloudinary.com/demo/image/upload/v1/posts/photo.jpg"


def test_transformation_is_inserted():
    result = transform(CLOUDINARY_URL, AVATAR_THUMB)

    assert f"/image/upload/{AVATAR_THUMB}/" in result
    assert result.endswith("v1/posts/photo.jpg")


def test_non_cloudinary_url_is_unchanged():
    local = "/media/posts/photo.jpg"

    assert transform(local, AVATAR_THUMB) == local


def test_empty_url_is_safe():
    assert transform("", AVATAR_THUMB) == ""
