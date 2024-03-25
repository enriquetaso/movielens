from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, TagViewSet

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = router.urls
