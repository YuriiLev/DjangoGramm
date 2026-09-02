from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from profiles.models import Profile

from .forms import PostForm
from .models import Post, PostImage, Tag


@login_required
def profile_posts(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    posts = profile.posts.prefetch_related("images", "tags")
    return render(request, "posts/profile_posts.html", {"profile": profile, "posts": posts})


@login_required
def post_create(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)

    if request.method == "POST":
        form = PostForm(request.POST)
        tag_ids = request.POST.getlist("tags")
        images = request.FILES.getlist("images")

        if form.is_valid():
            post = form.save(commit=False)
            post.profile = profile
            post.save()

            post.tags.set(Tag.objects.filter(id__in=tag_ids))

            for image in images:
                PostImage.objects.create(post=post, image=image)

            return redirect("profile-posts", profile_id=profile.id)
    else:
        form = PostForm()

    return render(
        request,
        "posts/post_form.html",
        {
            "form": form,
            "profile": profile,
            "title": "Create Post",
            "tags": Tag.objects.all(),
        },
    )


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id, profile__user=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        tag_ids = request.POST.getlist("tags")
        images = request.FILES.getlist("images")

        if form.is_valid():
            post = form.save()

            post.tags.set(Tag.objects.filter(id__in=tag_ids))

            for image in images:
                PostImage.objects.create(post=post, image=image)

            return redirect("profile-posts", profile_id=post.profile.id)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "posts/post_form.html",
        {
            "form": form,
            "post": post,
            "profile": post.profile,
            "title": "Edit Post",
            "tags": Tag.objects.all(),
        },
    )


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, profile__user=request.user)
    profile_id = post.profile.id

    if request.method == "POST":
        post.delete()
        return redirect("profile-posts", profile_id=profile_id)

    return render(request, "posts/post_confirm_delete.html", {"post": post})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("profile", "profile__user").prefetch_related("images", "tags"),
        id=post_id,
    )
    return render(request, "posts/post_detail.html", {"post": post})


@login_required
def tag_list(request):
    tags = Tag.objects.annotate(post_count=Count("posts")).order_by("name")
    return render(request, "posts/tag_list.html", {"tags": tags})


@login_required
def tag_detail(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    posts = (
        tag.posts.select_related("profile")
        .prefetch_related("images", "tags")
        .order_by("-created_at")
    )
    return render(request, "posts/tag_detail.html", {"tag": tag, "posts": posts})
