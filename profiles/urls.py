from django.urls import path

from .views import (
    ProfileCreateView,
    ProfileDeleteView,
    ProfileDetailView,
    ProfileListView,
    ProfileUpdateView,
    toggle_follow,
)

urlpatterns = [
    path("", ProfileListView.as_view(), name="profile-list"),
    path("new/", ProfileCreateView.as_view(), name="profile-create"),
    path("<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("<int:pk>/edit/", ProfileUpdateView.as_view(), name="profile-update"),
    path("<int:pk>/delete/", ProfileDeleteView.as_view(), name="profile-delete"),
    path("<int:profile_id>/follow/<int:follower_id>/", toggle_follow, name="toggle-follow"),
]
