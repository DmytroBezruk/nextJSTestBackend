from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.user_context import get_current_user


class ScopedQuerySet(models.QuerySet):
    def _with_scope(self):
        user = get_current_user()
        if user and getattr(user, "is_authenticated", False):
            return super().filter(created_by=user)
        return super().none()

    # Automatically scoped .filter()
    def filter(self, *args, **kwargs):
        return self._with_scope().filter(*args, **kwargs)

    # Automatically scoped .get()
    def get(self, *args, **kwargs):
        return self._with_scope().get(*args, **kwargs)

    # Automatically scoped .all()
    def all(self):
        return self._with_scope()



class UserScopedManager(models.Manager):
    def get_queryset(self):
        return ScopedQuerySet(self.model, using=self._db)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def for_user(self, user):
        return self.get_queryset().filter(created_by=user) if user and getattr(user, "is_authenticated", False) else self.get_queryset().none()


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

    # Default user-scoped manager: any Model.objects.* auto-filters by current user.
    objects = UserScopedManager()
    # Unrestricted manager for internal/admin/system usage.
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            if not self.pk and not self.created_by:
                self.created_by = current_user
        super().save(*args, **kwargs)
