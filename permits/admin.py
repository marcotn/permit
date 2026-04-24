from django.contrib import admin
from .models import PermitRequest


@admin.register(PermitRequest)
class PermitRequestAdmin(admin.ModelAdmin):
    list_display = [
        "permit_number", "permit_year", "email", "first_name", "last_name",
        "valid_from", "valid_to", "is_completed", "created_at",
    ]
    list_filter = ["is_completed", "permit_year"]
    search_fields = ["email", "first_name", "last_name", "plate"]
    readonly_fields = ["token", "token_expires_at", "permit_number", "permit_year", "issued_at", "created_at"]
