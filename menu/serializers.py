from rest_framework import serializers

from .models import Categoria, Produto


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nome", read_only=True)

    class Meta:
        model = Categoria
        fields = ("id", "name")
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nome", read_only=True)
    description = serializers.CharField(source="descricao", read_only=True)
    price = serializers.DecimalField(
        source="preco", max_digits=8, decimal_places=2, read_only=True
    )
    is_available = serializers.BooleanField(source="disponivel", read_only=True)
    category = CategorySerializer(source="categoria", read_only=True)

    class Meta:
        model = Produto
        fields = (
            "id",
            "name",
            "description",
            "price",
            "is_available",
            "category",
        )
        read_only_fields = fields
