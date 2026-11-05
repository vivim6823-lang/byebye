from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField("nome", max_length=100, unique=True)
    descricao = models.TextField("descrição", blank=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="categoria",
    )
    nome = models.CharField("nome", max_length=150)
    descricao = models.TextField("descrição", blank=True)
    preco = models.DecimalField(
        "preço",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    disponivel = models.BooleanField("disponível", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["categoria__nome", "nome"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.nome
