from django.urls import path
from . import views


app_name = "nichan"
urlpatterns = [
    path("", views.index, name='index'),
    path("<int:text_id>/detail/", views.detail, name='detail'),
    path("post/", views.post, name='post'),
]