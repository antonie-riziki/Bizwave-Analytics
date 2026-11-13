
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.supabase_auth import SupabaseAuthentication


class SupabaseBusinessRegisterView(APIView):
    authentication_classes = [SupabaseAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business_name = request.data.get("business_name")
        business_type = request.data.get("business_type")
        location = request.data.get("location", "")

        if not isinstance(business_name, str) or not business_name.strip():
            return Response(
                {"error": "Business name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(business_type, str) or not business_type.strip():
            return Response(
                {"error": "Business type is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(location, str):
            return Response(
                {"error": "Location must be text."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO businesses
                            (business_name, business_type, location)
                        VALUES (%s, %s, %s)
                        RETURNING business_id
                        """,
                        [
                            business_name.strip(),
                            business_type.strip(),
                            location.strip(),
                        ],
                    )

                    business_id = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        INSERT INTO business_members
                            (business_id, user_id, role)
                        VALUES (%s, %s, %s)
                        """,
                        [business_id, request.user.id, "owner"],
                    )

            return Response(
                {
                    "message": "Business registered successfully.",
                    "business_id": business_id,
                    "business_name": business_name.strip(),
                    "business_type": business_type.strip(),
                    "location": location.strip(),
                    "role": "owner",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception:
            return Response(
                {"error": "Business registration failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SupabaseMyBusinessesView(APIView):
    authentication_classes = [SupabaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    b.business_id,
                    b.business_name,
                    b.business_type,
                    b.location,
                    bm.role
                FROM businesses b
                INNER JOIN business_members bm
                    ON b.business_id = bm.business_id
                WHERE bm.user_id = %s
                ORDER BY b.business_id
                """,
                [str(request.user.id)],
            )

            rows = cursor.fetchall()

        businesses = [
            {
                "business_id": row[0],
                "business_name": row[1],
                "business_type": row[2],
                "location": row[3],
                "role": row[4],
            }
            for row in rows
        ]

        return Response({
            "count": len(businesses),
            "businesses": businesses,
        })
