from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from friends.models import Follow
from notifications.models import Notification
from notifications.services import notify
from posts.services import visible_posts

from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, NotificationSerializer, PostSerializer, UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_permissions(self):
        # like / comments sarvanna chalatat; edit/delete fakt author la
        if self.action in ("like", "comments"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        qs = visible_posts(self.request.user)
        q = self.request.query_params.get("search")
        author = self.request.query_params.get("author")
        if q:
            qs = qs.filter(content__icontains=q)
        if author:
            qs = qs.filter(author__username=author)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        if post.likes.filter(pk=request.user.pk).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
            notify(recipient=post.author, actor=request.user, verb="liked your post", post=post)
        return Response({"liked": liked, "like_count": post.likes.count()})

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "POST":
            ser = CommentSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save(post=post, author=request.user)
            notify(recipient=post.author, actor=request.user, verb="commented on your post", post=post)
            return Response(ser.data, status=201)
        return Response(CommentSerializer(post.comments.select_related("author"), many=True).data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    lookup_field = "username"
    queryset = User.objects.select_related("profile").order_by("username")

    @action(detail=True, methods=["post"])
    def follow(self, request, username=None):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=400)
        obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if created:
            notify(recipient=target, actor=request.user, verb="started following you")
        else:
            obj.delete()
        return Response({"following": created})


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"status": "ok"})
