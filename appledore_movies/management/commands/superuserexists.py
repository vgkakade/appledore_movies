from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check if a superuser exists"

    def handle(self, *args, **kwargs):
        model = get_user_model()
        user_exists = model.objects.filter(is_superuser=True).exists()
        if not user_exists:
            print("No superuser exists.")
            raise SystemExit(1)
