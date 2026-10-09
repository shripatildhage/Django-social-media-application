# REST API

Base URL: `/api/`. Auth: session cookie (log in via `/api/auth/login/` or the site) or HTTP Basic. Responses are paginated (`count`, `next`, `previous`, `results`). Browsable API at `/api/`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/` | List visible posts. Filters: `?search=text`, `?author=username` |
| POST | `/api/posts/` | Create post (`content`, optional `image` as multipart) |
| GET/PATCH/DELETE | `/api/posts/{id}/` | Retrieve / edit / delete (author only for write) |
| POST | `/api/posts/{id}/like/` | Toggle like -> `{"liked": true, "like_count": 3}` |
| GET/POST | `/api/posts/{id}/comments/` | List / add comments |
| GET | `/api/users/` , `/api/users/{username}/` | Users and profile summary |
| POST | `/api/users/{username}/follow/` | Toggle follow -> `{"following": true}` |
| GET | `/api/notifications/` | Your notifications |
| POST | `/api/notifications/mark_all_read/` | Mark all read |

## Examples
```bash
curl -u alex:demo12345 http://127.0.0.1:8000/api/posts/
curl -u alex:demo12345 -X POST -H "Content-Type: application/json" \
     -d '{"content":"Hello from the API"}' http://127.0.0.1:8000/api/posts/
curl -u alex:demo12345 -X POST http://127.0.0.1:8000/api/posts/1/like/
```
Status codes: 200/201 success, 400 validation error, 401/403 not authenticated or not allowed, 404 not found / not visible.

> Basic auth is for development and testing. For production mobile apps add token or JWT auth (e.g. `djangorestframework-simplejwt`).
