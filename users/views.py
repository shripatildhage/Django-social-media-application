from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from friends.models import Follow
from posts.models import Post
from posts.services import can_view_user_posts

from .forms import ProfileForm, RegisterForm, UserUpdateForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile_detail(request, username):
    profile_user = get_object_or_404(User.objects.select_related("profile"), username=username)
    allowed = can_view_user_posts(request.user, profile_user)
    posts = (
        Post.objects.filter(author=profile_user, is_hidden=False).select_related("author__profile")
        if allowed
        else Post.objects.none()
    )
    context = {
        "profile_user": profile_user,
        "posts": posts,
        "can_view": allowed,
        "is_following": Follow.objects.filter(follower=request.user, following=profile_user).exists(),
        "followers_count": profile_user.follower_set.count(),
        "following_count": profile_user.following_set.count(),
        "posts_count": Post.objects.filter(author=profile_user, is_hidden=False).count(),
    }
    return render(request, "profile.html", context)


@login_required
def profile_edit(request):
    u_form = UserUpdateForm(request.POST or None, instance=request.user)
    p_form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == "POST" and u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile", username=request.user.username)
    return render(request, "profile_edit.html", {"u_form": u_form, "p_form": p_form})
