from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Author, Category, Book, BorrowerProfile, Loan

# Profile inline for user
class BorrowerProfileInline(admin.StackedInline):
    model = BorrowerProfile
    can_delete = False
    extra = 0

class UserAdmin(BaseUserAdmin):
    inlines = [BorrowerProfileInline]
    list_display = BaseUserAdmin.list_display + ('active_loans_count',)

    def active_loans_count(self, obj):
        count = Loan.objects.filter(borrower=obj, status='ongoing').count()
        if count > 0:
            return format_html(
                '<span style="color: orange; font-weight: bold;">📚 {}</span>',
                count
            )
        return '—'
    active_loans_count.short_description = "Emprunts actifs"

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return super().get_readonly_fields(request, obj)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return super().has_delete_permission(request, obj)


# Unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'book_count')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    
    def book_count(self, obj):
        count = Book.objects.filter(author__icontains=f"{obj.first_name} {obj.last_name}").count()
        if count > 0:
            return format_html('<span style="color: green;">📚 {}</span>', count)
        return '0'
    book_count.short_description = "Nombre de livres"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def book_count(self, obj):
        count = obj.books.count()
        if count > 0:
            return format_html('<span style="color: green;">📚 {}</span>', count)
        return '0'
    book_count.short_description = "Nombre de livres"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'availability_status',
        'total_copies',
        'available_copies',
        'isbn'
    )
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('📖 Informations générales', {
            'fields': ('title', 'slug', 'author', 'category', 'description', 'isbn')
        }),
        ('📊 Gestion des exemplaires', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('🌙 Avis spirituel', {
            'fields': ('spiritual_review',),
            'classes': ('collapse',),
            'description': 'Avis et recommandations du pôle spiritualité'
        }),
        ('🕐 Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def availability_status(self, obj):
        if obj.available_copies > 0:
            return format_html(
                '<span style="background: #d1fae5; color: #065f46; padding: 4px 10px; border-radius: 12px; font-weight: bold;">✓ {} dispo</span>',
                obj.available_copies
            )
        else:
            return format_html(
                '<span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 12px; font-weight: bold;">✗ Indisponible</span>'
            )
    availability_status.short_description = "Disponibilité"
    
    actions = ['mark_as_unavailable', 'add_copy', 'remove_copy']
    
    def mark_as_unavailable(self, request, queryset):
        for book in queryset:
            book.available_copies = 0
            book.save()
        self.message_user(request, f"✓ {queryset.count()} livre(s) marqué(s) comme indisponible(s).")
    mark_as_unavailable.short_description = "❌ Marquer comme indisponible"
    
    def add_copy(self, request, queryset):
        for book in queryset:
            book.total_copies += 1
            book.available_copies += 1
            book.save()
        self.message_user(request, f"✓ Un exemplaire ajouté à {queryset.count()} livre(s).")
    add_copy.short_description = "➕ Ajouter un exemplaire"
    
    def remove_copy(self, request, queryset):
        for book in queryset:
            if book.total_copies > 0:
                book.total_copies -= 1
                if book.available_copies > 0:
                    book.available_copies -= 1
                book.save()
        self.message_user(request, f"✓ Un exemplaire retiré de {queryset.count()} livre(s).")
    remove_copy.short_description = "➖ Retirer un exemplaire"


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'book',
        'borrower',
        'quantity',
        'borrowed_at_formatted',
        'due_date_formatted',
        'status_badge',
        'days_info'
    )
    list_filter = ('status', 'borrowed_at', 'due_date')
    search_fields = ('book__title', 'borrower__username', 'borrower__first_name', 'borrower__last_name')
    readonly_fields = ('borrowed_at', 'returned_at')
    date_hierarchy = 'borrowed_at'
    
    fieldsets = (
        ('📚 Informations de l\'emprunt', {
            'fields': ('book', 'borrower', 'quantity', 'status')
        }),
        ('📅 Dates', {
            'fields': ('borrowed_at', 'due_date', 'returned_at')
        }),
        ('📝 Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def borrowed_at_formatted(self, obj):
        return obj.borrowed_at.strftime('%d/%m/%Y')
    borrowed_at_formatted.short_description = "Date d'emprunt"
    borrowed_at_formatted.admin_order_field = 'borrowed_at'
    
    def due_date_formatted(self, obj):
        return obj.due_date.strftime('%d/%m/%Y')
    due_date_formatted.short_description = "Date limite"
    due_date_formatted.admin_order_field = 'due_date'
    
    def status_badge(self, obj):
        badges = {
            'ongoing': ('<span style="background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 12px; font-weight: bold;">📖 En cours</span>'),
            'returned': ('<span style="background: #d1fae5; color: #065f46; padding: 4px 10px; border-radius: 12px; font-weight: bold;">✓ Rendu</span>'),
            'overdue': ('<span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 12px; font-weight: bold;">⚠️ En retard</span>')
        }
        return format_html(badges.get(obj.status, obj.get_status_display()))
    status_badge.short_description = "Statut"
    
    def days_info(self, obj):
        if obj.status == 'returned':
            return format_html('<span style="color: green;">✓ Rendu</span>')
        
        now = timezone.now()
        if obj.due_date < now:
            delta = now - obj.due_date
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {} jour(s) de retard</span>',
                delta.days
            )
        else:
            delta = obj.due_date - now
            if delta.days <= 3:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⏰ {} jour(s) restant(s)</span>',
                    delta.days
                )
            return format_html(
                '<span style="color: green;">⏱️ {} jour(s) restant(s)</span>',
                delta.days
            )
    days_info.short_description = "Délai"
    
    actions = ['mark_as_returned', 'extend_due_date_7days', 'extend_due_date_14days']
    
    def mark_as_returned(self, request, queryset):
        count = 0
        for loan in queryset:
            if loan.status != 'returned':
                loan.mark_returned()
                count += 1
        self.message_user(request, f"✓ {count} emprunt(s) marqué(s) comme rendu(s).")
    mark_as_returned.short_description = "✓ Marquer comme rendu"
    
    def extend_due_date_7days(self, request, queryset):
        from datetime import timedelta
        count = 0
        for loan in queryset:
            if loan.status == 'ongoing':
                loan.due_date = loan.due_date + timedelta(days=7)
                loan.save()
                count += 1
        self.message_user(request, f"✓ Date limite prolongée de 7 jours pour {count} emprunt(s).")
    extend_due_date_7days.short_description = "📅 Prolonger de 7 jours"
    
    def extend_due_date_14days(self, request, queryset):
        from datetime import timedelta
        count = 0
        for loan in queryset:
            if loan.status == 'ongoing':
                loan.due_date = loan.due_date + timedelta(days=14)
                loan.save()
                count += 1
        self.message_user(request, f"✓ Date limite prolongée de 14 jours pour {count} emprunt(s).")
    extend_due_date_14days.short_description = "📅 Prolonger de 14 jours"


# Personnalisation du titre de l'admin
admin.site.site_header = "📚 Administration MuslimINT"
admin.site.site_title = "MuslimINT Admin"
admin.site.index_title = "Gestion de la bibliothèque"