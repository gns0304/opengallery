from django.urls import path
from .views import SignupView, SigninView, SignoutView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/",  SigninView.as_view(), name="login"),
    path("logout/", SignoutView.as_view(), name="logout"),
]