from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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