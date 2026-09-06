from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from config.images import AVATAR_THUMB, transform

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} (@{self.user.email})"

    @property
    def avatar_thumb_url(self):
        return transform(self.avatar.url, AVATAR_THUMB) if self.avatar else ""


class Follow(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("followed")),
                name="no_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.follower.full_name} follows {self.followed.full_name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.follower_id == self.followed_id:
            raise ValidationError("A profile cannot follow itself.")
