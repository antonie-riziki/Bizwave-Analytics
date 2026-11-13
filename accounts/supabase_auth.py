
import os

import jwt
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SupabaseUser:
    def __init__(self, user_id, claims):
        self.id = user_id
        self.pk = user_id
        self.email = claims.get("email", "")
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self):
        return self.email or self.id


class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get("Authorization", "")

        if not authorization:
            return None

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed(
                "Use Authorization: Bearer <access_token>"
            )

        token = parts[1]
        supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")

        if not supabase_url:
            raise AuthenticationFailed("Supabase URL is not configured.")

        jwks_url = (
            f"{supabase_url}/auth/v1/.well-known/jwks.json"
        )

        try:
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer=f"{supabase_url}/auth/v1",
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )

            if claims.get("role") != "authenticated":
                raise AuthenticationFailed("Invalid user role.")

            user_id = claims["sub"]
            return SupabaseUser(user_id, claims), token

        except AuthenticationFailed:
            raise
        except (jwt.PyJWTError, ValueError) as exc:
            raise AuthenticationFailed(
                "Invalid or expired Supabase access token."
            ) from exc
        except Exception as exc:
            raise AuthenticationFailed(
                "Unable to verify Supabase access token."
            ) from exc

    def authenticate_header(self, request):
        return "Bearer"
