from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from .user_context import get_current_user
except Exception:
    def get_current_user():  # fallback if import fails
        return None


class UserReferenceMixin(models.Model):
    """Abstract mixin that adds user reference fields for auditing.

    Fields:
        created_by: Optional FK to the user who initially created the object.

    Notes:
        - related_name patterns use the model class name for clarity.
        - Population of these fields should be handled in forms, serializers,
          admin save_model overrides, or dedicated middleware capturing the
          acting user. This mixin purposefully does not attempt implicit
          assignment to avoid hidden dependencies on request-thread globals.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name=_("Created by"),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            if not self.pk and not self.created_by:
                self.created_by = current_user
        super().save(*args, **kwargs)


class UserScopedQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = get_current_user()
        if not user or not user.is_authenticated:
            return qs.none()
        return qs.filter(created_by=user)
