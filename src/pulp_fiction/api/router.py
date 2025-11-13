from django.urls import path
from rest_framework.routers import SimpleRouter

from pulp_fiction.api.views import AuthorViewSet, BookViewSet

router = SimpleRouter()
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"books", BookViewSet, basename="book")

api_urlpatterns = [
    *router.urls,
]

