from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from notifications.services import notify

from .models import FriendRequest, Follow, are_friends, friends_of


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("profile", username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if created:
        notify(recipient=target, actor=request.user, verb="started following you")
    else:
        follow.delete()
    return redirect("profile", username=username)


@login_required
@require_POST
def send_request(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "You cannot friend yourself.")
    elif are_friends(request.user, target):
        messages.info(request, "You are already friends.")
    else:
        reverse = FriendRequest.objects.filter(
            from_user=target, to_user=request.user, status=FriendRequest.PENDING
        ).first()
        if reverse:  # they already asked us - auto accept
            reverse.status = FriendRequest.ACCEPTED
            reverse.save()
            notify(recipient=target, actor=request.user, verb="accepted your friend request")
        else:
            fr, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=target)
            if not created and fr.status == FriendRequest.DECLINED:
                fr.status = FriendRequest.PENDING
                fr.save()
            notify(recipient=target, actor=request.user, verb="sent you a friend request")
            messages.success(request, "Friend request sent.")
    return redirect("profile", username=username)


@login_required
@require_POST
def respond_request(request, pk, action):
    fr = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status=FriendRequest.PENDING)
    if action == "accept":
        fr.status = FriendRequest.ACCEPTED
        notify(recipient=fr.from_user, actor=request.user, verb="accepted your friend request")
    elif action == "decline":
        fr.status = FriendRequest.DECLINED
    else:
        return redirect("friends")
    fr.save()
    return redirect("friends")


@login_required
def friends_list(request):
    pending = FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.PENDING).select_related("from_user__profile")
    followers = User.objects.filter(following_set__following=request.user).select_related("profile")
    following = User.objects.filter(follower_set__follower=request.user).select_related("profile")
    return render(
        request,
        "friends.html",
        {"pending": pending, "friends": friends_of(request.user), "followers": followers, "following": following},
    )
