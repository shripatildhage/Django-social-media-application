from django.conf import settings
from django.db import models
from django.db.models import Q


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follower_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(check=~Q(follower=models.F("following")), name="no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class FriendRequest(models.Model):
    PENDING, ACCEPTED, DECLINED = "pending", "accepted", "declined"
    STATUS_CHOICES = [(PENDING, "Pending"), (ACCEPTED, "Accepted"), (DECLINED, "Declined")]

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="unique_friend_request"),
            models.CheckConstraint(check=~Q(from_user=models.F("to_user")), name="no_self_request"),
        ]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"


def are_friends(a, b):
    return FriendRequest.objects.filter(
        Q(from_user=a, to_user=b) | Q(from_user=b, to_user=a), status=FriendRequest.ACCEPTED
    ).exists()


def friends_of(user):
    from django.contrib.auth.models import User

    pairs = FriendRequest.objects.filter(
        Q(from_user=user) | Q(to_user=user), status=FriendRequest.ACCEPTED
    ).values_list("from_user_id", "to_user_id")
    ids = {i for pair in pairs for i in pair} - {user.id}
    return User.objects.filter(id__in=ids).select_related("profile")
