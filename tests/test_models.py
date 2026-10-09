from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from friends.models import Follow, FriendRequest, are_friends, friends_of
from notifications.models import Notification
from notifications.services import notify
from posts.models import Comment, Post
from posts.services import can_view_user_posts, visible_posts


class ModelTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user("alice", password="pw12345678")
        self.b = User.objects.create_user("bob", password="pw12345678")

    def test_profile_created_automatically(self):
        self.assertTrue(hasattr(self.a, "profile"))
        self.assertEqual(str(self.a.profile), "alice Profile")

    def test_post_like_count_and_str(self):
        p = Post.objects.create(author=self.a, content="hi")
        p.likes.add(self.b)
        self.assertEqual(p.like_count(), 1)
        self.assertIn("alice", str(p))

    def test_comment_str(self):
        p = Post.objects.create(author=self.a, content="hi")
        c = Comment.objects.create(post=p, author=self.b, content="yo")
        self.assertIn("bob", str(c))

    def test_cannot_follow_self_or_twice(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(follower=self.a, following=self.a)
        Follow.objects.create(follower=self.a, following=self.b)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(follower=self.a, following=self.b)

    def test_friendship(self):
        FriendRequest.objects.create(from_user=self.a, to_user=self.b, status=FriendRequest.ACCEPTED)
        self.assertTrue(are_friends(self.a, self.b))
        self.assertTrue(are_friends(self.b, self.a))
        self.assertIn(self.b, friends_of(self.a))

    def test_private_profile_visibility(self):
        self.b.profile.is_private = True
        self.b.profile.save()
        Post.objects.create(author=self.b, content="secret")
        self.assertFalse(can_view_user_posts(self.a, self.b))
        self.assertEqual(visible_posts(self.a).count(), 0)
        Follow.objects.create(follower=self.a, following=self.b)
        self.assertTrue(can_view_user_posts(self.a, self.b))
        self.assertEqual(visible_posts(self.a).count(), 1)

    def test_hidden_posts_excluded(self):
        Post.objects.create(author=self.b, content="bad", is_hidden=True)
        self.assertEqual(visible_posts(self.a).count(), 0)

    def test_notify_skips_self_and_creates_other(self):
        self.assertIsNone(notify(self.a, self.a, "liked your post"))
        n = notify(self.a, self.b, "started following you")
        self.assertEqual(Notification.objects.filter(recipient=self.a).count(), 1)
        self.assertEqual(n.text, "bob started following you")
