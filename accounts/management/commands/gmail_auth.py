"""
One-time command to authorise the Gmail API and obtain a refresh token.

Run this locally (not in Docker) once:

    python manage.py gmail_auth

A browser window opens for the Google consent screen.
After consent, the refresh token is printed: copy it into the
GMAIL_REFRESH_TOKEN env var (stack-prod.yml / .env).

The command uses the same GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET already
configured for social login, so no new GCP credentials are needed — but you
MUST enable the Gmail API and add the scope in the GCP console first
(see README for the exact steps).
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class Command(BaseCommand):
    help = "Obtain a Gmail API refresh token via OAuth2 browser flow."

    def handle(self, *args, **options):
        client_id = settings.GMAIL_CLIENT_ID
        client_secret = settings.GMAIL_CLIENT_SECRET

        if not client_id or not client_secret:
            self.stderr.write(self.style.ERROR(
                "GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set.\n"
                "Create a Desktop app OAuth credential in GCP Console and add them to .env"
            ))
            return

        # Build the client-secrets structure in memory (no JSON file needed)
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

        self.stdout.write(
            "\nA browser window will open. Log in with the Gmail account "
            "you want to use for sending emails.\n"
        )

        creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

        self.stdout.write(self.style.SUCCESS("\n✓ Authorisation complete.\n"))
        self.stdout.write("Add this to your stack-prod.yml and .env:\n")
        self.stdout.write(
            self.style.WARNING(f"  GMAIL_REFRESH_TOKEN: {creds.refresh_token}\n")
        )
