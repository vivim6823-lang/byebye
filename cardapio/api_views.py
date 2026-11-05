from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    @action(detail=True, methods=["get"])
    def produtos(self, request, pk=None):
        categoria = self.get_object()
        queryset = Produto.objects.filter(categoria=categoria).select_related(
            "categoria"
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProdutoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProdutoSerializer(queryset, many=True)
        return Response(serializer.data)


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.select_related("categoria").all()
    serializer_class = ProdutoSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("nome",)

    def get_queryset(self):
        queryset = super().get_queryset()
        disponivel = self.request.query_params.get("disponivel")
        if disponivel is not None:
            value = disponivel.strip().lower()
            if value not in {"true", "false"}:
                raise ValidationError(
                    {"disponivel": "Use 'true' ou 'false'."}
                )
            queryset = queryset.filter(disponivel=(value == "true"))
        return queryset
