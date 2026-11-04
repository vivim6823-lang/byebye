from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("nome", max_length=100, unique=True)
    description = models.TextField("descrição", blank=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoria",
    )
    name = models.CharField("nome", max_length=120)
    description = models.TextField("descrição", blank=True)
    price = models.DecimalField(
        "preço",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_available = models.BooleanField("disponível", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["category__name", "name"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.name
