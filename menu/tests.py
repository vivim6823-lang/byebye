from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Produto


class MenuModelTests(TestCase):
    def test_category_name_is_unique_and_description_is_optional(self):
        category = Categoria.objects.create(nome="Lanches")
        name_field = Categoria._meta.get_field("nome")
        self.assertEqual(name_field.max_length, 100)
        self.assertTrue(name_field.unique)
        self.assertEqual(category.descricao, "")
        with self.assertRaises(ValidationError):
            Categoria(nome="Lanches").validate_unique()

    def test_product_matches_required_schema(self):
        category = Categoria.objects.create(nome="Lanches")
        product = Produto.objects.create(categoria=category, nome="X-Burger", preco=0)

        self.assertEqual(Produto._meta.get_field("nome").max_length, 150)
        price_field = Produto._meta.get_field("preco")
        self.assertEqual(price_field.max_digits, 8)
        self.assertEqual(price_field.decimal_places, 2)
        self.assertEqual(product.disponivel, True)
        self.assertEqual(product.descricao, "")
        self.assertEqual(category.produtos.get(), product)
        self.assertEqual(Produto._meta.get_field("categoria").remote_field.related_name, "produtos")

    def test_product_price_cannot_be_negative(self):
        category = Categoria.objects.create(nome="Lanches")
        product = Produto(categoria=category, nome="X-Burger", preco="-0.01")

        with self.assertRaises(ValidationError):
            product.full_clean()


class MenuApiTests(TestCase):
    def setUp(self):
        self.category = Categoria.objects.create(nome="Lanches")
        self.product = Produto.objects.create(
            categoria=self.category,
            nome="X-Burger",
            descricao="Hambúrguer com queijo",
            preco="22.90",
        )

    def test_homepage_links_to_admin_and_api(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/admin/"')
        self.assertContains(response, 'href="/api/categories/"')
        self.assertContains(response, 'href="/api/products/"')

    def test_categories_returns_only_active_categories(self):
        Categoria.objects.create(nome="Inativa", is_active=False)

        response = self.client.get(reverse("api-categories-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "count": 1,
            "results": [{"id": self.category.id, "name": "Lanches"}],
        })

    def test_products_returns_price_as_decimal_string(self):
        response = self.client.get(reverse("api-products-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [{
            "id": self.product.id,
            "name": "X-Burger",
            "description": "Hambúrguer com queijo",
            "price": "22.90",
            "is_available": True,
            "category": {"id": self.category.id, "name": "Lanches"},
        }])

    def test_products_supports_filters(self):
        response = self.client.get(
            reverse("api-products-list"),
            {"category_id": self.category.id, "available": "true", "q": "burger"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.product.id)

    def test_products_paginates_results(self):
        Produto.objects.create(
            categoria=self.category, nome="X-Salada", preco="20.00", disponivel=False
        )

        first_page = self.client.get(
            reverse("api-products-list"), {"page_size": "1", "page": "1"}
        ).json()
        second_page = self.client.get(
            reverse("api-products-list"), {"page_size": "1", "page": "2"}
        ).json()

        self.assertEqual(first_page["count"], 2)
        self.assertEqual(first_page["next"], 2)
        self.assertIsNone(first_page["previous"])
        self.assertEqual(second_page["previous"], 1)
        self.assertIsNone(second_page["next"])

    def test_invalid_filter_returns_bad_request(self):
        response = self.client.get(
            reverse("api-products-list"), {"available": "maybe"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_product_detail_hides_products_in_inactive_categories(self):
        self.category.is_active = False
        self.category.save()

        response = self.client.get(
            reverse("api-products-detail", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_api_rejects_non_get_methods(self):
        response = self.client.post(reverse("api-products-list"))

        self.assertEqual(response.status_code, 405)

    def test_invalid_page_size_returns_bad_request(self):
        response = self.client.get(
            reverse("api-products-list"), {"page_size": "101"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"error": "page_size não pode ser maior que 100."}
        )


class AdminPanelTests(TestCase):
    def test_bootstrap_command_creates_and_updates_admin_password(self):
        with patch.dict(
            "os.environ",
            {
                "ADMIN_USERNAME": "configured-admin",
                "ADMIN_PASSWORD": "initial-password",
                "ADMIN_EMAIL": "owner@example.com",
            },
        ):
            call_command("bootstrap_admin", stdout=StringIO())
        with patch.dict(
            "os.environ",
            {
                "ADMIN_USERNAME": "configured-admin",
                "ADMIN_PASSWORD": "updated-password",
            },
        ):
            call_command("bootstrap_admin", stdout=StringIO())

        user = get_user_model().objects.get(username="configured-admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("updated-password"))

    def test_admin_can_manage_categories_and_products(self):
        user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(user)

        categories_response = self.client.get("/admin/menu/categoria/")
        products_response = self.client.get("/admin/menu/produto/")

        self.assertEqual(categories_response.status_code, 200)
        self.assertEqual(products_response.status_code, 200)
