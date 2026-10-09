# Testing Evidence & Validation

Run: `python manage.py test tests -v 2`

| Area | Test file | What is verified |
|---|---|---|
| Models | `tests/test_models.py` | auto profile creation, like counts, `__str__`, unique/no-self follow constraints, friendship symmetry, private-profile visibility, hidden posts, self-notification skipping |
| Views | `tests/test_views.py` | login required, registration + duplicate email, post create/empty rejection, like toggle + notification + AJAX JSON, comments, author-only delete, follow toggle, friend request flow, private profile hides posts, search, one report per user, mark-all-read |
| API | `tests/test_api.py` | auth required, create/list, validation, 403 on editing others' posts, like/comment actions, follow, notifications |

## Manual validation checklist (capture screenshots into `docs/screenshots/`)
- [ ] Register page and home feed
- [ ] Post with image, likes and comments
- [ ] Profile page (public) and private-account view
- [ ] Friend request accept/decline
- [ ] Live notification toast (two browsers)
- [ ] Admin moderation action hiding a post
- [ ] Browsable API at `/api/posts/`
- [ ] Mobile layout (browser dev tools)
- [ ] Passing test output

Environment note: these tests were written without access to a Django runtime in the authoring sandbox, so run them once on your machine and fix any environment-specific issue before submitting.
