
from django.urls import path
from . import views

urlpatterns = [
    path(
        "upload/",
        views.upload_file,
        name="upload_file"
    ),
    path(
        "transactions/",
        views.get_transactions,
        name="get_transactions"
    ),
    path(
        "analytics/",
        views.sales_analytics,
        name="sales_analytics"
    ),
]
