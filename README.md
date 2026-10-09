# Social Platform (Django)

A full-featured social media platform built with Django: user profiles, posts with image uploads, comments, likes, follow + friend-request systems, notifications (auto-refresh, polling), search, privacy settings, content moderation, a REST API, a Bootstrap responsive UI, tests, and Docker deployment.

## Project overview
**Goals:** demonstrate Django's MTV architecture, ORM relationships, authentication, forms/validation, admin customization, Django REST Framework, testing and deployment.

| Feature | Where |
|---|---|
| Registration / login / logout | `users/` |
| Profile extension (bio, avatar, cover, privacy) | `users/models.py` |
| Posts with media, comments, likes | `posts/` |
| Follow system + friend requests | `friends/` |
| Notifications (JS polling) | `notifications/` |
| REST API (`/api/`) | `api/` |
| Search + filtering | `posts/views.py::search`, `/api/posts/?search=` |
| Privacy + moderation | `UserProfile.is_private`, `Report`, admin actions |

## Quick start (local)
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo          # optional demo data (alex / demo12345)
python manage.py runserver          # normal Django server, extra kahi install nako
```
Open http://127.0.0.1:8000/ - admin at `/admin/`, API at `/api/`.

> Migration files already included ahet, `makemigrations` challavayachi garaj nahi. Model badalle tar tevhach challva.

## Docker
```bash
docker compose up --build        # Postgres + Gunicorn on :8000
docker compose exec web python manage.py createsuperuser
```

## Run tests
```bash
python manage.py test tests -v 2
```

## Project structure
```
social_platform/      Django project root
|-- manage.py
|-- requirements.txt
|-- social_platform/  settings, urls, asgi, wsgi
|-- users/            registration, profiles, forms, signals, seed_demo command
|-- posts/            Post, Comment, Report, feed/visibility services
|-- friends/          Follow, FriendRequest
|-- notifications/    Notification model, service, polling view
|-- api/              DRF serializers, viewsets, permissions
|-- templates/        HTML templates (Bootstrap 5)
|-- static/           CSS, JS (AJAX likes + notification polling)
|-- media/            uploaded files
|-- tests/            model, view and API tests
|-- docs/             architecture, API, deployment, user manual, testing
|-- Dockerfile, docker-compose.yml, Procfile, .env.example
```

## Documentation
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - design, data model, algorithms
- [docs/API.md](docs/API.md) - REST endpoints
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Docker, Heroku, Railway
- [docs/USER_MANUAL.md](docs/USER_MANUAL.md) - end-user guide
- [docs/TESTING.md](docs/TESTING.md) - test evidence and validation
- [docs/screenshots/](docs/screenshots/) - add your own screenshots here (see the checklist in TESTING.md)

## Configuration
Copy `.env.example` to `.env` and export the variables (or set them in your host). Without `DATABASE_URL_NAME` SQLite is used; Redis / Daphne / Channels chi garaj nahi.
