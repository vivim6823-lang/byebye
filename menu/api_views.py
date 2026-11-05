from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.pagination import BasePagination
from rest_framework.response import Response

from .models import Categoria, Produto
from .serializers import CategorySerializer, ProductSerializer


class MenuApiError(APIException):
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        super().__init__({"error": message})


def _positive_int(value, name):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise MenuApiError(f"{name} deve ser um número inteiro positivo.")
    if number < 1:
        raise MenuApiError(f"{name} deve ser um número inteiro positivo.")
    return number


class MenuPagination(BasePagination):
    page_size = 50
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_number = _positive_int(request.query_params.get("page", "1"), "page")
        page_size = _positive_int(
            request.query_params.get("page_size", str(self.page_size)), "page_size"
        )
        if page_size > self.max_page_size:
            raise MenuApiError("page_size não pode ser maior que 100.")

        paginator = Paginator(queryset, page_size)
        try:
            self.page = paginator.page(page_number)
        except EmptyPage:
            raise MenuApiError(
                "A página solicitada não existe.", status.HTTP_404_NOT_FOUND
            )

        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": (
                    self.page.next_page_number() if self.page.has_next() else None
                ),
                "previous": (
                    self.page.previous_page_number()
                    if self.page.has_previous()
                    else None
                ),
                "results": data,
            }
        )


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Categoria.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": len(serializer.data), "results": serializer.data})


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = MenuPagination

    def get_queryset(self):
        queryset = Produto.objects.select_related("categoria").filter(
            categoria__is_active=True
        )
        if self.action != "list":
            return queryset

        category_id = self.request.query_params.get("category_id")
        if category_id is not None:
            queryset = queryset.filter(
                categoria_id=_positive_int(category_id, "category_id")
            )

        available = self.request.query_params.get("available")
        if available is not None:
            normalized = available.strip().lower()
            if normalized not in {"true", "false"}:
                raise MenuApiError("available deve ser 'true' ou 'false'.")
            queryset = queryset.filter(disponivel=(normalized == "true"))

        search = self.request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | Q(descricao__icontains=search)
            )

        return queryset
