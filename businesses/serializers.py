from rest_framework import serializers
from .models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "industry",
            "description",
            "email",
            "phone",
            "website",
            "country",
            "city",
            "address",
            "currency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
