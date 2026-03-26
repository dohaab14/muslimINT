from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'library'

urlpatterns = [
    # Authentification
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Reset mot de passe
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='library/password_reset.html',
        email_template_name='library/password_reset_email.html',
        subject_template_name='library/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='library/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='library/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='library/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Pages publiques
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<slug:slug>/borrow/', views.borrow_book, name='borrow_book'),
    
    # Espace utilisateur
    path('my-loans/', views.my_loans, name='my_loans'),
    path('loan/<int:loan_id>/return/', views.return_book, name='return_book'),
    path('profile/', views.profile, name='profile'),
    
    # Gestion staff (superuser uniquement)
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('toggle-staff/<int:user_id>/', views.toggle_staff, name='toggle_staff'),
    
    # Espace admin (réservé au bureau de l'association)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-loans/', views.admin_loans, name='admin_loans'),
    path('admin-loans/<int:loan_id>/mark-returned/', views.admin_mark_returned, name='admin_mark_returned'),
    path('admin-loans/<int:loan_id>/extend/', views.admin_extend_loan, name='admin_extend_loan'),
]