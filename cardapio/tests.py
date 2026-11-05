import json
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Produto
from .serializers import ProdutoSerializer


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

    def test_product_serializer_rejects_negative_price(self):
        category = Categoria.objects.create(nome="Lanches")
        serializer = ProdutoSerializer(
            data={
                "nome": "X-Burger",
                "preco": "-0.01",
                "categoria": category.pk,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("preco", serializer.errors)


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
        self.assertContains(response, 'href="/api/categorias/"')
        self.assertContains(response, 'href="/api/produtos/"')

    def test_categories_can_be_listed(self):
        response = self.client.get(reverse("categoria-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["nome"], "Lanches")

    def test_products_returns_price_and_category_name(self):
        response = self.client.get(reverse("produto-list"))

        self.assertEqual(response.status_code, 200)
        product = response.json()["results"][0]
        self.assertEqual(product["preco"], "22.90")
        self.assertEqual(product["categoria_nome"], "Lanches")

    def test_products_filter_by_availability_and_search_by_name(self):
        Produto.objects.create(
            categoria=self.category,
            nome="X-Salada",
            preco="20.00",
            disponivel=False,
        )
        response = self.client.get(
            reverse("produto-list"),
            {"disponivel": "true", "search": "Burger"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["nome"], "X-Burger")

    def test_products_paginates_results(self):
        for index in range(50):
            Produto.objects.create(
                categoria=self.category,
                nome=f"Produto {index}",
                preco="1.00",
            )

        first_page = self.client.get(reverse("produto-list"), {"page": "1"}).json()
        second_page = self.client.get(reverse("produto-list"), {"page": "2"}).json()

        self.assertEqual(first_page["count"], 51)
        self.assertIn("page=2", first_page["next"])
        self.assertIsNone(first_page["previous"])
        self.assertTrue(second_page["previous"].endswith("/api/produtos/"))
        self.assertIsNone(second_page["next"])

    def test_invalid_filter_returns_bad_request(self):
        response = self.client.get(
            reverse("produto-list"), {"disponivel": "maybe"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("disponivel", response.json())

    def test_category_action_lists_associated_products(self):
        response = self.client.get(
            reverse("categoria-produtos", args=[self.category.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["nome"], "X-Burger")

    def test_api_supports_crud_for_categories_and_products(self):
        user = get_user_model().objects.create_user(
            username="editor", password="strong-password"
        )
        self.client.force_login(user)

        category_response = self.client.post(
            reverse("categoria-list"),
            {"nome": "Bebidas", "descricao": "Bebidas frias"},
        )
        self.assertEqual(category_response.status_code, 201)
        category_id = category_response.json()["id"]
        category_detail = self.client.get(
            reverse("categoria-detail", args=[category_id])
        )
        self.assertEqual(category_detail.status_code, 200)
        category_update = self.client.patch(
            reverse("categoria-detail", args=[category_id]),
            {"descricao": "Sucos e refrigerantes"},
            content_type="application/json",
        )
        self.assertEqual(category_update.status_code, 200)

        product_response = self.client.post(
            reverse("produto-list"),
            {"nome": "Suco", "preco": "8.50", "categoria": category_id},
        )
        self.assertEqual(product_response.status_code, 201)
        product_id = product_response.json()["id"]

        detail_response = self.client.get(reverse("produto-detail", args=[product_id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["categoria_nome"], "Bebidas")

        update_response = self.client.patch(
            reverse("produto-detail", args=[product_id]),
            {"disponivel": False},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertFalse(update_response.json()["disponivel"])

        delete_response = self.client.delete(
            reverse("produto-detail", args=[product_id])
        )
        self.assertEqual(delete_response.status_code, 204)

        delete_category = self.client.delete(
            reverse("categoria-detail", args=[category_id])
        )
        self.assertEqual(delete_category.status_code, 204)

    def test_api_rejects_non_get_methods(self):
        response = self.client.post(reverse("produto-list"))

        self.assertEqual(response.status_code, 401)

    def test_token_endpoint_returns_authentication_token(self):
        user = get_user_model().objects.create_user(
            username="token-user", password="strong-password"
        )
        response = self.client.post(
            reverse("api-token"),
            {"username": user.username, "password": "strong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["token"])
        create_response = self.client.post(
            reverse("categoria-list"),
            {"nome": "Sobremesas"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {response.json()['token']}",
        )
        self.assertEqual(create_response.status_code, 201)

    def test_schema_and_swagger_documentation_are_available(self):
        schema_response = self.client.get(
            reverse("api-schema"), HTTP_ACCEPT="application/vnd.oai.openapi+json"
        )
        docs_response = self.client.get(reverse("api-docs"))

        self.assertEqual(schema_response.status_code, 200)
        schema = json.loads(schema_response.content)
        self.assertIn("/api/produtos/", schema["paths"])
        self.assertIn("/api/categorias/{id}/produtos/", schema["paths"])
        self.assertEqual(docs_response.status_code, 200)


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
