import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Category",
            new_name="Categoria",
        ),
        migrations.RenameModel(
            old_name="Product",
            new_name="Produto",
        ),
        migrations.RenameField(
            model_name="categoria",
            old_name="name",
            new_name="nome",
        ),
        migrations.RenameField(
            model_name="categoria",
            old_name="description",
            new_name="descricao",
        ),
        migrations.RenameField(
            model_name="produto",
            old_name="name",
            new_name="nome",
        ),
        migrations.RenameField(
            model_name="produto",
            old_name="category",
            new_name="categoria",
        ),
        migrations.RenameField(
            model_name="produto",
            old_name="description",
            new_name="descricao",
        ),
        migrations.RenameField(
            model_name="produto",
            old_name="price",
            new_name="preco",
        ),
        migrations.RenameField(
            model_name="produto",
            old_name="is_available",
            new_name="disponivel",
        ),
        migrations.AlterField(
            model_name="produto",
            name="nome",
            field=models.CharField(max_length=150, verbose_name="nome"),
        ),
        migrations.AlterField(
            model_name="produto",
            name="categoria",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="produtos",
                to="menu.categoria",
                verbose_name="categoria",
            ),
        ),
        migrations.AlterModelOptions(
            name="produto",
            options={
                "ordering": ["categoria__nome", "nome"],
                "verbose_name": "produto",
                "verbose_name_plural": "produtos",
            },
        ),
        migrations.AlterModelOptions(
            name="categoria",
            options={
                "ordering": ["nome"],
                "verbose_name": "categoria",
                "verbose_name_plural": "categorias",
            },
        ),
    ]
