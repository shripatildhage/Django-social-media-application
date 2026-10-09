from django.urls import path

from . import views

urlpatterns = [
    path("", views.notification_list, name="notifications"),
    path("unread/", views.unread_count, name="notifications_unread"),
    path("read-all/", views.mark_all_read, name="notifications_read_all"),
    path("<int:pk>/open/", views.open_notification, name="notification_open"),
]
