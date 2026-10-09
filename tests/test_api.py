from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from posts.models import Post


class ApiTests(APITestCase):
    def setUp(self):
        self.a = User.objects.create_user("alice", password="pw12345678")
        self.b = User.objects.create_user("bob", password="pw12345678")

    def test_auth_required(self):
        self.assertIn(self.client.get("/api/posts/").status_code, (401, 403))

    def test_create_and_list_posts(self):
        self.client.force_authenticate(self.a)
        r = self.client.post("/api/posts/", {"content": "api post"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["author"], "alice")
        self.assertEqual(self.client.get("/api/posts/").data["count"], 1)

    def test_empty_content_rejected(self):
        self.client.force_authenticate(self.a)
        self.assertEqual(self.client.post("/api/posts/", {"content": "  "}, format="json").status_code, 400)

    def test_cannot_edit_others_post(self):
        p = Post.objects.create(author=self.b, content="x")
        self.client.force_authenticate(self.a)
        self.assertEqual(self.client.patch(f"/api/posts/{p.id}/", {"content": "y"}, format="json").status_code, 403)

    def test_like_and_comment(self):
        p = Post.objects.create(author=self.b, content="x")
        self.client.force_authenticate(self.a)
        self.assertTrue(self.client.post(f"/api/posts/{p.id}/like/").data["liked"])
        r = self.client.post(f"/api/posts/{p.id}/comments/", {"content": "hey"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(len(self.client.get(f"/api/posts/{p.id}/comments/").data), 1)

    def test_follow(self):
        self.client.force_authenticate(self.a)
        self.assertTrue(self.client.post("/api/users/bob/follow/").data["following"])
        self.assertFalse(self.client.post("/api/users/bob/follow/").data["following"])
        self.assertEqual(self.client.post("/api/users/alice/follow/").status_code, 400)

    def test_notifications_endpoint(self):
        self.client.force_authenticate(self.a)
        self.client.post("/api/users/bob/follow/")
        self.client.force_authenticate(self.b)
        self.assertEqual(self.client.get("/api/notifications/").data["count"], 1)
