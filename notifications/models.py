from django.conf import settings
from django.db import models
from django.urls import reverse


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    verb = models.CharField(max_length=100)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.verb} -> {self.recipient}"

    @property
    def text(self):
        return f"{self.actor.username} {self.verb}"

    def get_url(self):
        if self.post_id:
            return reverse("post_detail", args=[self.post_id])
        return reverse("profile", args=[self.actor.username])
