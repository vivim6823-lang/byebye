from rest_framework.routers import SimpleRouter

from .api_views import CategoryViewSet, ProductViewSet

router = SimpleRouter()
router.register("categories", CategoryViewSet, basename="api-categories")
router.register("products", ProductViewSet, basename="api-products")

urlpatterns = router.urls
