"""
Custom Django email backend that sends via the Gmail API (OAuth2).

Required settings / env vars:
  GMAIL_CLIENT_ID      – OAuth2 Desktop app client ID (separato dal social login)
  GMAIL_CLIENT_SECRET  – OAuth2 Desktop app client secret
  GMAIL_REFRESH_TOKEN  – refresh token ottenuto con `manage.py gmail_auth`
  DEFAULT_FROM_EMAIL   – indirizzo mittente (deve corrispondere all'account autorizzato)
"""
import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailAPIBackend(BaseEmailBackend):

    def _get_service(self):
        creds = Credentials(
            token=None,
            refresh_token=settings.GMAIL_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )
        creds.refresh(Request())
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        try:
            service = self._get_service()
        except Exception as exc:
            if not self.fail_silently:
                raise
            logger.error("Gmail API: failed to initialise service: %s", exc)
            return 0

        sent = 0
        for message in email_messages:
            try:
                raw = self._build_raw(message)
                service.users().messages().send(
                    userId="me", body={"raw": raw}
                ).execute()
                sent += 1
            except HttpError as exc:
                if not self.fail_silently:
                    raise
                logger.error("Gmail API: send failed for %s: %s", message.to, exc)
        return sent

    @staticmethod
    def _build_raw(email_message):
        mime = MIMEMultipart("alternative")
        mime["Subject"] = email_message.subject
        mime["From"] = email_message.from_email
        mime["To"] = ", ".join(email_message.to)
        if email_message.cc:
            mime["Cc"] = ", ".join(email_message.cc)
        if email_message.reply_to:
            mime["Reply-To"] = ", ".join(email_message.reply_to)

        mime.attach(MIMEText(email_message.body, "plain", "utf-8"))

        for content, mimetype in getattr(email_message, "alternatives", []):
            if mimetype == "text/html":
                mime.attach(MIMEText(content, "html", "utf-8"))

        return base64.urlsafe_b64encode(mime.as_bytes()).decode()
