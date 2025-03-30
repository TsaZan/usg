from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifies the superuser account'

    def handle(self, *args, **options):
        try:
            superuser = User.objects.get(username='tsa')
            superuser.is_verified = True
            if not superuser.created_at:
                superuser.created_at = timezone.now()
            superuser.save()
            self.stdout.write(self.style.SUCCESS('Successfully verified superuser'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Superuser not found')) 