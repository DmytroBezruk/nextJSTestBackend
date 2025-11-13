from oxygen.api.permissions import (
    AuthenticationBasePermission,
    BaseAPIPermissions,
    IsAuthenticated,
    OxygenBasePermission,
)


class InvoiceBasePermission(OxygenBasePermission):
    permission_name = "GENERAL_INVOICE"


class InvoicePermissions(BaseAPIPermissions):
    base_perms = (
        IsAuthenticated,
        AuthenticationBasePermission,
        InvoiceBasePermission,
    )
    perms_map = {
        "create": base_perms,
        "list": base_perms,
        "retrieve": base_perms,
        "update": base_perms,
        "partial_update": base_perms,
        "destroy": base_perms,
        "save_as_draft": base_perms,
        "reminders_schedule": base_perms,
    }
