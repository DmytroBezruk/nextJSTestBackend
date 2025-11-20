from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import UserReferenceMixin


class Author(UserReferenceMixin, models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    details = models.TextField(_("Details"), blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    image = models.ImageField(_("Image"), upload_to="images/author/", null=True, blank=True)

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(UserReferenceMixin, models.Model):
    name = models.CharField(_("Name"), max_length=255)
    content = models.TextField(_("Content"), blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    image = models.ImageField(_("Image"), upload_to="images/book/", blank=True, null=True)

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        unique_together = ("name", "author")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "author"], name="book_name_author_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.author.name})"
