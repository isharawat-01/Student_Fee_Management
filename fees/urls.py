
from django.urls import path
from . import views

urlpatterns = [
    path(
        'dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'add-fee/',
        views.add_fee,
        name='add_fee'
    ),

    path(
        'receipt/<int:payment_id>/',
        views.download_receipt,
        name='download_receipt'
    ),

    path(
        'my-receipt/<int:payment_id>/',
        views.student_download_receipt,
        name='student_download_receipt'
    ),
]
