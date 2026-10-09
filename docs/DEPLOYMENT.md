# Deployment Guide

## Production checklist
1. Set `DJANGO_DEBUG=False`, a long random `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=yourdomain.com`, and `CSRF_TRUSTED_ORIGINS=https://yourdomain.com`.
2. Use PostgreSQL (`DATABASE_URL_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`).
4. Generate and **commit migrations** (`python manage.py makemigrations`).
5. Run `python manage.py collectstatic --noinput` and `migrate`.
6. Serve with Gunicorn: `gunicorn social_platform.wsgi:application` (install `requirements-prod.txt`).
7. Uploaded media: use persistent storage (volume or S3 via `django-storages`); Heroku/Railway filesystems are ephemeral.

## Docker
`docker compose up --build` starts web (Gunicorn) and Postgres. Persisted volumes: `pgdata`, `media`.

## Railway
1. Push the repo to GitHub, create a project from it, add PostgreSQL plugin.
2. Set variables above (map the plugin credentials). Railway reads the `Procfile` (`web:` line).
3. Add a volume mounted at `/app/media` for uploads.
4. Run `python manage.py createsuperuser` from the Railway shell.

## Heroku
```bash
heroku create my-social-app
heroku addons:create heroku-postgresql
heroku config:set DJANGO_DEBUG=False DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=my-social-app.herokuapp.com
# map DATABASE_* from DATABASE_URL
git push heroku main
heroku run python manage.py createsuperuser
```
Add `S3`/Cloudinary storage for media on Heroku.

## Troubleshooting
- *400 Bad Request*: host missing from `DJANGO_ALLOWED_HOSTS`.
- *Static files 404*: run `collectstatic`; confirm WhiteNoise middleware is present.
- *Notification delay*: they refresh every 15 seconds (polling).
