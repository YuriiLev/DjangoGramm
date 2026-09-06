from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from posts.views import feed

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("profiles.urls")),
    path("posts/", include("posts.urls")),
    path("", feed, name="home"),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()