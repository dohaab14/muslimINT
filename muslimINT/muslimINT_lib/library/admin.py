from django.contrib import admin
from .models import Author, Category, Book, BorrowerProfile, Loan
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title','isbn','total_copies','available_copies')
    search_fields = ('title','isbn')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book','borrower','quantity','borrowed_at','due_date','status')
    list_filter = ('status',)
    search_fields = ('book__title','borrower__username')

# profile inline for user
from django.contrib.auth.models import User
from .models import BorrowerProfile
from django.contrib import admin

class BorrowerProfileInline(admin.StackedInline):
    model = BorrowerProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (BorrowerProfileInline,)

# unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'quantity', 'borrowed_at', 'due_date', 'status', 'is_overdue')
    list_filter = ('status',)
    search_fields = ('book__title', 'borrower__username')

    def is_overdue(self, obj):
        return obj.due_date < timezone.now() and obj.status != 'returned'
    is_overdue.boolean = True  
    is_overdue.short_description = 'En retard ?'
