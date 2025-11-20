from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Author, Book


class UserReferenceMixinTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", name="Test User", password="pass1234")

    def test_author_user_reference_fields(self):
        author = Author.objects.create(name="Author Name", created_by=self.user, updated_by=self.user)
        self.assertEqual(author.created_by, self.user)
        self.assertEqual(author.updated_by, self.user)

    def test_book_user_reference_fields(self):
        author = Author.objects.create(name="Another Author")
        book = Book.objects.create(name="Book Title", author=author, created_by=self.user, updated_by=self.user)
        self.assertEqual(book.created_by, self.user)
        self.assertEqual(book.updated_by, self.user)

    def test_admin_like_update_sets_updated_by(self):
        author = Author.objects.create(name="Tmp Author")
        author.updated_by = self.user
        author.save()
        self.assertIsNone(author.created_by)
        self.assertEqual(author.updated_by, self.user)
