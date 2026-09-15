import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Cliente, ConfiguracaoEmpresa


class Command(BaseCommand):
    help = 'Cria dados mínimos e fictícios para a demonstração.'

    def handle(self, *args, **options):
        password = os.environ.get('DEMO_PASSWORD', 'SolarGestDemo123!')
        demo, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@solargest.local', 'is_staff': True, 'is_superuser': True},
        )
        if created or not demo.check_password(password):
            demo.set_password(password)
        demo.email = 'demo@solargest.local'
        demo.is_staff = True
        demo.is_superuser = True
        demo.save()

        ConfiguracaoEmpresa.objects.get_or_create(pk=1, defaults={'nome': 'Solar Gest'})
        Cliente.objects.get_or_create(
            nome='Cliente demonstração',
            defaults={
                'telefone': '+39 02 0000 0000',
                'email': 'cliente.demo@solargest.local',
                'endereco': 'Milano, Italia',
            },
        )
        self.stdout.write(self.style.SUCCESS('Dados demo prontos. Usuário: demo'))
