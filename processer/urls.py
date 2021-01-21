from django.urls import path
from. import views


app_name = "processer"
# 汎用Viewを使わない場合
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.detail, name='detail'),
    path("<int:pk>/image/", views.getFrameViaAjax, name="ajax_image"),
]