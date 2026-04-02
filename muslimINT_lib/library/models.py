from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Author(models.Model):
    """Modèle pour les auteurs"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, help_text="Biographie de l'auteur")
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Auteur"
        verbose_name_plural = "Auteurs"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    """Modèle pour les catégories de livres"""

    RELIGIOUS_CHOICES = [
        ('coran', 'Coran et Sciences du Coran'),
        ('hadith', 'Hadith'),
        ('aqida', 'Aqida (Dogme)'),
        ('fiqh', 'Fiqh (Jurisprudence)'),
        ('siras', 'Siras (Vie des Prophètes)'),
        ('histoires', 'Histoires Islamique'),
        ('spiritualite', 'Spiritualité (Tazkiya)'),
        ('langue_arabe', 'Langue Arabe'),
        ('education', 'Éducation et Famille'),
        ('pensee', 'Pensée Islamique'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom interne"
    )
    display_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom affiché"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de la catégorie"
    )
    slug = models.SlugField(
        max_length=500,
        unique=True,
        blank=True
    )
    is_predefined = models.BooleanField(
        default=False,
        verbose_name="Catégorie par défaut"
    )

    class Meta:
        ordering = ['display_name', 'name']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.display_name or self.name

    def save(self, *args, **kwargs):
        if not self.display_name:
            predefined_map = dict(self.RELIGIOUS_CHOICES)
            self.display_name = predefined_map.get(self.name, self.name)

        if not self.slug:
            self.slug = slugify(self.display_name or self.name)

        super().save(*args, **kwargs)

class Book(models.Model):
    """Modèle pour les livres"""
    title = models.CharField(max_length=300, verbose_name="Titre")
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    author = models.CharField(max_length=200, blank=True, verbose_name="Auteur")
    edition = models.CharField(max_length=200, blank=True, verbose_name="Édition / Maison d'édition")
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='books',
        verbose_name="Catégorie"
    )
    
    description = models.TextField(blank=True, verbose_name="Description")
    isbn = models.CharField(max_length=20, blank=True, verbose_name="ISBN")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="Image de couverture")
    
    # Gestion des exemplaires
    total_copies = models.PositiveIntegerField(default=1, verbose_name="Nombre total d'exemplaires")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Exemplaires disponibles")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    # Avis du pôle spiritualité (Phase 2)
    spiritual_review = models.TextField(
        blank=True, 
        help_text="Avis du pôle spiritualité sur ce livre",
        verbose_name="Avis spirituel"
    )
    
    class Meta:
        ordering = ['title']
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def borrow(self, quantity=1):
        """Emprunter un ou plusieurs exemplaires"""
        if self.available_copies >= quantity:
            self.available_copies -= quantity
            self.save()
            return True
        return False
    
    def return_copy(self, quantity=1):
        """Retourner un ou plusieurs exemplaires"""
        self.available_copies += quantity
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        self.save()
    
    @property
    def is_available(self):
        """Vérifier si le livre est disponible"""
        return self.available_copies > 0



class BorrowerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Profil emprunteur"
        verbose_name_plural = "Profils emprunteurs"
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Loan(models.Model):
    """Modèle pour les emprunts"""
    STATUS_CHOICES = (
        ('ongoing', 'En cours'),
        ('returned', 'Rendu'),
        ('overdue', 'En retard'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    
    # Dates
    borrowed_at = models.DateTimeField(default=timezone.now, verbose_name="Date d'emprunt")
    due_date = models.DateTimeField(verbose_name="Date limite de retour")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de retour")
     
    # Statut
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ongoing',
        verbose_name="Statut"
    )
    
    # Notes (optionnel pour Phase 2)
    notes = models.TextField(blank=True, help_text="Notes ou remarques sur l'emprunt")
    reminder_sent = models.BooleanField(default=False)
    overdue_email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-borrowed_at']
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
    
    def __str__(self):
        return f"{self.borrower.username} - {self.book.title}"
    
    def mark_returned(self):
        """Marquer le livre comme rendu"""
        if self.status != 'returned':
            self.status = 'returned'
            self.returned_at = timezone.now()
            self.book.return_copy(self.quantity)
            self.save()
    
    @property
    def is_overdue(self):
        """Vérifier si l'emprunt est en retard"""
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date
    
    @property
    def days_until_due(self):
        """Nombre de jours avant la date limite"""
        if self.status == 'returned':
            return None
        delta = self.due_date - timezone.now()
        return delta.days


# Pour Phase 2 : Système de suggestions de livres
class BookSuggestion(models.Model):
    """Suggestions de livres par les utilisateurs"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    )
    
    suggested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True)
    reason = models.TextField(help_text="Pourquoi suggérer ce livre ?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_suggestions'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Suggestion de livre"
        verbose_name_plural = "Suggestions de livres"
    
    def __str__(self):
        return f"{self.title} (suggéré par {self.suggested_by.username})"