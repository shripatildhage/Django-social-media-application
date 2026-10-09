"""Visibility / privacy rules shared by web views and the REST API."""
from django.db.models import Q

from friends.models import Follow, are_friends, friends_of
from .models import Post


def can_view_user_posts(viewer, owner):
    if viewer == owner or not owner.profile.is_private:
        return True
    return Follow.objects.filter(follower=viewer, following=owner).exists() or are_friends(viewer, owner)


def visible_posts(user):
    """All non-hidden posts the user is allowed to see."""
    friend_ids = list(friends_of(user).values_list("id", flat=True))
    followed_ids = list(Follow.objects.filter(follower=user).values_list("following_id", flat=True))
    q = (
        Q(author=user)
        | Q(author__profile__is_private=False)
        | Q(author_id__in=friend_ids)
        | Q(author_id__in=followed_ids)
    )
    return (
        Post.objects.filter(q, is_hidden=False)
        .select_related("author__profile")
        .prefetch_related("likes")
        .distinct()
    )


def following_feed(user):
    ids = set(Follow.objects.filter(follower=user).values_list("following_id", flat=True))
    ids |= set(friends_of(user).values_list("id", flat=True))
    ids.add(user.id)
    return visible_posts(user).filter(author_id__in=ids)
