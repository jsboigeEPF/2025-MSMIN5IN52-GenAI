from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from pathlib import Path
from typing import Dict, Any, List
from src.utils.file_utils import ensure_dir
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# --------------------------------------------------------------------
#                   CONSTANTES LAYOUT
# --------------------------------------------------------------------
TOP_MARGIN = 250 * mm
LEFT_MARGIN = 35 * mm
RIGHT_MARGIN = A4[0] - 25 * mm
BOTTOM_MARGIN = 25 * mm
CONTENT_WIDTH = A4[0] - LEFT_MARGIN - 25 * mm


# --------------------------------------------------------------------
#                   HEADER & FOOTER
# --------------------------------------------------------------------
def _add_header_footer(c: canvas.Canvas, title: str, author: str):
    width, height = A4

    # Ligne d'en-tête violette + titre centré
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#4B0082"))
    c.drawCentredString(width / 2, height - 20, title)

    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.3)
    c.line(LEFT_MARGIN, height - 28, width - LEFT_MARGIN, height - 28)

    # Pied de page
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    footer_text = f"{author} – EPF | Page {c.getPageNumber()}"
    c.drawRightString(width - LEFT_MARGIN, 25, footer_text)
    c.line(LEFT_MARGIN, 40, width - LEFT_MARGIN, 40)


# --------------------------------------------------------------------
#                   DÉCORATION : BANDE LAVANDE
# --------------------------------------------------------------------
def _draw_left_band(c: canvas.Canvas):
    """Dessine une bande lavande verticale à gauche (identique à la page de garde)."""
    c.setFillColor(colors.HexColor("#EAE6FF"))  # lavande claire
    c.rect(0, 0, 25 * mm, A4[1], stroke=0, fill=1)  # même largeur que la page de garde
    c.setFillColor(colors.black)



# --------------------------------------------------------------------
#                   MAIN FUNCTION
# --------------------------------------------------------------------
def render_pdf_report(data: Dict[str, Any]) -> str:
    try:
        # Normalisation
        if isinstance(data.get("author"), dict):
            a = data["author"]
            data["author"] = f"{a.get('name', '')} ({a.get('organization', '')})"

        if "summary" in data and "executive_summary" not in data:
            data["executive_summary"] = data["summary"]

        if "content" in data and not data.get("sections"):
            data["sections"] = [
                {"title": sec.get("section_title", "Untitled Section"),
                 "content": sec.get("section_content", "")}
                for sec in data["content"]
            ]

        output_dir = Path("out/report")
        ensure_dir(output_dir)
        report_id = data.get("report_id", "0001")
        output_path = output_dir / f"report_{report_id}.pdf"

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        _add_title_page(c, data, width, height)
        _add_executive_summary(c, data.get("executive_summary", ""), data)
        _add_table_of_contents(c, data.get("sections", []), data)

        for idx, section in enumerate(data.get("sections", []), 1):
            _add_section(c, section, data, idx)

        c.save()
        return str(output_path)

    except Exception as e:
        raise RuntimeError(f"Report PDF rendering failed: {str(e)}")


# --------------------------------------------------------------------
#                   PAGE DE TITRE (centrée verticalement + horizontalement)
# --------------------------------------------------------------------
def _add_title_page(c, data, width, height):
    """Page de garde professionnelle et institutionnelle EPF."""
    # === Fond lavande clair sur 25 mm ===
    c.setFillColor(colors.HexColor("#EAE6FF"))
    c.rect(0, 0, 25 * mm, height, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.rect(25 * mm, 0, width - 25 * mm, height, stroke=0, fill=1)

    # === Données principales ===
    title = data.get("title", "Rapport Technique")
    subtitle = data.get("subtitle", "Projet IMSA Forever Shop – EPF 2025")
    author = data.get("author", "Safae Berrichi (IMSA – EPF)")
    date = data.get("date", "Octobre 2025")

    # === Logo EPF dans la bande lavande (haut gauche) ===
    logo_path = Path("assets/epf_logo.png")
    if logo_path.exists():
        c.drawImage(str(logo_path), 10 * mm, height - 45 * mm, width=40 * mm, preserveAspectRatio=True)

    # === Titre principal (centré verticalement) ===
    y_center = height / 2 + 30

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor("#001F7F"))

    # Gestion automatique du retour à la ligne
    words = title.split(" ")
    line = ""
    lines = []
    for word in words:
        if c.stringWidth(line + " " + word, "Helvetica-Bold", 26) > width - 120:
            lines.append(line)
            line = word
        else:
            line += " " + word
    lines.append(line)

    for i, l in enumerate(lines):
        c.drawCentredString(width / 2 + 10 * mm, y_center - (i * 30), l.strip())

    # === Sous-titre (violet) ===
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.HexColor("#4B0082"))
    c.drawCentredString(width / 2 + 10 * mm, y_center - (len(lines) * 35), subtitle)

    # === Ligne décorative avec dégradé bleu-violet ===
    c.setLineWidth(1.8)
    for i in range(0, 200, 3):
        r = (0 + i * (75 / 200)) / 255
        g = (31 - i * (31 / 200)) / 255
        b = (127 + i * (128 - 127) / 200) / 255
        c.setStrokeColorRGB(r, g, b)
        c.line(width / 2 - 100 + i, y_center - (len(lines) * 45) - 10,
               width / 2 - 100 + i + 3, y_center - (len(lines) * 45) - 10)

    # === Informations en bas ===
    c.setStrokeColor(colors.lightgrey)
    c.line(LEFT_MARGIN, 100, width - LEFT_MARGIN, 100)

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2 + 10 * mm, 80, f"Auteur : {author}")
    c.drawCentredString(width / 2 + 10 * mm, 60, f"Date : {date}")

    # === Mention institutionnelle ===
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2 + 10 * mm, 40, "École d’ingénieurs EPF – Département Ingénierie Numérique")

    c.showPage()



# --------------------------------------------------------------------
#                   EXECUTIVE SUMMARY
# --------------------------------------------------------------------
def _add_executive_summary(c, summary, data):
    if not summary:
        return

    _draw_left_band(c)
    _add_header_footer(c, data.get("title", "Rapport Technique"), data.get("author", ""))

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#001F7F"))
    c.drawString(LEFT_MARGIN, TOP_MARGIN, "Executive Summary")

    c.setStrokeColor(colors.HexColor("#4B0082"))
    c.line(LEFT_MARGIN, TOP_MARGIN - 5, RIGHT_MARGIN, TOP_MARGIN - 5)

    _draw_paragraph(c, summary, LEFT_MARGIN, TOP_MARGIN - 25, font_size=11)
    c.showPage()


# --------------------------------------------------------------------
#                   TABLE DES MATIÈRES (TOC)
# --------------------------------------------------------------------
def _add_table_of_contents(c, sections, data):
    if not sections:
        return

    _draw_left_band(c)
    _add_header_footer(c, data.get("title", ""), data.get("author", ""))

    # Titre bleu foncé comme les autres sections
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#001F7F"))
    c.drawString(LEFT_MARGIN, TOP_MARGIN, "Table of Contents")

    # Ligne violette
    c.setStrokeColor(colors.HexColor("#4B0082"))
    c.line(LEFT_MARGIN, TOP_MARGIN - 5, RIGHT_MARGIN, TOP_MARGIN - 5)

    # Corps du sommaire
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    y = TOP_MARGIN - 30

    for i, sec in enumerate(sections, 1):
        title = sec.get("title", f"Section {i}")
        page_number = i + 3  # estimation : après résumé + TOC

        # Crée les points et le texte aligné
        dot_line = _create_leader_dots(title, LEFT_MARGIN + 5, RIGHT_MARGIN - 25, page_number, c)

        c.drawString(LEFT_MARGIN + 5, y, dot_line["text"])
        c.drawRightString(RIGHT_MARGIN, y, dot_line["page"])
        y -= 18

        if y < 60 * mm:
            c.showPage()
            _draw_left_band(c)
            _add_header_footer(c, data.get("title", ""), data.get("author", ""))
            y = TOP_MARGIN - 20

    c.showPage()


# --------------------------------------------------------------------
#                   LEADER DOTS UTILITY
# --------------------------------------------------------------------
def _create_leader_dots(title: str, x_start: float, x_end: float, page_num: int, c: canvas.Canvas) -> dict:
    """
    Crée une ligne avec des points entre le titre et le numéro de page.
    Exemple : "1. Architecture MERN ....................... Page 4"
    """
    c.setFont("Helvetica", 12)
    text = f"{title}"
    page_label = f"Page {page_num}"

    # Calcul largeur dispo
    text_width = c.stringWidth(text, "Helvetica", 12)
    page_width = c.stringWidth(page_label, "Helvetica", 12)
    available_width = x_end - x_start - text_width - page_width - 10

    # Nombre de points selon espace disponible
    if available_width > 0:
        num_dots = int(available_width / c.stringWidth(".", "Helvetica", 12))
        dots = "." * num_dots
    else:
        dots = " "

    return {"text": f"{text} {dots}", "page": page_label}


# --------------------------------------------------------------------
#                   SECTIONS
# --------------------------------------------------------------------
def _add_section(c, section, data, index):
    _draw_left_band(c)
    _add_header_footer(c, data.get("title", ""), data.get("author", ""))

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#001F7F"))
    c.drawString(LEFT_MARGIN, TOP_MARGIN, section.get("title", f"Section {index}"))
    c.setStrokeColor(colors.HexColor("#4B0082"))
    c.line(LEFT_MARGIN, TOP_MARGIN - 5, RIGHT_MARGIN, TOP_MARGIN - 5)

    _draw_paragraph(c, section.get("content", ""), LEFT_MARGIN, TOP_MARGIN - 25, font_size=11)
    c.showPage()


# --------------------------------------------------------------------
#                   PARAGRAPHES JUSTIFIÉS
# --------------------------------------------------------------------
def _draw_paragraph(c, text, x, y, font_size=11):
    """Paragraphe justifié avec gestion fluide."""
    style = ParagraphStyle(
        "Justify",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 4,
        alignment=4,  # Justified
        textColor=colors.black,
    )

    p = Paragraph(text.replace("\n", "<br/>"), style)
    frame = Frame(x, 50 * mm, CONTENT_WIDTH, y - 50 * mm, leftPadding=0, bottomPadding=0, rightPadding=0)
    frame.addFromList([p], c)
