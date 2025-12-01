# Create your views here
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import Book, Loan

class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 10

class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

@login_required
def borrow_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if book.available_copies < 1:
        return render(request, 'library/borrow_confirm.html', {'error': "Aucun exemplaire disponible", 'book': book})

    due = timezone.now() + timedelta(days=14)
    loan = Loan.objects.create(book=book, borrower=request.user, quantity=1, due_date=due)
    book.borrow(1)
    return render(request, 'library/borrow_confirm.html', {'loan': loan, 'book': book})
