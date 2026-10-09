from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from friends.models import Follow
from notifications.services import notify

from .forms import CommentForm, PostForm
from .models import Post, Report
from .services import following_feed, visible_posts


@login_required
def home(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post published.")
            return redirect("home")
    else:
        form = PostForm()

    mode = request.GET.get("feed", "following")
    qs = visible_posts(request.user) if mode == "all" else following_feed(request.user)
    page = Paginator(qs, 10).get_page(request.GET.get("page"))

    followed = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
    suggestions = (
        User.objects.exclude(id__in=list(followed) + [request.user.id]).select_related("profile").order_by("?")[:5]
    )
    return render(request, "home.html", {"form": form, "page": page, "mode": mode, "suggestions": suggestions})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    comments = post.comments.select_related("author__profile")
    return render(request, "post_detail.html", {"post": post, "comments": comments, "comment_form": CommentForm()})


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("home")


@login_required
@require_POST
def post_like(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        notify(recipient=post.author, actor=request.user, verb="liked your post", post=post)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "count": post.likes.count()})
    return redirect(request.META.get("HTTP_REFERER") or "home")


@login_required
@require_POST
def comment_add(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post, comment.author = post, request.user
        comment.save()
        notify(recipient=post.author, actor=request.user, verb="commented on your post", post=post)
    else:
        messages.error(request, "Comment cannot be empty.")
    return redirect("post_detail", pk=pk)


@login_required
@require_POST
def post_report(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    reason = request.POST.get("reason", "").strip()[:255] or "Inappropriate content"
    _, created = Report.objects.get_or_create(post=post, reporter=request.user, defaults={"reason": reason})
    messages.success(request, "Thanks - a moderator will review this post." if created else "You already reported this post.")
    return redirect("post_detail", pk=pk)


@login_required
def search(request):
    q = request.GET.get("q", "").strip()
    users, posts = User.objects.none(), Post.objects.none()
    if q:
        users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)).select_related("profile")[:20]
        posts = visible_posts(request.user).filter(content__icontains=q)[:20]
    return render(request, "search.html", {"q": q, "users": users, "posts": posts})
