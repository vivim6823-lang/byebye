from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Category, Product


def _category_data(category):
    return {"id": category.id, "name": category.name}


def _product_data(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": format(product.price, ".2f"),
        "is_available": product.is_available,
        "category": _category_data(product.category),
    }


def _positive_int(value, name):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} deve ser um número inteiro positivo.")
    if number < 1:
        raise ValueError(f"{name} deve ser um número inteiro positivo.")
    return number


@require_GET
def categories(request):
    results = [
        _category_data(category)
        for category in Category.objects.filter(is_active=True)
    ]
    return JsonResponse({"count": len(results), "results": results})


@require_GET
def products(request):
    queryset = Product.objects.select_related("category").filter(
        category__is_active=True
    )
    category_id = request.GET.get("category_id")
    if category_id is not None:
        try:
            queryset = queryset.filter(
                category_id=_positive_int(category_id, "category_id")
            )
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    available = request.GET.get("available")
    if available is not None:
        normalized = available.strip().lower()
        if normalized not in {"true", "false"}:
            return JsonResponse(
                {"error": "available deve ser 'true' ou 'false'."}, status=400
            )
        queryset = queryset.filter(is_available=(normalized == "true"))

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    try:
        page_number = _positive_int(request.GET.get("page", "1"), "page")
        page_size = _positive_int(request.GET.get("page_size", "50"), "page_size")
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    if page_size > 100:
        return JsonResponse(
            {"error": "page_size não pode ser maior que 100."}, status=400
        )

    page = Paginator(queryset, page_size)
    try:
        page_results = page.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        return JsonResponse({"error": "A página solicitada não existe."}, status=404)

    return JsonResponse(
        {
            "count": page.count,
            "next": page_results.next_page_number() if page_results.has_next() else None,
            "previous": (
                page_results.previous_page_number()
                if page_results.has_previous()
                else None
            ),
            "results": [_product_data(product) for product in page_results],
        }
    )


@require_GET
def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=product_id,
        category__is_active=True,
    )
    return JsonResponse(_product_data(product))
