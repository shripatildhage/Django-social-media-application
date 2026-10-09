from django.contrib.auth.models import User
from rest_framework import serializers

from notifications.models import Notification
from posts.models import Comment, Post


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source="profile.bio", read_only=True)
    location = serializers.CharField(source="profile.location", read_only=True)
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "bio", "location", "followers", "following")

    def get_followers(self, obj):
        return obj.follower_set.count()

    def get_following(self, obj):
        return obj.following_set.count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")
        read_only_fields = ("id", "author", "created_at")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "author", "content", "image", "created_at", "like_count", "comment_count", "liked_by_me")
        read_only_fields = ("id", "author", "created_at")

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_liked_by_me(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(pk=user.pk).exists()

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Post cannot be empty.")
        return value.strip()


class NotificationSerializer(serializers.ModelSerializer):
    text = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "text", "is_read", "created_at", "post")
