from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
