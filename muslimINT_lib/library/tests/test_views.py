
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Loan

class LibraryViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Test Book', available_copies=1)

    def test_borrow_book(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('library:borrow_book', args=[self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vous avez emprunté')

    def test_login(self):
        response = self.client.post(reverse('library:login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion