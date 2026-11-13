
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BusinessViewSet
from .supabase_views import (
    SupabaseBusinessRegisterView,
    SupabaseMyBusinessesView,
)

router = DefaultRouter()
router.register("", BusinessViewSet, basename="business")

urlpatterns = [
    path(
        "register/",
        SupabaseBusinessRegisterView.as_view(),
        name="supabase-business-register",
    ),
    path(
        "my-businesses/",
        SupabaseMyBusinessesView.as_view(),
        name="supabase-my-businesses",
    ),
] + router.urls
