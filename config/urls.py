from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include


def auth_without_trailing_slash(request):
    return redirect("/api/auth/")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth", auth_without_trailing_slash),
    path("api/auth/", include("accounts.urls")),
    path("api/businesses/", include("businesses.urls")),
]
