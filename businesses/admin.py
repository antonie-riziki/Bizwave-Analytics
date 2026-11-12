from django.contrib import admin
from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "owner", "country", "created_at")
    search_fields = ("name", "industry", "owner__email")
    list_filter = ("industry", "country", "currency")
