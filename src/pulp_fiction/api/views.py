from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from core.user_context import get_current_user
from pulp_fiction.models import Author, Book

from .serializers import (
    AuthorSerializer,
    BookSerializer,
    AnalyticsSerializer,
    AuthorCreateSerializer,
    BookCreateUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(responses=AuthorSerializer),
    retrieve=extend_schema(responses=AuthorSerializer),
    create=extend_schema(
        request=AuthorCreateSerializer,
        responses=AuthorSerializer,
        description="Create an author (multipart/form-data with optional image)",
    ),
    update=extend_schema(
        request=AuthorCreateSerializer,
        responses=AuthorSerializer,
        description="Update an author (multipart/form-data with optional image)",
    ),
    partial_update=extend_schema(
        request=AuthorCreateSerializer,
        responses=AuthorSerializer,
        description="Partially update an author (multipart/form-data with optional image)",
    ),
    destroy=extend_schema(responses=None),
)
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.filter(created_by=get_current_user())
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return AuthorCreateSerializer
        return AuthorSerializer

    def get_parser_classes(self):  # drf-spectacular will inspect this per action
        if self.action in {"create", "update", "partial_update"}:
            return [MultiPartParser, FormParser]  # limit to multipart/form-data for write operations
        return [JSONParser]

    @extend_schema(
        responses=AuthorSerializer(many=True),
        description="Return all authors without pagination."
    )
    @action(detail=False, methods=["get"], pagination_class=None)
    def all(self, request):
        authors = self.get_queryset()
        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(responses=BookSerializer),
    retrieve=extend_schema(responses=BookSerializer),
    create=extend_schema(
        request=BookCreateUpdateSerializer,
        responses=BookSerializer,
        description="Create a book (multipart/form-data, include image and author_id).",
    ),
    update=extend_schema(
        request=BookCreateUpdateSerializer,
        responses=BookSerializer,
        description="Update a book (multipart/form-data, include image and author_id).",
    ),
    partial_update=extend_schema(
        request=BookCreateUpdateSerializer,
        responses=BookSerializer,
        description="Partially update a book (multipart/form-data).",
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").filter(created_by=get_current_user())
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return BookCreateUpdateSerializer
        return BookSerializer

    def get_parser_classes(self):
        if self.action in {"create", "update", "partial_update"}:
            return [MultiPartParser, FormParser]
        return [JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        author_id = self.request.query_params.get("author")
        if author_id:
            qs = qs.filter(author_id=author_id)
        return qs


@extend_schema_view(
    list=extend_schema(responses=AnalyticsSerializer),
)
class AnalyticsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        now = timezone.now()
        last30 = now - timezone.timedelta(days=30)
        prev30_start = now - timezone.timedelta(days=60)
        prev30_end = last30

        user = get_current_user()

        user_filter = {"created_by": user} if user else {}

        # Totals
        total_books = Book.objects.filter(**user_filter).count()
        total_authors = Author.objects.filter(**user_filter).count()

        # New entities
        new_books_last30 = Book.objects.filter(created_at__gte=last30, **user_filter).count()
        new_books_prev30 = Book.objects.filter(created_at__gte=prev30_start, created_at__lt=prev30_end, **user_filter).count()
        new_authors_last30 = Author.objects.filter(created_at__gte=last30, **user_filter).count()
        new_authors_prev30 = Author.objects.filter(created_at__gte=prev30_start, created_at__lt=prev30_end, **user_filter).count()

        def pct_change(current: int, prev: int) -> float:
            if prev == 0:
                return 0.0 if current == 0 else 100.0
            return ((current - prev) / prev) * 100.0

        books_growth_pct = pct_change(new_books_last30, new_books_prev30)
        authors_growth_pct = pct_change(new_authors_last30, new_authors_prev30)

        # Helper to shift months like JS new Date(year, month - i, 1)
        def shift_month(dt: timezone.datetime, offset: int) -> timezone.datetime:
            base_month = dt.month - 1
            total = base_month + offset
            year = dt.year + total // 12
            month = total % 12 + 1
            return timezone.datetime(year=year, month=month, day=1, tzinfo=dt.tzinfo)

        # Determine earliest bucket's first day
        current_month_start = timezone.datetime(year=now.year, month=now.month, day=1, tzinfo=now.tzinfo)
        start_month = shift_month(current_month_start, -5)

        # Aggregate per month using TruncMonth
        book_months = (
            Book.objects.filter(created_at__gte=start_month, **user_filter)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        author_months = (
            Author.objects.filter(created_at__gte=start_month, **user_filter)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        # Build a dict for quick lookup
        books_by_month = {bm["month"].date(): bm["count"] for bm in book_months}
        authors_by_month = {am["month"].date(): am["count"] for am in author_months}

        # Prepare labels and ensure 6 buckets (including current month)
        buckets = []
        for i in range(5, -1, -1):
            month_dt = shift_month(current_month_start, -i)
            month_key = month_dt.date()
            label = month_dt.strftime("%b")
            buckets.append(
                {
                    "label": label,
                    "books": int(books_by_month.get(month_key, 0)),
                    "authors": int(authors_by_month.get(month_key, 0)),
                }
            )

        payload = {
            "totalBooks": int(total_books),
            "totalAuthors": int(total_authors),
            "newBooksLast30": int(new_books_last30),
            "newAuthorsLast30": int(new_authors_last30),
            "booksGrowthPct": float(books_growth_pct),
            "authorsGrowthPct": float(authors_growth_pct),
            "buckets": buckets,
        }

        serializer = AnalyticsSerializer(payload)
        return Response(serializer.data)
