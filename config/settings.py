import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ---------------------------------------------------------------------------
# Reverse proxy / HTTPS
# Quando Django è dietro un proxy che termina SSL (nginx, Traefik, Caddy…)
# il proxy aggiunge X-Forwarded-Proto: https alle richieste.
# Questa impostazione dice a Django di considerare la richiesta come HTTPS,
# così allauth genera i redirect URL corretti (https://) verso Google OAuth.
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_htmx",
    "whitenoise.runserver_nostatic",
    # local
    "permits",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "permit"),
        "USER": os.environ.get("POSTGRES_USER", "permit"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "permit"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {"pool": True},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "it"
LANGUAGES = [
    ("it", "Italiano"),
    ("de", "Deutsch"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

# ---------------------------------------------------------------------------
# Authentication – allauth + Auth0 via OpenID Connect (same pattern as daccollect)
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

SOCIALACCOUNT_ONLY = os.environ.get("SOCIALACCOUNT_ONLY", "1") == "1"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "offline"},
        "OAUTH_PKCE_ENABLED": True,
        "EMAIL_AUTHENICATION": True,
        "EMAIL_AUTHENTICATION_AUTO_CONNECT": True,
        "SOCIALACCOUNT_ONLY": os.environ.get("SOCIALACCOUNT_ONLY", "1") == "1",
        
    },
}

# Django 4.0+ richiede CSRF_TRUSTED_ORIGINS quando le richieste arrivano
# con un dominio/schema diverso da quello visto da Django (tipico con proxy HTTPS).
# Elenco separato da virgole, es: https://permit.vitreo.cloud
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost:8000").split(",")

#LOGIN_URL = "/accounts/google/login/"
LOGIN_REDIRECT_URL = "/admin-panel/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------------------
# Email
# Sviluppo : Mailpit SMTP  →  EMAIL_BACKEND=smtp (default)
# Produzione: Gmail API    →  EMAIL_BACKEND=gmail
#
# Per usare Gmail API:
#   1. Abilita Gmail API nel progetto GCP
#   2. Aggiungi scope https://www.googleapis.com/auth/gmail.send alla OAuth consent screen
#   3. Esegui una volta in locale: python manage.py gmail_auth
#   4. Copia GMAIL_REFRESH_TOKEN nell'env di produzione
# ---------------------------------------------------------------------------
_email_backend = os.environ.get("EMAIL_BACKEND", "smtp")
if _email_backend == "gmail":
    EMAIL_BACKEND = "config.gmail_backend.GmailAPIBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "mailpit")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 1025))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False") == "True"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@permit.example.com")

# Gmail API credentials – credenziali tipo "Desktop app" (separate dal social login)
# Crea un nuovo OAuth client ID di tipo Desktop app in GCP Console e usa quelli qui.
GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN", "")


SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")

PERMIT_TEMPLATE_ADMIN_PATH = BASE_DIR / "docx_templates/permit_template_admin.docx"
PERMIT_TEMPLATE_CLIENT_PATH = BASE_DIR / "docx_templates/permit_template_client.docx"
