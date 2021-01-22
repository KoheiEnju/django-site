from django.urls import path
from. import views
from django.contrib.auth.views import LogoutView


app_name = "accounts"
# 汎用Viewを使わない場合
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_account, name='create'),
    path("login/", views.login_account, name='login'),
    path("logout/", LogoutView.as_view(template_name='accounts/index.html'), name='logout'),
]