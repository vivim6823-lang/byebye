from rest_framework import serializers

from .models import Categoria, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ("id", "nome", "descricao", "is_active")
        read_only_fields = ("id",)


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)

    class Meta:
        model = Produto
        fields = (
            "id",
            "nome",
            "descricao",
            "preco",
            "disponivel",
            "categoria",
            "categoria_nome",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "categoria_nome", "created_at", "updated_at")

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value
