UPLOAD_MARKER = "/image/upload/"


def transform(url, transformation):
    """Insert a Cloudinary transformation into a delivery URL.

    Returns the URL unchanged when it isn't a Cloudinary one, so local
    file storage and the test suite keep working.
    """
    if not url or UPLOAD_MARKER not in url:
        return url
    return url.replace(UPLOAD_MARKER, f"{UPLOAD_MARKER}{transformation}/", 1)


AVATAR_THUMB = "c_fill,f_auto,g_face,h_160,q_auto,w_160"
POST_COVER = "c_fill,f_auto,h_440,q_auto,w_600"
POST_FULL = "c_limit,f_auto,q_auto,w_1200"
