import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria ou atualiza a conta de administrador configurada no ambiente."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")
        email = os.environ.get("ADMIN_EMAIL", "").strip()
        if not username or not password:
            raise CommandError(
                "Defina ADMIN_USERNAME e ADMIN_PASSWORD no ambiente ou no arquivo .env."
            )

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS(f"Administrador '{username}' {action}."))
