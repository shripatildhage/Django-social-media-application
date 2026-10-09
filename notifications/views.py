from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    items = request.user.notifications.select_related("actor", "post")[:50]
    return render(request, "notifications.html", {"notifications": items})


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect("notifications")


@login_required
def open_notification(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect(n.get_url())


@login_required
def unread_count(request):
    """Browser he URL darr 15 sec la vichartoy (polling) - latest unread count + navin notification."""
    since = request.GET.get("since")
    qs = request.user.notifications.filter(is_read=False)
    latest = []
    if since and since.isdigit():
        for n in qs.filter(id__gt=int(since)).order_by("id")[:5]:
            latest.append({"id": n.id, "text": n.text, "url": n.get_url()})
    last = request.user.notifications.order_by("-id").values_list("id", flat=True).first() or 0
    return JsonResponse({"unread": qs.count(), "last_id": last, "new": latest})
