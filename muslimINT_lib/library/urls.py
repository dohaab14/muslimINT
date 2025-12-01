from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Authentification
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Pages publiques
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<slug:slug>/borrow/', views.borrow_book, name='borrow_book'),
    
    # Espace utilisateur
    path('my-loans/', views.my_loans, name='my_loans'),
    path('loan/<int:loan_id>/return/', views.return_book, name='return_book'),
    
    # Espace admin (réservé au bureau de l'association)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-loans/', views.admin_loans, name='admin_loans'),
    path('admin-loans/<int:loan_id>/mark-returned/', views.admin_mark_returned, name='admin_mark_returned'),
    path('admin-loans/<int:loan_id>/extend/', views.admin_extend_loan, name='admin_extend_loan'),
]