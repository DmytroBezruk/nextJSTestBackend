from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from pulp_fiction.models import Author, Book


class AuthorBookAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="apitester@example.com", password="testpass123", name="API Tester")
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Stephen King", details="Famous horror author")
        self.book = Book.objects.create(name="It", author=self.author, content="Scary clown novel")

    def test_list_authors(self):
        url = reverse("pulp_fiction_api:author-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], self.author.name)

    def test_create_author(self):
        url = reverse("pulp_fiction_api:author-list")
        data = {"name": "J. R. R. Tolkien", "details": "Fantasy author"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], data["name"])

    def test_list_books(self):
        url = reverse("pulp_fiction_api:book-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], self.book.name)

    def test_create_book(self):
        url = reverse("pulp_fiction_api:book-list")
        data = {"name": "The Shining", "content": "Overlook Hotel.", "author_id": self.author.id}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], data["name"])
        self.assertEqual(resp.data["author"]["id"], self.author.id)

    def test_unique_book_author_constraint(self):
        url = reverse("pulp_fiction_api:book-list")
        data = {"name": "It", "author_id": self.author.id}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_books_by_author(self):
        url = reverse("pulp_fiction_api:book-list") + f"?author={self.author.id}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["author"]["id"], self.author.id)

