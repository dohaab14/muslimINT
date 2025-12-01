from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

from django.db import models
from django.utils.text import slugify

class Book(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def borrow(self, quantity=1):
        if self.available_copies >= quantity:
            self.available_copies -= quantity
            self.save()
            return True
        return False

    def return_copy(self, quantity=1):
        self.available_copies += quantity
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        self.save()

class BorrowerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Loan(models.Model):
    STATUS_CHOICES = (
        ('ongoing', 'En cours'),
        ('returned', 'Rendu'),
        ('overdue', 'En retard'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')

    class Meta:
        ordering = ['-borrowed_at']

    def mark_returned(self):
        if self.status != 'returned':
            self.status = 'returned'
            self.returned_at = timezone.now()
            self.book.return_copy(self.quantity)
            self.save()
