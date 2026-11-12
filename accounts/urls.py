from django.urls import path
from .views import AuthRootView, RegisterView, LoginView, LogoutView, CurrentUserView

urlpatterns = [
    path("", AuthRootView.as_view(), name="auth-root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
]
