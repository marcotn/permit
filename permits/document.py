"""Generate filled permit .docx files from Word templates using docxtpl."""

import io
from django.conf import settings
from docxtpl import DocxTemplate


def _build_context(permit: object) -> dict:
    return {
        "numero": str(permit.permit_number or ""),
        "anno": str(permit.permit_year or ""),
        "nome": permit.first_name.upper(),
        "cognome": permit.last_name.upper(),
        "residenza": permit.city.upper(),
        "tipo_veicolo": dict(permit.VEHICLE_CHOICES).get(permit.vehicle_type, permit.vehicle_type).upper(),
        "targa": permit.plate.upper(),
        "dal": permit.valid_from.strftime("%d/%m/%Y"),
        "al": permit.valid_to.strftime("%d/%m/%Y"),
        "data_emissione": permit.issued_at.strftime("%d/%m/%Y") if permit.issued_at else "",
    }


def generate_permit_docx(permit, doc_type: str) -> bytes:
    """
    doc_type: "admin"  → cedolino gestore
              "client" → autorizzazione parabrezza
    """
    template_path = (
        settings.PERMIT_TEMPLATE_ADMIN_PATH
        if doc_type == "admin"
        else settings.PERMIT_TEMPLATE_CLIENT_PATH
    )
    tpl = DocxTemplate(template_path)
    tpl.render(_build_context(permit))
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)
    return buf.read()
