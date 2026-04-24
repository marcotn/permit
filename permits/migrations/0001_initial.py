import permits.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PermitRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254)),
                ("valid_from", models.DateField()),
                ("valid_to", models.DateField()),
                ("token", models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ("token_expires_at", models.DateTimeField(default=permits.models.token_expiry)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("city", models.CharField(blank=True, max_length=150)),
                ("vehicle_type", models.CharField(blank=True, choices=[("auto", "Automobile"), ("moto", "Motociclo"), ("quad", "Quad"), ("furgone", "Furgone"), ("camion", "Camion"), ("altro", "Altro")], max_length=20)),
                ("plate", models.CharField(blank=True, max_length=20)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                ("permit_number", models.PositiveIntegerField(blank=True, null=True)),
                ("permit_year", models.PositiveIntegerField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="permit_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
