import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings


def token_expiry():
    return timezone.now() + timedelta(hours=24)


class PermitRequest(models.Model):
    """Created by admin. Triggers email with unique link."""

    VEHICLE_CHOICES = [
        ("auto", "Automobile"),
        ("moto", "Motociclo"),
        ("quad", "Quad"),
        ("furgone", "Furgone"),
        ("camion", "Camion"),
        ("altro", "Altro"),
    ]

    # --- admin fills these ---
    email = models.EmailField()
    valid_from = models.DateField()
    valid_to = models.DateField()

    # --- token for the public link ---
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    token_expires_at = models.DateTimeField(default=token_expiry)

    # --- filled by recipient ---
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=150, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, blank=True)
    plate = models.CharField(max_length=20, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)

    # --- permit number (resets each year) ---
    permit_number = models.PositiveIntegerField(null=True, blank=True)
    permit_year = models.PositiveIntegerField(null=True, blank=True)

    # --- state ---
    is_completed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="permit_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Permit {self.permit_number}/{self.permit_year} – {self.email}"

    @property
    def is_token_valid(self):
        return timezone.now() < self.token_expires_at

    @property
    def public_url(self):
        return f"{settings.SITE_URL}/permit/{self.token}/"

    def assign_permit_number(self):
        """Assign next sequential number for the current year."""
        now = timezone.now()
        year = now.year
        last = (
            PermitRequest.objects.filter(permit_year=year, permit_number__isnull=False)
            .order_by("-permit_number")
            .first()
        )
        self.permit_number = (last.permit_number + 1) if last else 1
        self.permit_year = year
        self.issued_at = now

    def save_completed(self, first_name, last_name, city, vehicle_type, plate):
        self.first_name = first_name
        self.last_name = last_name
        self.city = city
        self.vehicle_type = vehicle_type
        self.plate = plate
        self.assign_permit_number()
        self.is_completed = True
        self.save()
