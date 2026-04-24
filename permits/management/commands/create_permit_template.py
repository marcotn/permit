"""
Management command che genera i due template Word per i permessi.

Eseguire una volta dopo il setup:
    python manage.py create_permit_template

Genera:
  - permit_template_admin.docx   → copia per il gestore (cedolino/matrice)
  - permit_template_client.docx  → copia per il cliente (da esporre sul parabrezza)

I file vengono salvati nei percorsi definiti in settings.
Aprire in Word/LibreOffice per rifinire la grafica; i placeholder {{ variabile }}
devono rimanere invariati.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_doc():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    style = doc.styles["Normal"]
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(4)
    style.font.name = "Arial"
    style.font.size = Pt(11)
    return doc


def _add_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10)


def _add_body(doc, text, bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    return p


def _add_field(doc, label, placeholder, size=12):
    p = doc.add_paragraph()
    r1 = p.add_run(f"{label}:  ")
    r1.font.size = Pt(11)
    r2 = p.add_run(placeholder)
    r2.bold = True
    r2.font.size = Pt(size)
    return p


def _add_separator(doc):
    p = doc.add_paragraph("─" * 60)
    p.runs[0].font.size = Pt(8)
    p.runs[0].font.color.rgb = None


HEADER = (
    "PROVINCIA AUTONOMA DI TRENTO\n"
    "ASUC DI CELENTINO\n"
    "Via Giovanni Caserotti n. 31 – 38024 Cogolo di Peio (TN)"
)

LEGAL_NOTE = (
    "In base all'art. 100 della Legge Provinciale 23 maggio 2007, n. 11\n"
    "e relativo regolamento di attuazione,\n"
    "accertato che sussistono le condizioni di cui all'art. 29 del regolamento,"
)


# ---------------------------------------------------------------------------
# Admin template (cedolino – copia gestore)
# ---------------------------------------------------------------------------

def _build_admin_template(doc):
    _add_heading(doc, HEADER)
    doc.add_paragraph()

    _add_separator(doc)
    _add_body(doc, "MATRICE RELATIVA ALL'AUTORIZZAZIONE AL TRANSITO", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_body(doc, "SU STRADA FORESTALE DI TIPO B", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_separator(doc)

    doc.add_paragraph()
    _add_body(doc, "Il proprietario/gestore della Strada Forestale di Tipo B denominata")
    _add_body(doc, "MALGA CAMPO", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_body(doc, "rilascia al Signor/a:")

    doc.add_paragraph()
    _add_field(doc, "Nome", "{{ nome }}")
    _add_field(doc, "Cognome", "{{ cognome }}")
    _add_field(doc, "Residente a", "{{ residenza }}")

    doc.add_paragraph()
    _add_body(doc, "il quale ha dichiarato di dover percorrere la strada forestale sopra citata\ncon il veicolo:")

    _add_field(doc, "Tipo veicolo", "{{ tipo_veicolo }}")
    _add_field(doc, "Targa", "{{ targa }}")

    doc.add_paragraph()
    _add_body(doc, "L'AUTORIZZAZIONE AL TRANSITO PER IL PERIODO", bold=True)

    p = doc.add_paragraph()
    p.add_run("dal  ").font.size = Pt(11)
    r2 = p.add_run("{{ dal }}")
    r2.bold = True
    r2.font.size = Pt(12)
    p.add_run("   al   ").font.size = Pt(11)
    r4 = p.add_run("{{ al }}")
    r4.bold = True
    r4.font.size = Pt(12)

    doc.add_paragraph()
    _add_separator(doc)

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_num.add_run("N.  {{ numero }} / {{ anno }}")
    r.bold = True
    r.font.size = Pt(16)

    _add_separator(doc)
    doc.add_paragraph()
    _add_field(doc, "Data emissione", "{{ data_emissione }}")


# ---------------------------------------------------------------------------
# Client template (autorizzazione – copia cliente / parabrezza)
# ---------------------------------------------------------------------------

def _build_client_template(doc):
    _add_heading(doc, HEADER)
    doc.add_paragraph()

    _add_separator(doc)
    _add_body(doc, "AUTORIZZAZIONE AL TRANSITO SU STRADA FORESTALE DI TIPO B", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_separator(doc)

    doc.add_paragraph()
    _add_body(doc, LEGAL_NOTE)
    doc.add_paragraph()
    _add_body(doc, "SI AUTORIZZA", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    _add_field(doc, "Intestatario", "{{ nome }} {{ cognome }}")
    _add_field(doc, "Residente a", "{{ residenza }}")

    doc.add_paragraph()
    _add_body(doc, "IL TRANSITO DEL VEICOLO:", bold=True)
    _add_field(doc, "Tipo veicolo", "{{ tipo_veicolo }}")
    _add_field(doc, "Targa", "{{ targa }}")

    doc.add_paragraph()
    _add_body(doc, "sulla Strada Forestale denominata")
    _add_body(doc, "MALGA CAMPO", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph()
    _add_body(doc, "per il periodo:")
    p = doc.add_paragraph()
    p.add_run("dal  ").font.size = Pt(11)
    r2 = p.add_run("{{ dal }}")
    r2.bold = True
    r2.font.size = Pt(12)
    p.add_run("   al   ").font.size = Pt(11)
    r4 = p.add_run("{{ al }}")
    r4.bold = True
    r4.font.size = Pt(12)

    doc.add_paragraph()
    _add_body(doc, "Firma e/o timbro proprietario / titolare della gestione:")
    doc.add_paragraph()
    _add_field(doc, "Data", "{{ data_emissione }}")

    doc.add_paragraph()
    _add_separator(doc)

    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_num.add_run("N.  {{ numero }} / {{ anno }}")
    r.bold = True
    r.font.size = Pt(16)

    _add_separator(doc)
    doc.add_paragraph()
    _add_body(doc, "⚠  DA ESPORRE IN MODO BEN VISIBILE SUL VEICOLO", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Genera i due template Word per i permessi (admin e cliente)"

    def handle(self, *args, **options):
        for attr, builder, label in [
            ("PERMIT_TEMPLATE_ADMIN_PATH", _build_admin_template, "admin (cedolino gestore)"),
            ("PERMIT_TEMPLATE_CLIENT_PATH", _build_client_template, "cliente (parabrezza)"),
        ]:
            path = getattr(settings, attr)
            path.parent.mkdir(parents=True, exist_ok=True)
            doc = _new_doc()
            builder(doc)
            doc.save(path)
            self.stdout.write(self.style.SUCCESS(f"✓ Template {label} salvato in: {path}"))

        self.stdout.write("\nAprire i file in Word/LibreOffice per rifinire la grafica.")
        self.stdout.write("I placeholder {{ variabile }} devono restare invariati.")
