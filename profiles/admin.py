from django.contrib import admin

from .models import Follow, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["full_name", "user__email"]
    raw_id_fields = ["user"]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "followed", "created_at"]
    raw_id_fields = ["follower", "followed"]
