from os import name
from django.urls import path
from. import views


app_name = "processer"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.detail, name='detail'),
    path("<int:pk>/image/", views.getFrameViaAjax, name="ajax_image"),
]