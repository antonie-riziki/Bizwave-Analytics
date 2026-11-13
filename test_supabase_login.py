
import os
import getpass

import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_PUBLISHABLE_KEY"]


def main():
    print("\n===== BIZ WAVE BACKEND TEST =====\n")

    email = input("Enter your test user email: ").strip()
    password = getpass.getpass("Enter your test user password: ")

    # STEP 1: Supabase login
    try:
        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": email,
                "password": password,
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        print("Supabase connection failed:", exc)
        return
    finally:
        password = None

    if response.status_code != 200:
        print("\nSupabase login: FAILED")
        print("HTTP status:", response.status_code)

        try:
            error = response.json()
            print(
                "Error code:",
                error.get("error_code") or error.get("code"),
            )
            print(
                "Error message:",
                error.get("msg")
                or error.get("message")
                or error.get("error_description"),
            )
        except ValueError:
            print("Supabase returned an unexpected response.")

        return

    token = response.json().get("access_token")

    if not token:
        print("Login succeeded but no access token was returned.")
        return

    print("\nSupabase login: SUCCESS")

    # STEP 2: Initialize Django
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings",
    )

    import django
    django.setup()

    from rest_framework.test import APIRequestFactory
    from accounts.supabase_auth import SupabaseAuthentication
    from django.test import Client

    # STEP 3: Verify Supabase JWT
    request = APIRequestFactory().get(
        "/api/test/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    try:
        result = SupabaseAuthentication().authenticate(request)

        if result is None:
            print("Django token verification: FAILED")
            return

        user, _ = result

        print("Django token verification: SUCCESS")
        print(
            "Authenticated email matches:",
            user.email.lower() == email.lower(),
        )

    except Exception as exc:
        print("Django token verification: FAILED")
        print("Error:", str(exc))
        return

    # STEP 4: Test My Businesses API
    print("\n===== MY BUSINESSES API TEST =====")

    client = Client(SERVER_NAME="localhost")

    try:
        businesses_response = client.get(
            "/api/businesses/my-businesses/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        print("HTTP status:", businesses_response.status_code)

        if "application/json" in businesses_response.headers.get(
            "Content-Type", ""
        ):
            print("Response:", businesses_response.json())
        else:
            print(
                "Unexpected response content type:",
                businesses_response.headers.get("Content-Type"),
            )

        if businesses_response.status_code == 200:
            print("My Businesses API: SUCCESS")
        else:
            print("My Businesses API: FAILED")

    except Exception as exc:
        print("My Businesses API test error:", str(exc))


    # STEP 5: Transactions Security Test
    print("\n===== TRANSACTIONS SECURITY TEST =====")

    endpoint = "/api/ingestion/transactions/"

    # Test 1: Authorized business
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="2",
    )
    print("Authorized business status:", response.status_code)

    # Test 2: Missing authentication token
    response = client.get(
        endpoint,
        HTTP_X_BUSINESS_ID="2",
    )
    print("Missing token status:", response.status_code)

    # Test 3: Business without membership
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="999999",
    )
    print("Unauthorized business status:", response.status_code)


    # Sales Analytics Security Test
    print("\n===== SALES ANALYTICS SECURITY TEST =====")

    endpoint = "/api/ingestion/analytics/"

    # Test 1: Authorized business
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="2",
    )
    print("Authorized analytics status:", response.status_code)

    if response.status_code == 200:
        print("Analytics response:", response.json())

    # Test 2: Missing authentication token
    response = client.get(
        endpoint,
        HTTP_X_BUSINESS_ID="2",
    )
    print("Missing token status:", response.status_code)

    # Test 3: Business without membership
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="999999",
    )
    print("Unauthorized business status:", response.status_code)

    # Daily Sales Security Test
    print("\n===== DAILY SALES SECURITY TEST =====")
    endpoint = "/api/ingestion/daily-sales/"

    # Test 1: Authorized business
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="2",
    )
    print("Authorized daily sales status:", response.status_code)

    if response.status_code == 200:
        print("Daily sales response:", response.json())

    # Test 2: Missing authentication token
    response = client.get(
        endpoint,
        HTTP_X_BUSINESS_ID="2",
    )
    print("Missing token status:", response.status_code)

    # Test 3: Unauthorized business
    response = client.get(
        endpoint,
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="999999",
    )
    print("Unauthorized business status:", response.status_code)


    # CSV/Excel Upload Security Test
    print("\n===== FILE UPLOAD SECURITY TEST =====")
    endpoint = "/api/ingestion/upload/"

    # Test 1: Authorized owner, but no file supplied
    response = client.post(
        endpoint,
        data={},
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="2",
    )
    print("Authorized owner status:", response.status_code)
    print("Response:", response.json())

    # Test 2: Missing authentication token
    response = client.post(
        endpoint,
        data={},
        HTTP_X_BUSINESS_ID="2",
    )
    print("Missing token status:", response.status_code)

    # Test 3: Unauthorized business
    response = client.post(
        endpoint,
        data={},
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_X_BUSINESS_ID="999999",
    )
    print("Unauthorized business status:", response.status_code)


    # STEP 5: Optional business registration
    print("\n===== BUSINESS REGISTRATION TEST =====")

    choice = input(
        "Register another demo business? (yes/no): "
    ).strip().lower()

    if choice not in ("yes", "y"):
        print("Business registration skipped.")
        print("\n===== TEST COMPLETED =====")
        return

    try:
        business_response = client.post(
            "/api/businesses/register/",
            data={
                "business_name": "Bizwave Demo Shop",
                "business_type": "Retail",
                "location": "Bungoma",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        print(
            "Business registration status:",
            business_response.status_code,
        )

        if "application/json" in business_response.headers.get(
            "Content-Type", ""
        ):
            print(
                "Business registration response:",
                business_response.json(),
            )
        else:
            print(
                "Unexpected response content type:",
                business_response.headers.get("Content-Type"),
            )

        if business_response.status_code == 201:
            print("Business registration: SUCCESS")
        else:
            print("Business registration: FAILED")

    except Exception as exc:
        print("Business registration test error:", str(exc))

    print("\n===== TEST COMPLETED =====")


if __name__ == "__main__":
    main()
