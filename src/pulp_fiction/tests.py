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

    def test_for_current_user_queryset(self):
        a1 = Author.objects.create(name="Scoped A1", created_by=self.user, updated_by=self.user)
        other = get_user_model().objects.create_user(email="diff@example.com", name="Diff User", password="pass")
        Author.objects.create(name="Scoped A2", created_by=other, updated_by=other)
        set_current_user(self.user)
        qs = Author.for_current_user()
        clear_current_user()
        self.assertEqual(list(qs), [a1])

    def test_get_for_current_user_success(self):
        a1 = Author.objects.create(name="GetMe", created_by=self.user, updated_by=self.user)
        set_current_user(self.user)
        obj = Author.get_for_current_user(name="GetMe")
        clear_current_user()
        self.assertEqual(obj, a1)

    def test_get_for_current_user_not_found(self):
        Author.objects.create(name="NotMine", created_by=self.user, updated_by=self.user)
        other = get_user_model().objects.create_user(email="otherq@example.com", name="Other Q", password="pass")
        Author.objects.create(name="OtherUserAuthor", created_by=other, updated_by=other)
        set_current_user(self.user)
        with self.assertRaises(Author.DoesNotExist):
            Author.get_for_current_user(name="OtherUserAuthor")
        clear_current_user()

    def test_scoped_manager_objects(self):
        other = get_user_model().objects.create_user(email="other-scope@example.com", name="Other Scope", password="pass")
        set_current_user(self.user)
        a1 = Author.objects.create(name="Mine 1")
        clear_current_user()
        set_current_user(other)
        Author.objects.create(name="Theirs 1")
        clear_current_user()
        set_current_user(self.user)
        mine_qs = Author.objects.all()  # should only show current user's author(s)
        clear_current_user()
        self.assertEqual(list(mine_qs), [a1])

    def test_unscoped_all_objects(self):
        other = get_user_model().objects.create_user(email="other-all@example.com", name="Other All", password="pass")
        set_current_user(self.user)
        a1 = Author.objects.create(name="Mine Unscoped")
        clear_current_user()
        set_current_user(other)
        a2 = Author.objects.create(name="Other Unscoped")
        clear_current_user()
        all_qs = Author.all_objects.all()
        self.assertCountEqual(list(all_qs), [a1, a2])
