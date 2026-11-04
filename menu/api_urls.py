from django.urls import path

from . import api_views

urlpatterns = [
    path("categories/", api_views.categories, name="api-categories"),
    path("products/", api_views.products, name="api-products"),
    path("products/<int:product_id>/", api_views.product_detail, name="api-product-detail"),
]
