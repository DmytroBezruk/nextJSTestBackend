from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from pulp_fiction.models import Author, Book

from .serializers import AuthorSerializer, BookSerializer


@extend_schema_view(
    list=extend_schema(responses=AuthorSerializer),
    retrieve=extend_schema(responses=AuthorSerializer),
    create=extend_schema(request=AuthorSerializer, responses=AuthorSerializer),
    update=extend_schema(request=AuthorSerializer, responses=AuthorSerializer),
    partial_update=extend_schema(request=AuthorSerializer, responses=AuthorSerializer),
    destroy=extend_schema(responses=None),
)
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"


@extend_schema_view(
    list=extend_schema(responses=BookSerializer),
    retrieve=extend_schema(responses=BookSerializer),
    create=extend_schema(request=BookSerializer, responses=BookSerializer),
    update=extend_schema(request=BookSerializer, responses=BookSerializer),
    partial_update=extend_schema(request=BookSerializer, responses=BookSerializer),
    destroy=extend_schema(responses=None),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        qs = super().get_queryset()
        author_id = self.request.query_params.get("author")
        if author_id:
            qs = qs.filter(author_id=author_id)
        return qs

