from django.urls import path

from . import views

urlpatterns = [
    path("profile/<int:profile_id>/", views.profile_posts, name="profile-posts"),
    path("profile/<int:profile_id>/new/", views.post_create, name="post-create"),
    path("<int:post_id>/", views.post_detail, name="post-detail"),
    path("<int:post_id>/edit/", views.post_update, name="post-update"),
    path("<int:post_id>/delete/", views.post_delete, name="post-delete"),
]
