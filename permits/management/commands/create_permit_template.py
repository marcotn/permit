"""
Management command che genera i due template Word trilingui (IT/DE/EN) per i permessi.

    python manage.py create_permit_template

Genera:
  - permit_template_admin.docx   → copia gestore (cedolino/matrice)
  - permit_template_client.docx  → copia cliente (da esporre sul parabrezza)

I placeholder {{ variabile }} devono restare invariati.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ---------------------------------------------------------------------------
# Testo trilingue
# ---------------------------------------------------------------------------

HEADER = (
    "PROVINCIA AUTONOMA DI TRENTO  –  ASUC DI CELENTINO\n"
    "Via Giovanni Caserotti n. 31 – 38024 Cogolo di Peio (TN)"
)
ROAD_NAME = "MALGA CAMPO"

GREY1 = RGBColor(70,  70,  70)   # DE
GREY2 = RGBColor(110, 110, 110)  # EN / etichette


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_doc():
    doc = Document()
    s = doc.sections[0]
    s.page_width  = Cm(21)
    s.page_height = Cm(29.7)
    s.top_margin    = Cm(1.5)
    s.bottom_margin = Cm(1.5)
    s.left_margin   = Cm(2.5)
    s.right_margin  = Cm(2.5)
    style = doc.styles["Normal"]
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after  = Pt(2)
    style.font.name = "Arial"
    style.font.size = Pt(10)
    return doc


def _sep(doc):
    p = doc.add_paragraph("─" * 62)
    p.paragraph_format.space_after = Pt(1)
    p.runs[0].font.size = Pt(7)


def _blank(doc, after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)


def _center(doc, it_text, de_text=None, en_text=None,
            it_size=12, de_en_size=8, it_bold=True):
    """Testo centrato: IT su riga propria, DE / EN su riga unica sotto."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(it_text)
    r.bold = it_bold
    r.font.size = Pt(it_size)

    if de_text or en_text:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(1)
        parts = [t for t in [de_text, en_text] if t]
        r2 = p2.add_run("  /  ".join(parts))
        r2.font.size = Pt(de_en_size)
        r2.font.color.rgb = GREY1


def _left(doc, it_text, de_text=None, en_text=None,
          it_size=10, de_en_size=8, it_bold=False, after=2):
    """Testo allineato a sinistra: IT, poi DE / EN sotto."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(it_text)
    r.bold = it_bold
    r.font.size = Pt(it_size)

    if de_text or en_text:
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(after)
        parts = [t for t in [de_text, en_text] if t]
        r2 = p2.add_run("  /  ".join(parts))
        r2.font.size = Pt(de_en_size)
        r2.font.color.rgb = GREY1
    else:
        p.paragraph_format.space_after = Pt(after)


def _field(doc, it_label, de_en_label, placeholder, val_size=11, after=2):
    """Riga campo: etichetta trilingue (piccola, grigia) + valore bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    r1 = p.add_run(f"{it_label} / {de_en_label}:  ")
    r1.font.size = Pt(8)
    r1.font.color.rgb = GREY2
    r2 = p.add_run(placeholder)
    r2.bold = True
    r2.font.size = Pt(val_size)


def _dal_al(doc, ph_dal, ph_al):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run("dal/von/from  ")
    r1.font.size = Pt(8)
    r1.font.color.rgb = GREY2
    r2 = p.add_run(ph_dal)
    r2.bold = True
    r2.font.size = Pt(11)
    p.add_run("        ")
    r3 = p.add_run("al/bis/to  ")
    r3.font.size = Pt(8)
    r3.font.color.rgb = GREY2
    r4 = p.add_run(ph_al)
    r4.bold = True
    r4.font.size = Pt(11)


def _numero(doc):
    _sep(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("N.  {{ numero }} / {{ anno }}")
    r.bold = True
    r.font.size = Pt(16)
    _sep(doc)


# ---------------------------------------------------------------------------
# Copia gestore – cedolino/matrice
# ---------------------------------------------------------------------------

def _build_admin_template(doc):
    # Intestazione
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(HEADER)
    r.font.size = Pt(9)
    r.bold = True

    _sep(doc)
    _center(doc,
            "MATRICE RELATIVA ALL'AUTORIZZAZIONE AL TRANSITO SU STRADA FORESTALE DI TIPO B",
            "MATRIX DER DURCHFAHRTSGENEHMIGUNG AUF FORSTSTRASSE TYP B",
            "TRANSIT AUTHORIZATION MATRIX – FOREST ROAD TYPE B",
            it_size=11, de_en_size=8)
    _sep(doc)

    _blank(doc, 3)

    _left(doc,
          "Il proprietario/gestore della Strada Forestale di Tipo B denominata",
          "Der Eigentümer/Verwalter der Forststraße Typ B namens",
          "The owner/manager of the Type B Forest Road named",
          it_size=10, de_en_size=8, after=2)

    _center(doc, ROAD_NAME, it_size=13, it_bold=True)

    _left(doc,
          "rilascia al Signor/a:",
          "gewährt Herrn/Frau:",
          "grants to Mr./Ms.:",
          it_size=10, de_en_size=8, after=4)

    _field(doc, "Nome", "Vorname / First name", "{{ nome }}")
    _field(doc, "Cognome", "Nachname / Last name", "{{ cognome }}")
    _field(doc, "Residente a", "Wohnhaft in / Resident in", "{{ residenza }}", after=3)

    _left(doc,
          "il quale ha dichiarato di dover percorrere la strada forestale sopra citata con il veicolo:",
          "der/die erklärt hat, die oben genannte Forststraße mit folgendem Fahrzeug befahren zu müssen:",
          "who has declared the need to travel on the aforementioned forest road with the vehicle:",
          it_size=10, de_en_size=8, after=3)

    _field(doc, "Tipo veicolo", "Fahrzeugtyp / Vehicle type", "{{ tipo_veicolo }}")
    _field(doc, "Targa", "Kennzeichen / Plate", "{{ targa }}", after=4)

    _center(doc,
            "L'AUTORIZZAZIONE AL TRANSITO PER IL PERIODO",
            "DIE DURCHFAHRTSGENEHMIGUNG FÜR DEN ZEITRAUM",
            "THE TRANSIT AUTHORIZATION FOR THE PERIOD",
            it_size=11, de_en_size=8, it_bold=True)

    _dal_al(doc, "{{ dal }}", "{{ al }}")

    _numero(doc)

    _blank(doc, 2)
    _field(doc, "Data emissione", "Ausstellungsdatum / Issue date", "{{ data_emissione }}")


# ---------------------------------------------------------------------------
# Copia cliente – autorizzazione parabrezza
# ---------------------------------------------------------------------------

def _build_client_template(doc):
    # Intestazione
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(HEADER)
    r.font.size = Pt(9)
    r.bold = True

    _sep(doc)
    _center(doc,
            "AUTORIZZAZIONE AL TRANSITO SU STRADA FORESTALE DI TIPO B",
            "DURCHFAHRTSGENEHMIGUNG AUF FORSTSTRASSE TYP B",
            "TRANSIT AUTHORIZATION ON FOREST ROAD TYPE B",
            it_size=11, de_en_size=8)
    _sep(doc)

    _blank(doc, 3)

    # Nota legale – solo IT per brevità, DE/EN su riga unica sotto
    _left(doc,
          "In base all'art. 100 della Legge Provinciale 23 maggio 2007, n. 11 e relativo regolamento di attuazione,\n"
          "accertato che sussistono le condizioni di cui all'art. 29 del regolamento,",
          "Gemäß Art. 100 LG 23.05.2007, Nr. 11 / Pursuant to Art. 100 Provincial Law 23.05.2007, No. 11",
          it_size=9, de_en_size=8, after=4)

    _center(doc,
            "SI AUTORIZZA",
            "WIRD GENEHMIGT",
            "IS AUTHORIZED",
            it_size=14, de_en_size=9, it_bold=True)

    _blank(doc, 3)

    _field(doc, "Intestatario", "Inhaber / Holder", "{{ nome }} {{ cognome }}", val_size=12)
    _field(doc, "Residente a", "Wohnhaft in / Resident in", "{{ residenza }}", after=3)

    _left(doc,
          "IL TRANSITO DEL VEICOLO:",
          "DIE DURCHFAHRT DES FAHRZEUGS:  /  VEHICLE TRANSIT:",
          it_size=10, de_en_size=8, it_bold=True, after=2)

    _field(doc, "Tipo veicolo", "Fahrzeugtyp / Vehicle type", "{{ tipo_veicolo }}")
    _field(doc, "Targa", "Kennzeichen / Plate", "{{ targa }}", after=3)

    _left(doc,
          "sulla Strada Forestale denominata  /  auf der Forststraße:  /  on the forest road:",
          it_size=9, de_en_size=8, after=1)
    _center(doc, ROAD_NAME, it_size=13, it_bold=True)

    _blank(doc, 3)

    _left(doc,
          "per il periodo:  /  für den Zeitraum:  /  for the period:",
          it_size=9, de_en_size=8, after=1)
    _dal_al(doc, "{{ dal }}", "{{ al }}")

    _blank(doc, 3)

    # Firma
    _left(doc,
          "Firma e/o timbro del proprietario / titolare della gestione:",
          "Unterschrift/Stempel des Eigentümers  /  Signature/stamp of the owner:",
          it_size=9, de_en_size=8, after=1)
    _field(doc, "Data", "Datum / Date", "{{ data_emissione }}", after=4)

    _numero(doc)

    _blank(doc, 2)

    # Avviso esporre
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("⚠  DA ESPORRE BEN VISIBILE SUL VEICOLO  /  GUT SICHTBAR AUSLEGEN  /  DISPLAY CLEARLY IN THE VEHICLE")
    r.bold = True
    r.font.size = Pt(8)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Genera i due template Word trilingui (IT/DE/EN) per i permessi"

    def handle(self, *args, **options):
        for attr, builder, label in [
            ("PERMIT_TEMPLATE_ADMIN_PATH",  _build_admin_template,  "admin (cedolino gestore)"),
            ("PERMIT_TEMPLATE_CLIENT_PATH", _build_client_template, "cliente (parabrezza)"),
        ]:
            path = getattr(settings, attr)
            path.parent.mkdir(parents=True, exist_ok=True)
            doc = _new_doc()
            builder(doc)
            doc.save(path)
            self.stdout.write(self.style.SUCCESS(f"✓ {label}  →  {path}"))

        self.stdout.write("\nI placeholder {{ variabile }} devono restare invariati.")
