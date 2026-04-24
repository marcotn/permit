"""
Crea (o aggiorna) la SocialApp Google nel database e allinea il record Site.
Va eseguito una volta dopo le migrazioni, o ogni volta che cambiano le credenziali.

    python manage.py setup_oauth
"""

import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea/aggiorna la SocialApp Google e il Site nel database"

    def handle(self, *args, **options):
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

        if not client_id or not secret:
            raise CommandError(
                "GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET devono essere definiti nel .env"
            )

        site_url = os.environ.get("SITE_URL", "http://localhost:8000")
        domain = site_url.replace("https://", "").replace("http://", "").rstrip("/")

        # 1. Aggiorna il record Site
        site, _ = Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={"domain": domain, "name": "Permit"},
        )
        self.stdout.write(f"✓ Site aggiornato: {domain}")

        # 2. Crea o aggiorna la SocialApp Google
        app, created = SocialApp.objects.update_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": client_id,
                "secret": secret,
            },
        )
        app.sites.add(site)

        action = "Creata" if created else "Aggiornata"
        self.stdout.write(self.style.SUCCESS(f"✓ {action} SocialApp Google (client_id: {client_id[:12]}...)"))
