from django.test import TestCase
from django.contrib.auth import get_user_model
from core.user_context import set_current_user, clear_current_user
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

    def test_auto_population_on_create(self):
        set_current_user(self.user)
        author = Author.objects.create(name="Auto Author")
        clear_current_user()
        self.assertEqual(author.created_by, self.user)
        self.assertEqual(author.updated_by, self.user)

    def test_manual_assignment_still_respected(self):
        other = get_user_model().objects.create_user(email="other@example.com", name="Other User", password="pass5678")
        set_current_user(self.user)
        author = Author(name="Manual Author", created_by=other)
        author.save()
        clear_current_user()
        # created_by should remain the manually assigned one, updated_by set to current thread user
        self.assertEqual(author.created_by, other)
        self.assertEqual(author.updated_by, self.user)

    def test_book_auto_population(self):
        set_current_user(self.user)
        author = Author.objects.create(name="Book Author")
        book = Book.objects.create(name="Book Auto", author=author)
        clear_current_user()
        self.assertEqual(book.created_by, self.user)
        self.assertEqual(book.updated_by, self.user)

    def test_updated_by_changes_on_each_save(self):
        set_current_user(self.user)
        author = Author.objects.create(name="Changing Author")
        clear_current_user()
        other = get_user_model().objects.create_user(email="third@example.com", name="Third User", password="pass9876")
        set_current_user(other)
        author.name = "Changing Author 2"
        author.save()
        clear_current_user()
        self.assertEqual(author.created_by, self.user)
        self.assertEqual(author.updated_by, other)
