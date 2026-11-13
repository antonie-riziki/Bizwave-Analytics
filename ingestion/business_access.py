
from django.db import connection
from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied,
    ValidationError,
)

from accounts.supabase_auth import SupabaseAuthentication


def get_authorized_business_id(request):
    """
    Verify the Supabase user and check business membership.
    """

    authentication = SupabaseAuthentication()
    result = authentication.authenticate(request)

    if result is None:
        raise AuthenticationFailed(
            "Supabase access token is required."
        )

    user, _ = result

    raw_business_id = (
        request.headers.get("X-Business-ID")
        or request.GET.get("business_id")
    )

    if not raw_business_id:
        raise ValidationError(
            "Business ID is required."
        )

    try:
        business_id = int(raw_business_id)
    except (TypeError, ValueError):
        raise ValidationError(
            "Business ID must be a valid integer."
        )

    if business_id <= 0:
        raise ValidationError(
            "Business ID must be positive."
        )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM business_members
            WHERE business_id = %s
              AND user_id = %s
            LIMIT 1
            """,
            [business_id, str(user.id)],
        )

        if cursor.fetchone() is None:
            raise PermissionDenied(
                "You do not have access to this business."
            )

    return business_id


def get_upload_authorized_business_id(request):
    business_id = get_authorized_business_id(request)

    authentication = SupabaseAuthentication()
    user, _ = authentication.authenticate(request)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM business_members
            WHERE business_id = %s
              AND user_id = %s
              AND LOWER(role) IN ('owner', 'admin')
            LIMIT 1
            """,
            [business_id, str(user.id)],
        )

        if cursor.fetchone() is None:
            raise PermissionDenied(
                "Only business owners and admins can upload sales."
            )

    return business_id