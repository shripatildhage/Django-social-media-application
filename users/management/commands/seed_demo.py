import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from friends.models import Follow
from posts.models import Comment, Post

NAMES = ["alex", "john", "sarah", "david", "priya", "mark", "jane", "mike"]
TEXTS = [
    "Just completed my Django project!",
    "Learning Django has been an incredible journey.",
    "Anyone tried Django Channels for real-time features?",
    "Deployed my first app today.",
    "Tip: use select_related to avoid N+1 queries.",
]


class Command(BaseCommand):
    help = "Create demo users (password: demo12345), posts, comments, likes and follows."

    def handle(self, *args, **opts):
        users = []
        for n in NAMES:
            u, created = User.objects.get_or_create(username=n, defaults={"email": f"{n}@example.com"})
            if created:
                u.set_password("demo12345")
                u.save()
            users.append(u)
        for u in users:
            for _ in range(2):
                p = Post.objects.create(author=u, content=random.choice(TEXTS))
                p.likes.set(random.sample(users, k=random.randint(0, len(users))))
                for c in random.sample(users, k=2):
                    Comment.objects.create(post=p, author=c, content="Great post!")
            for other in random.sample([x for x in users if x != u], k=3):
                Follow.objects.get_or_create(follower=u, following=other)
        self.stdout.write(self.style.SUCCESS("Demo data created. Log in as 'alex' / 'demo12345'."))
