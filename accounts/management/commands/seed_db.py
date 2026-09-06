import random

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from posts.models import Like, Post, PostImage, Tag
from profiles.models import Follow, Profile

User = get_user_model()

TAG_NAMES = [
    "travel",
    "food",
    "nature",
    "city",
    "portrait",
    "street",
    "sunset",
    "coffee",
    "architecture",
    "mountains",
    "sea",
    "winter",
    "summer",
    "blackandwhite",
    "minimal",
]


class Command(BaseCommand):
    help = "Fill the database with fake data for local development and demos."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=15)
        parser.add_argument("--posts", type=int, default=200)
        parser.add_argument("--flush", action="store_true", help="Delete seeded data first")

    @transaction.atomic
    def handle(self, *args, **options):
        from faker import Faker

        fake = Faker()
        random.seed(42)
        Faker.seed(42)

        if options["flush"]:
            User.objects.filter(is_superuser=False).delete()
            Tag.objects.all().delete()
            self.stdout.write("Deleted existing seed data.")

        users = []
        for _ in range(options["users"]):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password="demo1234",
            )
            EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
            users.append(user)

        profiles = []
        for user in users:
            for _ in range(random.randint(1, 2)):
                profiles.append(
                    Profile(
                        user=user,
                        full_name=fake.name(),
                        bio=fake.sentence(nb_words=12),
                    )
                )
        Profile.objects.bulk_create(profiles)
        profiles = list(Profile.objects.all())

        tags = Tag.objects.bulk_create(
            [Tag(name=name) for name in TAG_NAMES], ignore_conflicts=True
        )
        tags = list(Tag.objects.all())

        posts = [
            Post(profile=random.choice(profiles), description=fake.sentence(nb_words=10))
            for _ in range(options["posts"])
        ]
        Post.objects.bulk_create(posts)
        posts = list(Post.objects.all())

        images = []
        for post in posts:
            for i in range(random.randint(1, 3)):
                images.append(PostImage(post=post, image=f"posts/seed_{post.id}_{i}.jpg"))
        PostImage.objects.bulk_create(images)

        for tag in tags:
            tag.posts.add(*random.sample(posts, k=min(len(posts), random.randint(5, 40))))

        likes = [
            Like(profile=random.choice(profiles), post=random.choice(posts))
            for _ in range(options["posts"] * 4)
        ]
        Like.objects.bulk_create(likes, ignore_conflicts=True)

        follows = []
        for profile in profiles:
            targets = random.sample(profiles, k=min(len(profiles), random.randint(2, 8)))
            for target in targets:
                if target.id != profile.id:
                    follows.append(Follow(follower=profile, followed=target))
        Follow.objects.bulk_create(follows, ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(users)} users, {len(profiles)} profiles, "
                f"{len(posts)} posts, {Like.objects.count()} likes, "
                f"{Follow.objects.count()} follows."
            )
        )
