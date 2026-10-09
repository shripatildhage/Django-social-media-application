from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("post/<int:pk>/like/", views.post_like, name="post_like"),
    path("post/<int:pk>/comment/", views.comment_add, name="comment_add"),
    path("post/<int:pk>/report/", views.post_report, name="post_report"),
]
