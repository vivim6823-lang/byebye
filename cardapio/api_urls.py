from rest_framework.routers import DefaultRouter

from .api_views import CategoriaViewSet, ProdutoViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("produtos", ProdutoViewSet, basename="produto")

urlpatterns = router.urls
