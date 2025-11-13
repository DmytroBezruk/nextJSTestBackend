from django.urls import include, path

from .api import router as api_router

urlpatterns = [
    path("api/", include((api_router.api_urlpatterns, "pulp_fiction_api"), namespace="pulp_fiction_api")),
]

