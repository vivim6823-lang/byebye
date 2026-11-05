from django.contrib import admin

from .models import Categoria, Produto


admin.site.site_header = "Administração do cardápio"
admin.site.site_title = "Cardápio"
admin.site.index_title = "Gerenciamento do cardápio"


@admin.register(Categoria)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nome", "is_active")
    list_filter = ("is_active",)
    search_fields = ("nome", "descricao")
    list_editable = ("is_active",)


@admin.register(Produto)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "preco", "disponivel", "updated_at")
    list_filter = ("categoria", "disponivel")
    search_fields = ("nome", "descricao", "categoria__nome")
    list_editable = ("preco", "disponivel")
    autocomplete_fields = ("categoria",)
    readonly_fields = ("created_at", "updated_at")
