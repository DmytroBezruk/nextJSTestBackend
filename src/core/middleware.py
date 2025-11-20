from django.http import HttpResponseRedirect
from django.urls import reverse
from .user_context import set_current_user, clear_current_user
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication

__all__ = [
    "is_restricted_internal_url",
    "login_required_middleware",
    "CurrentUserMiddleware",
]


def is_restricted_internal_url(url):
    URL_PREFIXES_EXCLUDES = [
        # '/media/',
        "/__debug__/",
        "/login/",
        "/register/",
        "/logout/",
        "/password-",
        "/reset/",
        "/superadmin/",
    ]
    return not max([url.startswith(x) for x in URL_PREFIXES_EXCLUDES])


def login_required_middleware(get_response):
    def middleware(request):
        assert hasattr(request, "user")
        if not request.user.is_authenticated:
            if is_restricted_internal_url(request.path_info):
                return HttpResponseRedirect(reverse("login"))

        response = get_response(request)
        return response

    return middleware


def CurrentUserMiddleware(get_response):
    def middleware(request):
        # Attempt JWT auth early if still anonymous (SimpleJWT runs inside DRF view normally)
        if isinstance(getattr(request, "user", None), AnonymousUser):
            auth = JWTAuthentication()
            try:
                auth_result = auth.authenticate(request)
            except Exception:
                auth_result = None
            if auth_result is not None:
                user, _ = auth_result
                request.user = user
        set_current_user(getattr(request, "user", None))
        try:
            response = get_response(request)
        finally:
            clear_current_user()
        return response

    return middleware
