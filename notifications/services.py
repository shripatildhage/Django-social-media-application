from .models import Notification


def notify(recipient, actor, verb, post=None):
    """Notification save kara (swatahala notify karu naye)."""
    if recipient == actor:
        return None
    return Notification.objects.create(recipient=recipient, actor=actor, verb=verb, post=post)
