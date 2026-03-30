from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Book

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    email = forms.EmailField(
        label="Adresse e-mail académique",
        help_text="Utilisez uniquement une adresse e-mail se terminant par @telecom-sudparis.eu ou @imt-bs.eu."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ['@telecom-sudparis.eu', '@imt-bs.eu']
        if not any(email.endswith(domain) for domain in allowed_domains):
            raise ValidationError("L'adresse e-mail doit appartenir à @telecom-sudparis.eu ou @imt-bs.eu.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        
class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Utilisez votre adresse @telecom-sudparis.eu ou @imt-bs.eu")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        allowed_domains = ['telecom-sudparis.eu', 'imt-bs.eu']
        domain = email.split('@')[-1]
        
        if domain not in allowed_domains:
            raise ValidationError("Désolé, vous devez utiliser une adresse mail de l'école (TSP ou IMT BS).")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'description','spiritual_review', 'isbn', 'total_copies', 'available_copies', 'edition', 'cover_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # On ajoute la classe 'form-control' à chaque champ
            field.widget.attrs['class'] = 'form-control'
            # On peut aussi ajouter des placeholders personnalisés
            field.widget.attrs['placeholder'] = f"Entrez le/la {field.label.lower()}"
        self.fields['spiritual_review'].widget.attrs['rows'] = 4
        self.fields['description'].widget.attrs['rows'] = 5