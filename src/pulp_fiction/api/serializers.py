from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from pulp_fiction.models import Author, Book


@extend_schema_field(OpenApiTypes.BINARY)
class UploadImageField(serializers.ImageField):
    """ImageField that forces OpenAPI spec to render as a binary/file input."""
    pass


class AuthorSerializer(serializers.ModelSerializer):
    image = UploadImageField(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Author
        fields = ("id", "name", "details", "image", "image_url", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "image", "image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class AuthorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating Author instances including image upload.
    Use this for request bodies (multipart/form-data) while responding with AuthorSerializer.
    """
    image = UploadImageField(required=False, allow_null=True)

    class Meta:
        model = Author
        fields = ("name", "details", "image")


class BookSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="author", queryset=Author.objects.all(), write_only=True)
    author = AuthorSerializer(read_only=True)
    image = UploadImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Book
        fields = ("id", "name", "content", "image", "image_url", "author", "author_id", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "author", "image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate(self, attrs):
        # Enforce unique_together validation with a clear error
        author = attrs.get("author") or self.instance and self.instance.author
        name = attrs.get("name") or self.instance and self.instance.name
        if author and name and Book.objects.filter(author=author, name=name).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError({"non_field_errors": ["Book with this Name and Author already exists."]})
        return attrs


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer used for create/update operations with multipart form including image."""
    author_id = serializers.PrimaryKeyRelatedField(source="author", queryset=Author.objects.all())
    image = UploadImageField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = ("name", "content", "image", "author_id")

    def validate(self, attrs):
        author = attrs.get("author") or self.instance and self.instance.author
        name = attrs.get("name") or self.instance and self.instance.name
        if author and name and Book.objects.filter(author=author, name=name).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError({"non_field_errors": ["Book with this Name and Author already exists."]})
        return attrs


class MonthBucketSerializer(serializers.Serializer):
    label = serializers.CharField()
    books = serializers.IntegerField()
    authors = serializers.IntegerField()


class AnalyticsSerializer(serializers.Serializer):
    totalBooks = serializers.IntegerField()
    totalAuthors = serializers.IntegerField()
    newBooksLast30 = serializers.IntegerField()
    newAuthorsLast30 = serializers.IntegerField()
    booksGrowthPct = serializers.FloatField()
    authorsGrowthPct = serializers.FloatField()
    buckets = MonthBucketSerializer(many=True)
