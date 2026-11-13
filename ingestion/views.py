
import io
from decimal import Decimal, InvalidOperation

import pandas as pd
from django.conf import settings
from django.db import connection, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


REQUIRED_COLUMNS = [
    "Order_ID",
    "Pizza_Name",
    "Quantity",
    "Estimated_Order_Total_KES",
]


def local_demo_only(request):
    """Restrict unauthenticated demo APIs to local development."""
    return (
        settings.DEBUG
        and request.META.get("REMOTE_ADDR") in ("127.0.0.1", "::1")
    )


@csrf_exempt
@require_POST
def upload_file(request):
    """Upload CSV/Excel orders and save sales to Supabase."""

    if not local_demo_only(request):
        return JsonResponse(
            {"error": "Local development only"},
            status=403
        )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "Please upload a CSV or Excel file."},
            status=400
        )

    filename = uploaded_file.name.lower()

    if not filename.endswith((".csv", ".xlsx")):
        return JsonResponse(
            {"error": "Only CSV and XLSX files are supported."},
            status=400
        )

    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse(
            {"error": "File must not exceed 5 MB."},
            status=400
        )

    try:
        file_bytes = io.BytesIO(uploaded_file.read())

        if filename.endswith(".csv"):
            df = pd.read_csv(
                file_bytes,
                dtype={"Order_ID": str}
            )
        else:
            df = pd.read_excel(
                file_bytes,
                dtype={"Order_ID": str}
            )

    except Exception:
        return JsonResponse(
            {"error": "Unable to read the uploaded file."},
            status=400
        )

    if df.empty:
        return JsonResponse(
            {"error": "The uploaded file is empty."},
            status=400
        )

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return JsonResponse(
            {
                "error": "Missing required columns",
                "columns": missing_columns
            },
            status=400
        )

    if df[REQUIRED_COLUMNS].isnull().any().any():
        return JsonResponse(
            {"error": "Required fields cannot be empty."},
            status=400
        )

    if df["Order_ID"].astype(str).str.strip().duplicated().any():
        return JsonResponse(
            {"error": "Duplicate Order_ID values in uploaded file."},
            status=400
        )

    business_id = 1
    prepared = []

    try:
        for _, row in df.iterrows():
            order_id = str(row["Order_ID"]).strip()
            product = str(row["Pizza_Name"]).strip()
            quantity = Decimal(str(row["Quantity"]))
            amount = Decimal(str(row["Estimated_Order_Total_KES"]))

            if (
                not order_id
                or not product
                or not quantity.is_finite()
                or quantity <= 0
                or quantity != quantity.to_integral_value()
                or not amount.is_finite()
                or amount < 0
            ):
                raise ValueError("Invalid order values")

            description = (
                f"Order {order_id}: {product} x{int(quantity)}"
            )

            prepared.append(
                (order_id, description, amount)
            )

    except (ValueError, InvalidOperation, TypeError):
        return JsonResponse(
            {"error": "One or more orders contain invalid values."},
            status=400
        )

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT business_id
                    FROM businesses
                    WHERE business_id = %s
                    """,
                    [business_id]
                )

                if cursor.fetchone() is None:
                    return JsonResponse(
                        {"error": "Demo business does not exist."},
                        status=400
                    )

                cursor.execute(
                    "SELECT pg_advisory_xact_lock(%s)",
                    [business_id]
                )

                cursor.execute(
                    """
                    SELECT description
                    FROM transactions
                    WHERE business_id = %s
                    AND transaction_type = %s
                    """,
                    [business_id, "sale"]
                )

                existing = {
                    description.split(": ", 1)[0]
                    for (description,) in cursor.fetchall()
                    if description
                    and description.startswith("Order ")
                }

                saved = 0
                skipped = 0
                total_amount = Decimal("0")

                for order_id, description, amount in prepared:
                    key = f"Order {order_id}"

                    if key in existing:
                        skipped += 1
                        continue

                    cursor.execute(
                        """
                        INSERT INTO transactions
                        (
                            business_id,
                            transaction_type,
                            description,
                            amount
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        [
                            business_id,
                            "sale",
                            description,
                            amount
                        ]
                    )

                    existing.add(key)
                    saved += 1
                    total_amount += amount

    except Exception:
        return JsonResponse(
            {
                "error": "Database save failed. No new orders were committed."
            },
            status=500
        )

    return JsonResponse({
        "status": "success",
        "message": "File processed and transactions saved!",
        "business_id": business_id,
        "filename": uploaded_file.name,
        "total_rows": len(df),
        "saved_transactions": saved,
        "skipped_duplicates": skipped,
        "saved_amount_kes": str(total_amount)
    })


@require_GET
def get_transactions(request):
    """Retrieve demo business sales transactions from Supabase."""

    if not local_demo_only(request):
        return JsonResponse(
            {"error": "Local development only"},
            status=403
        )

    business_id = 1

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    transaction_id,
                    description,
                    amount,
                    transaction_date
                FROM transactions
                WHERE business_id = %s
                AND transaction_type = %s
                ORDER BY transaction_id DESC
                """,
                [business_id, "sale"]
            )

            rows = cursor.fetchall()

        transactions = [
            {
                "transaction_id": row[0],
                "description": row[1],
                "amount": str(row[2]),
                "transaction_date": (
                    row[3].isoformat()
                    if row[3] else None
                )
            }
            for row in rows
        ]

        total_sales = sum(
            (row[2] for row in rows),
            Decimal("0")
        )

        return JsonResponse({
            "status": "success",
            "business_id": business_id,
            "total_transactions": len(transactions),
            "total_sales_kes": str(total_sales),
            "transactions": transactions
        })

    except Exception:
        return JsonResponse(
            {"error": "Unable to retrieve transactions."},
            status=500
        )

        
@require_GET
def sales_analytics(request):
    """Calculate sales analytics from Supabase transactions."""

    if not local_demo_only(request):
        return JsonResponse(
            {"error": "Local development only"},
            status=403
        )

    business_id = 1

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT description, amount
                FROM transactions
                WHERE business_id = %s
                  AND transaction_type = %s
                """,
                [business_id, "sale"]
            )
            rows = cursor.fetchall()

        total_orders = len(rows)
        total_sales = sum(
            (amount for _, amount in rows),
            Decimal("0")
        )

        average_order = (
            total_sales / total_orders
            if total_orders else Decimal("0")
        )

        product_stats = {}

        for description, amount in rows:
            if not description or ": " not in description:
                continue

            details = description.split(": ", 1)[1]

            if " x" not in details:
                continue

            product, quantity_text = details.rsplit(" x", 1)

            try:
                quantity = int(quantity_text)
            except ValueError:
                continue

            if quantity <= 0 or not product.strip():
                continue

            product = product.strip()

            if product not in product_stats:
                product_stats[product] = {
                    "product": product,
                    "quantity_sold": 0,
                    "revenue_kes": Decimal("0")
                }

            product_stats[product]["quantity_sold"] += quantity
            product_stats[product]["revenue_kes"] += amount

        ranked_products = sorted(
            product_stats.values(),
            key=lambda p: (
                -p["quantity_sold"],
                -p["revenue_kes"],
                p["product"]
            )
        )

        products = [
            {
                "product": p["product"],
                "quantity_sold": p["quantity_sold"],
                "revenue_kes": str(p["revenue_kes"])
            }
            for p in ranked_products
        ]

        return JsonResponse({
            "status": "success",
            "business_id": business_id,
            "total_sales_kes": str(total_sales),
            "total_orders": total_orders,
            "average_order_value_kes": str(
                average_order.quantize(Decimal("0.01"))
            ),
            "best_selling_product": (
                ranked_products[0]["product"]
                if ranked_products else None
            ),
            "products": products
        })

    except Exception:
        return JsonResponse(
            {"error": "Unable to calculate sales analytics."},
            status=500
        )


@require_GET
def daily_sales(request):
    """Return daily sales trends from Supabase PostgreSQL."""

    if not local_demo_only(request):
        return JsonResponse(
            {"error": "Local development only"},
            status=403
        )

    business_id = 1

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (transaction_date AT TIME ZONE 'Africa/Nairobi')::date
                        AS sale_date,
                    COUNT(*) AS total_orders,
                    SUM(amount) AS total_sales
                FROM transactions
                WHERE business_id = %s
                  AND transaction_type = %s
                GROUP BY sale_date
                ORDER BY sale_date ASC
                """,
                [business_id, "sale"]
            )

            rows = cursor.fetchall()

        daily_data = [
            {
                "date": str(row[0]),
                "total_orders": row[1],
                "total_sales_kes": str(row[2])
            }
            for row in rows
        ]

        total_sales = sum(
            (row[2] for row in rows),
            Decimal("0")
        )

        highest_day = (
            max(daily_data, key=lambda day: Decimal(day["total_sales_kes"]))
            if daily_data else None
        )

        return JsonResponse({
            "status": "success",
            "business_id": business_id,
            "timezone": "Africa/Nairobi",
            "days_recorded": len(daily_data),
            "total_sales_kes": str(total_sales),
            "highest_sales_day": highest_day,
            "daily_sales": daily_data
        })

    except Exception:
        return JsonResponse(
            {"error": "Unable to retrieve daily sales trends."},
            status=500
        )
