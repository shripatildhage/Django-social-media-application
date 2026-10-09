# Architecture & Technical Details

## 1. MTV overview
Django's Model-Template-View pattern: **models** (`*/models.py`) define data, **views** (`*/views.py`) hold request logic, **templates** render HTML. Business rules shared by HTML views and the API live in `posts/services.py` and `notifications/services.py`, so both interfaces behave identically.

## 2. Data model
```
User (django.contrib.auth) 1--1 UserProfile
User 1--* Post            Post *--* User (likes)
Post 1--* Comment         Comment *--1 User
Post 1--* Report          Report  *--1 User (reporter)
User *--* User  via Follow(follower, following)          (directed)
User *--* User  via FriendRequest(from_user, to_user, status) (mutual once accepted)
Notification(recipient, actor, verb, post?, is_read)
```
Integrity constraints: unique follow pair, no self-follow (`CheckConstraint`), unique friend request, no self-request, one report per user per post.

## 3. Key algorithms
**Post visibility** (`posts/services.visible_posts`): a post is visible when it is not hidden AND (author is me OR author's profile is public OR I follow the author OR we are friends). Implemented as one ORM query with `Q` objects + `distinct()`. This enforces privacy settings in the feed, profile, search, post detail and API.

**Feed** (`following_feed`): visible posts whose author is in `{me} U following U friends`, ordered by `-created_at` (indexed) and paginated 10 per page (`Paginator`). "Discover" shows all visible posts.

**Friend system**: a request is `pending -> accepted | declined`. If B sends a request to A while A's request to B is pending, it is auto-accepted. `friends_of(user)` collects accepted pairs in either direction into a set of IDs (set union removes duplicates), then fetches users in one query.

**Likes**: `ManyToManyField` toggle - add if absent, remove if present; AJAX returns the new count as JSON.

**Notifications**: `notify()` (1) skips self-notifications, (2) saves a row, (3) the browser JS polls `/notifications/unread/` every 15 seconds, updates the badge and shows a toast for new items. No WebSockets / Channels needed; notifications also always appear on `/notifications/`.

**Search**: `icontains` filters over usernames/names and visible post content (limited to 20 results).

## 4. Security
CSRF protection on every POST form; POST-only for state changes (`require_POST`); `login_required` everywhere; author-only deletion (404 otherwise); upload size validation (5 MB) and `ImageField` (Pillow verifies images); Django password validators; unique email check; template auto-escaping (JS toast uses `textContent`); HTTPS/secure cookies when `DEBUG=False`; secrets via environment variables.

## 5. Performance
`select_related`/`prefetch_related` on feeds, DB index on `created_at`, pagination, WhiteNoise for static files, gunicorn workers. Next steps: annotate counts (`Count('likes')`) to avoid per-post count queries, Django cache for suggestions, Celery for heavy tasks.

## 6. Moderation
Users report posts (`Report`). Admins can hide posts (`is_hidden`) via admin actions; hidden posts disappear from every feed, search result and API response.
