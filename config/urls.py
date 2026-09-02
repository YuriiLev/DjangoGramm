from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("profiles.urls")),
    path("posts/", include("posts.urls")),
    path("", include("accounts.urls")),
]
