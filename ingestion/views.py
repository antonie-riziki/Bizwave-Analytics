
import io
import pandas as pd

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST
def upload_file(request):
    """
    BIZ WAVE - CSV/Excel Data Ingestion API
    Temporary local-development endpoint.
    """

    # Restrict this demo endpoint to local development
    if (
        not settings.DEBUG
        or request.META.get("REMOTE_ADDR") not in ("127.0.0.1", "::1")
    ):
        return JsonResponse(
            {"error": "Local development only"},
            status=403
        )

    # Check whether a file was uploaded
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "Please upload a CSV or Excel file."},
            status=400
        )

    filename = uploaded_file.name.lower()

    # Accept only CSV and Excel files
    if not filename.endswith((".csv", ".xlsx")):
        return JsonResponse(
            {"error": "Only CSV and XLSX files are supported."},
            status=400
        )

    # Limit upload size to 5 MB
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse(
            {"error": "File must be smaller than 5 MB."},
            status=400
        )

    try:
        file_bytes = uploaded_file.read()

        # Read CSV or Excel file
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))

        # Check for empty files
        if df.empty:
            return JsonResponse(
                {"error": "The uploaded file is empty."},
                status=400
            )

        # Check missing values
        missing_values = {
            str(column): int(count)
            for column, count in df.isnull().sum().items()
        }

        # Check duplicate rows
        duplicate_rows = int(df.duplicated().sum())

        # Return file analysis as JSON
        return JsonResponse({
            "status": "success",
            "message": "File processed successfully!",
            "filename": uploaded_file.name,
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "columns": [str(col) for col in df.columns],
            "duplicate_rows": duplicate_rows,
            "missing_values": missing_values
        })

    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unable to process this file. Check its format."
            },
            status=400
        )
