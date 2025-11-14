from rest_framework.routers import SimpleRouter

from pulp_fiction.api.views import AuthorViewSet, BookViewSet, AnalyticsView

router = SimpleRouter()
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"books", BookViewSet, basename="book")
router.register(r"analytics", AnalyticsView, basename="analytics")

api_urlpatterns = [
    *router.urls,
]
