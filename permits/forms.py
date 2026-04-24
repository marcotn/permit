from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PermitRequest


class PermitRequestForm(forms.ModelForm):
    """Admin creates a permit request (email + dates)."""

    class Meta:
        model = PermitRequest
        fields = ["email", "valid_from", "valid_to"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "valid_from": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "valid_to": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "email": _("Email del destinatario"),
            "valid_from": _("Valido dal"),
            "valid_to": _("Valido al"),
        }

    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get("valid_from")
        valid_to = cleaned_data.get("valid_to")
        if valid_from and valid_to and valid_to < valid_from:
            raise forms.ValidationError(_("La data di fine deve essere successiva alla data di inizio."))
        return cleaned_data


VEHICLE_CHOICES = [
    ("", _("Seleziona tipo veicolo")),
    ("auto", "Automobile"),
    ("moto", "Motociclo"),
    ("quad", "Quad"),
    ("furgone", "Furgone"),
    ("camion", "Camion"),
    ("altro", "Altro"),
]


class PermitFillForm(forms.Form):
    """Public form filled by the permit recipient."""

    first_name = forms.CharField(
        max_length=150,
        label=_("Nome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        label=_("Cognome"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    city = forms.CharField(
        max_length=150,
        label=_("Comune di residenza"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_CHOICES,
        label=_("Tipo di veicolo"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    plate = forms.CharField(
        max_length=20,
        label=_("Targa"),
        widget=forms.TextInput(attrs={"class": "form-control", "style": "text-transform:uppercase"}),
    )

    def clean_plate(self):
        return self.cleaned_data["plate"].upper()
