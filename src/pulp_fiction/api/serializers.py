from rest_framework import serializers

from pulp_fiction.models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name", "details", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class BookSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="author", queryset=Author.objects.all(), write_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ("id", "name", "content", "author", "author_id", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "author")

    def validate(self, attrs):
        # Enforce unique_together validation with a clear error
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
