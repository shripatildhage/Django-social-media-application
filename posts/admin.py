from django.contrib import admin

from .models import Comment, Post, Report


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short", "created_at", "is_hidden")
    list_filter = ("is_hidden", "created_at")
    search_fields = ("content", "author__username")
    actions = ["hide_posts", "unhide_posts"]

    @admin.display(description="Content")
    def short(self, obj):
        return obj.content[:60]

    @admin.action(description="Hide selected posts (moderation)")
    def hide_posts(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description="Unhide selected posts")
    def unhide_posts(self, request, queryset):
        queryset.update(is_hidden=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "created_at")
    search_fields = ("content", "author__username")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("post", "reporter", "reason", "resolved", "created_at")
    list_filter = ("resolved",)
    actions = ["hide_reported_posts"]

    @admin.action(description="Hide reported posts and mark resolved")
    def hide_reported_posts(self, request, queryset):
        Post.objects.filter(id__in=queryset.values("post_id")).update(is_hidden=True)
        queryset.update(resolved=True)
