from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config

#Used to create a superuser
class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username="johnr").exists():
            User.objects.create_superuser(config("SUPERUSER_USERNAME"), config("SUPERUSER_EMAIL"), config("SUPERUSER_PASSWORD"))