from django.urls import path

from . import views

urlpatterns = [
    path("", views.friends_list, name="friends"),
    path("follow/<str:username>/", views.toggle_follow, name="toggle_follow"),
    path("request/<str:username>/", views.send_request, name="send_request"),
    path("respond/<int:pk>/<str:action>/", views.respond_request, name="respond_request"),
]
