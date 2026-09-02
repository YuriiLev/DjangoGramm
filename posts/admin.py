from django.contrib import admin

from .models import Post, PostImage, Tag


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["__str__", "profile", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["description", "profile__full_name"]
    raw_id_fields = ["profile"]
    inlines = [PostImageInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    filter_horizontal = ["posts"]
