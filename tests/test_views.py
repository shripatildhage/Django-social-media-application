from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from friends.models import Follow, FriendRequest
from notifications.models import Notification
from posts.models import Post, Report


class ViewTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user("alice", "a@x.com", "pw12345678")
        self.b = User.objects.create_user("bob", "b@x.com", "pw12345678")
        self.client.login(username="alice", password="pw12345678")

    def test_login_required(self):
        self.client.logout()
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_register(self):
        self.client.logout()
        r = self.client.post(reverse("register"), {
            "username": "carol", "email": "c@x.com", "password1": "Str0ng!pass99", "password2": "Str0ng!pass99"})
        self.assertRedirects(r, reverse("home"))
        self.assertTrue(User.objects.filter(username="carol").exists())

    def test_duplicate_email_rejected(self):
        self.client.logout()
        r = self.client.post(reverse("register"), {
            "username": "dave", "email": "a@x.com", "password1": "Str0ng!pass99", "password2": "Str0ng!pass99"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="dave").exists())

    def test_create_post_and_empty_rejected(self):
        self.client.post(reverse("home"), {"content": "hello world"})
        self.assertEqual(Post.objects.filter(author=self.a).count(), 1)
        self.client.post(reverse("home"), {"content": "   "})
        self.assertEqual(Post.objects.count(), 1)

    def test_like_toggle_and_notification(self):
        p = Post.objects.create(author=self.b, content="x")
        self.client.post(reverse("post_like", args=[p.id]))
        self.assertEqual(p.likes.count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.b, verb="liked your post").count(), 1)
        self.client.post(reverse("post_like", args=[p.id]))
        self.assertEqual(p.likes.count(), 0)

    def test_ajax_like_returns_json(self):
        p = Post.objects.create(author=self.b, content="x")
        r = self.client.post(reverse("post_like", args=[p.id]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.json(), {"liked": True, "count": 1})

    def test_comment(self):
        p = Post.objects.create(author=self.b, content="x")
        self.client.post(reverse("comment_add", args=[p.id]), {"content": "nice"})
        self.assertEqual(p.comments.count(), 1)

    def test_only_author_can_delete(self):
        p = Post.objects.create(author=self.b, content="x")
        self.assertEqual(self.client.post(reverse("post_delete", args=[p.id])).status_code, 404)
        self.assertTrue(Post.objects.filter(id=p.id).exists())

    def test_follow_toggle(self):
        self.client.post(reverse("toggle_follow", args=["bob"]))
        self.assertTrue(Follow.objects.filter(follower=self.a, following=self.b).exists())
        self.client.post(reverse("toggle_follow", args=["bob"]))
        self.assertFalse(Follow.objects.filter(follower=self.a, following=self.b).exists())

    def test_friend_request_flow(self):
        self.client.post(reverse("send_request", args=["bob"]))
        fr = FriendRequest.objects.get(from_user=self.a, to_user=self.b)
        self.client.logout()
        self.client.login(username="bob", password="pw12345678")
        self.client.post(reverse("respond_request", args=[fr.id, "accept"]))
        fr.refresh_from_db()
        self.assertEqual(fr.status, FriendRequest.ACCEPTED)

    def test_private_profile_hides_posts(self):
        self.b.profile.is_private = True
        self.b.profile.save()
        Post.objects.create(author=self.b, content="secret-text")
        r = self.client.get(reverse("profile", args=["bob"]))
        self.assertNotContains(r, "secret-text")

    def test_search(self):
        Post.objects.create(author=self.b, content="django rocks")
        r = self.client.get(reverse("search"), {"q": "django"})
        self.assertContains(r, "django rocks")

    def test_report_once(self):
        p = Post.objects.create(author=self.b, content="x")
        self.client.post(reverse("post_report", args=[p.id]), {"reason": "spam"})
        self.client.post(reverse("post_report", args=[p.id]), {"reason": "spam"})
        self.assertEqual(Report.objects.count(), 1)

    def test_notifications_mark_read(self):
        Notification.objects.create(recipient=self.a, actor=self.b, verb="started following you")
        self.client.post(reverse("notifications_read_all"))
        self.assertEqual(self.a.notifications.filter(is_read=False).count(), 0)


class NotificationPollingTests(TestCase):
    def test_unread_endpoint(self):
        a = User.objects.create_user("pa", password="pw12345678")
        b = User.objects.create_user("pb", password="pw12345678")
        Notification.objects.create(recipient=a, actor=b, verb="started following you")
        self.client.login(username="pa", password="pw12345678")
        d = self.client.get("/notifications/unread/?since=0").json()
        self.assertEqual(d["unread"], 1)
        self.assertEqual(len(d["new"]), 1)
