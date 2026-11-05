from django.contrib import admin

from .models import Category, Product


admin.site.site_header = "Administração do cardápio"
admin.site.site_title = "Cardápio"
admin.site.index_title = "Gerenciamento do cardápio"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    list_editable = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "updated_at")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description", "category__name")
    list_editable = ("price", "is_available")
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at")
