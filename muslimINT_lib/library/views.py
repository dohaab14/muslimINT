from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from datetime import timedelta
from django.contrib.auth.models import User 
from .models import Book, Loan, BorrowerProfile, Category, Author


# Fonction pour vérifier si l'utilisateur est admin/staff
def is_admin(user):
    return user.is_staff or user.is_superuser


class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.all().select_related()
        
        # Recherche par texte
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(description__icontains=query) |
                Q(isbn__icontains=query)
            )
        
        # Filtre par catégorie
        category = self.request.GET.get('category', '').strip()
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        # Filtre par auteur
        author = self.request.GET.get('author', '').strip()
        if author:
            queryset = queryset.filter(author__icontains=author)
        
        # Filtre par disponibilité
        availability = self.request.GET.get('availability', '')
        if availability == 'available':
            queryset = queryset.filter(available_copies__gt=0)
        elif availability == 'unavailable':
            queryset = queryset.filter(available_copies=0)
        
        # Tri
        sort_by = self.request.GET.get('sort', 'title')
        if sort_by == 'title':
            queryset = queryset.order_by('title')
        elif sort_by == '-title':
            queryset = queryset.order_by('-title')
        elif sort_by == 'author':
            queryset = queryset.order_by('author', 'title')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-id')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('id')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les catégories et auteurs pour les filtres
        context['categories'] = Category.objects.all().order_by('name')
        context['all_authors'] = Book.objects.values_list('author', flat=True).distinct().order_by('author')
        context['all_authors'] = [author for author in context['all_authors'] if author]
        
        # Garder les paramètres de recherche pour la pagination
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_author'] = self.request.GET.get('author', '')
        context['selected_availability'] = self.request.GET.get('availability', '')
        context['selected_sort'] = self.request.GET.get('sort', 'title')
        
        # Stats rapides
        context['total_books'] = Book.objects.count()
        context['available_books'] = Book.objects.filter(available_copies__gt=0).count()
        
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vérifier si l'utilisateur a déjà emprunté ce livre
        if self.request.user.is_authenticated:
            context['user_has_borrowed'] = Loan.objects.filter(
                borrower=self.request.user,
                book=self.object,
                status='ongoing'
            ).exists()
        
        # Emprunts récents pour ce livre
        context['recent_loans'] = Loan.objects.filter(
            book=self.object
        ).select_related('borrower').order_by('-borrowed_at')[:5]
        
        return context


@login_required
def borrow_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    
    # Vérifier si le livre est disponible
    if book.available_copies < 1:
        messages.error(request, f'Le livre "{book.title}" n\'est pas disponible pour le moment.')
        return redirect('library:book_list')
    
    # Vérifier si l'utilisateur a déjà emprunté ce livre (et ne l'a pas rendu)
    existing_loan = Loan.objects.filter(
        borrower=request.user,
        book=book,
        status='ongoing'
    ).first()
    
    if existing_loan:
        messages.warning(request, f'Vous avez déjà emprunté le livre "{book.title}".')
        return redirect('library:my_loans')
    
    # Créer le prêt (durée par défaut : 14 jours)
    due_date = timezone.now() + timedelta(days=14)
    loan = Loan.objects.create(
        book=book,
        borrower=request.user,
        quantity=1,
        due_date=due_date,
        status='ongoing'
    )
    
    # Décrémenter les copies disponibles
    book.borrow(quantity=1)
    
    messages.success(request, f'Vous avez emprunté "{book.title}" avec succès ! À rendre avant le {due_date.strftime("%d/%m/%Y")}.')
    
    return render(request, 'library/borrow_confirm.html', {
        'book': book,
        'loan': loan
    })


@login_required
def my_loans(request):
    now = timezone.now()
    
    # Récupérer tous les emprunts de l'utilisateur
    all_loans = Loan.objects.filter(borrower=request.user).select_related('book')
    
    # Emprunts en cours (non rendus)
    ongoing_loans = all_loans.filter(status='ongoing').order_by('due_date')
    
    # Historique (rendus)
    history_loans = all_loans.filter(status='returned').order_by('-returned_at')
    
    # Calculer les statistiques
    ongoing_count = ongoing_loans.count()
    returned_count = history_loans.count()
    overdue_count = ongoing_loans.filter(due_date__lt=now).count()
    
    # Mettre à jour le statut des emprunts en retard
    for loan in ongoing_loans:
        if loan.due_date < now and loan.status == 'ongoing':
            loan.status = 'overdue'
            loan.save()
    
    context = {
        'ongoing_loans': ongoing_loans,
        'history_loans': history_loans,
        'ongoing_count': ongoing_count,
        'returned_count': returned_count,
        'overdue_count': overdue_count,
        'now': now,
    }
    
    return render(request, 'library/my_loans.html', context)


@login_required
def return_book(request, loan_id):
    """Vue pour marquer un livre comme rendu"""
    loan = get_object_or_404(Loan, id=loan_id, borrower=request.user)
    
    if loan.status == 'returned':
        messages.warning(request, 'Ce livre a déjà été rendu.')
    else:
        loan.mark_returned()
        messages.success(request, f'Le livre "{loan.book.title}" a été marqué comme rendu. Merci !')
    
    return redirect('library:my_loans')


# ===== NOUVELLES VUES ADMIN =====

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Tableau de bord principal pour les admins"""
    now = timezone.now()
    
    # Statistiques globales
    total_books = Book.objects.count()
    total_copies = Book.objects.aggregate(total=Count('total_copies'))['total'] or 0
    available_copies = Book.objects.aggregate(total=Count('available_copies'))['total'] or 0
    
    total_loans = Loan.objects.count()
    ongoing_loans = Loan.objects.filter(status='ongoing').count()
    overdue_loans = Loan.objects.filter(status='ongoing', due_date__lt=now).count()
    
    total_users = User.objects.count()
    active_borrowers = Loan.objects.filter(status='ongoing').values('borrower').distinct().count()
    
    # Emprunts récents
    recent_loans = Loan.objects.select_related('book', 'borrower').order_by('-borrowed_at')[:10]
    
    # Livres les plus empruntés
    popular_books = Book.objects.annotate(
        loan_count=Count('loans')
    ).order_by('-loan_count')[:5]
    
    # Utilisateurs avec emprunts en retard
    overdue_users = Loan.objects.filter(
        status='ongoing',
        due_date__lt=now
    ).select_related('borrower', 'book').order_by('due_date')
    
    context = {
        'total_books': total_books,
        'total_copies': total_copies,
        'available_copies': available_copies,
        'total_loans': total_loans,
        'ongoing_loans': ongoing_loans,
        'overdue_loans': overdue_loans,
        'total_users': total_users,
        'active_borrowers': active_borrowers,
        'recent_loans': recent_loans,
        'popular_books': popular_books,
        'overdue_users': overdue_users,
        'now': now,
    }
    
    return render(request, 'library/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_loans(request):
    """Gestion complète des emprunts"""
    now = timezone.now()
    
    # Filtres
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    loans = Loan.objects.select_related('book', 'borrower', 'borrower__borrowerprofile').all()
    
    # Appliquer les filtres
    if status_filter:
        loans = loans.filter(status=status_filter)
    
    if search_query:
        loans = loans.filter(
            Q(book__title__icontains=search_query) |
            Q(borrower__username__icontains=search_query) |
            Q(borrower__email__icontains=search_query) |
            Q(borrower__first_name__icontains=search_query) |
            Q(borrower__last_name__icontains=search_query)
        )
    
    loans = loans.order_by('-borrowed_at')
    
    context = {
        'loans': loans,
        'status_filter': status_filter,
        'search_query': search_query,
        'now': now,
    }
    
    return render(request, 'library/admin_loans.html', context)


@login_required
@user_passes_test(is_admin)
def admin_mark_returned(request, loan_id):
    """Marquer un emprunt comme rendu (admin)"""
    loan = get_object_or_404(Loan, id=loan_id)
    
    if loan.status != 'returned':
        loan.mark_returned()
        messages.success(request, f'L\'emprunt de "{loan.book.title}" par {loan.borrower.username} a été marqué comme rendu.')
    else:
        messages.info(request, 'Cet emprunt était déjà marqué comme rendu.')
    
    return redirect('library:admin_loans')

# Ajoute ces imports en haut de views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

# Ajoute cette vue à la fin de views.py

def custom_login(request):
    """Page de connexion personnalisée"""
    if request.user.is_authenticated:
        # Si déjà connecté, rediriger selon le rôle
        if request.user.is_staff:
            return redirect('library:admin_dashboard')
        else:
            return redirect('library:my_loans')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} ! 👋')
            
            # Redirection selon le rôle
            if user.is_staff:
                return redirect('library:admin_dashboard')
            else:
                return redirect('library:my_loans')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'library/login.html')


def custom_logout(request):
    """Déconnexion personnalisée"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('library:login')

@login_required
@user_passes_test(is_admin)
def admin_extend_loan(request, loan_id):
    """Prolonger un emprunt (admin)"""
    loan = get_object_or_404(Loan, id=loan_id)
    days = int(request.GET.get('days', 7))
    
    if loan.status == 'ongoing':
        loan.due_date = loan.due_date + timedelta(days=days)
        loan.save()
        messages.success(request, f'L\'emprunt a été prolongé de {days} jours. Nouvelle date limite : {loan.due_date.strftime("%d/%m/%Y")}')
    else:
        messages.warning(request, 'Impossible de prolonger un emprunt déjà rendu.')
    
    return redirect('library:admin_loans')