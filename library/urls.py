from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_dashboard, name='library_dashboard'),

    path('books/', views.book_list, name='book_list'),

    path('issue/', views.issue_book_view, name='issue_book'),

    path('issued/', views.issued_books, name='issued_books'),

    path(
        'return/<int:issue_id>/',
        views.return_book_view,
        name='return_book'
    ),
    path(
    'pay-fine/<int:issue_id>/',
    views.pay_fine,
    name='pay_fine'
),
]