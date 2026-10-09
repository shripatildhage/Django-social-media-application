from django.contrib import admin

from .models import Follow, FriendRequest

admin.site.register(Follow)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "status", "created_at")
    list_filter = ("status",)
