from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from typing import Dict, Any
from pathlib import Path
from src.utils.file_utils import ensure_dir
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY


def render_pdf_cv(data: Dict[str, Any], theme_color: str = "#ede6f9") -> str:
    """
    CV moderne fusionné :
    - style visuel de la version initiale (photo ronde + barre lavande douce)
    - logique solide de la version modernisée
    - compatibilité avec les nouvelles clés JSON : personal_info, work_experience, etc.
    """
    try:
        # === Préparation sortie ===
        output_dir = Path("out/cv")
        ensure_dir(output_dir)
        name = data.get("personal_info", {}).get("name", "cv").replace(" ", "_")
        output_path = output_dir / f"{name}_modern_cv.pdf"

        # === Canvas ===
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4
        margin = 20 * mm
        sidebar_width = 70 * mm
        content_x = margin + sidebar_width + 10  # 🔹 poussé un peu à gauche
        right_limit = width - margin
        y_top = height - margin

        # === Barre lavande plaquée à gauche ===
        c.setFillColor(colors.HexColor(theme_color))
        c.rect(0, 0, sidebar_width, height, stroke=0, fill=1)

        # === Photo circulaire centrée dans la colonne ===
        personal = data.get("personal_info", {})
        photo_path = personal.get("photo")
        if photo_path and Path(photo_path).exists():
            _draw_circular_photo_with_shadow(c, photo_path, 9 * mm, height - 95 * mm, 50 * mm)  

        # === Sidebar (gauche) ===
        y = height - 115 * mm
        y = _sidebar_block(c, "CONTACT", [
            personal.get("address", ""),
            personal.get("phone", ""),
            personal.get("email", "")
        ], 10 * mm, y)

        y = _sidebar_block(c, "COMPÉTENCES", _flatten_skills(data.get("skills", {})), 10 * mm, y - 5)
        y = _sidebar_block(c, "LANGUES", data.get("languages", []), 10 * mm, y - 5)
        y = _sidebar_block(c, "INTÉRÊTS", data.get("interests", []), 10 * mm, y - 5)

        # === Partie droite ===
        y = y_top - 10
        y = _draw_header_right(c, personal, content_x, y, right_limit)
        y = _draw_separator(c, content_x, y, right_limit)

        if "education" in data:
            y = _draw_section_right(c, "FORMATION", data["education"], content_x, y - 10, right_limit)
            y = _draw_separator(c, content_x, y, right_limit)
        if "work_experience" in data:
            y = _draw_section_right(c, "EXPÉRIENCE PROFESSIONNELLE", data["work_experience"], content_x, y - 10, right_limit)
            y = _draw_separator(c, content_x, y, right_limit)
        if "projects" in data:
            y = _draw_section_right(c, "PROJETS PERSONNELS", data["projects"], content_x, y - 10, right_limit)
            y = _draw_separator(c, content_x, y, right_limit)
        if "certifications" in data:
            y = _draw_section_right(c, "CERTIFICATIONS", data["certifications"], content_x, y - 10, right_limit)

        c.showPage()
        c.save()
        print(f"✅ PDF généré : {output_path}")
        return str(output_path)

    except Exception as e:
        raise RuntimeError(f"Modern CV PDF rendering failed: {str(e)}")


# === PHOTO RONDE ===
def _draw_circular_photo_with_shadow(c, photo_path, x, y, size):
    """Photo ronde avec bord blanc et ombre légère."""
    c.setFillColorRGB(0, 0, 0, alpha=0.15)
    c.circle(x + size / 2 + 3, y + size / 2 - 3, size / 2 + 3, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.circle(x + size / 2, y + size / 2, size / 2, stroke=0, fill=1)
    c.saveState()
    p = c.beginPath()
    p.circle(x + size / 2, y + size / 2, size / 2)
    c.clipPath(p, stroke=0)
    c.drawImage(ImageReader(photo_path), x, y, size, size, mask="auto")
    c.restoreState()


def _sidebar_block(c, title, lines, x, y):
    """Bloc latéral (titre + contenu avec interlignes améliorés)."""
    if not lines:
        return y

    # Titre de section
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#2E2E2E"))
    c.drawString(x, y, title.upper())
    y -= 14  # 🔹 un peu plus d’espace sous le titre

    # Contenu
    c.setFont("Helvetica", 9)
    line_spacing = 12  # 🔹 interligne élargi
    section_spacing = 10  # 🔹 espacement entre paragraphes

    for line in lines:
        if isinstance(line, dict):
            line = ", ".join(f"{k}: {v}" for k, v in line.items() if v)
        elif isinstance(line, list):
            line = ", ".join(str(v) for v in line)
        else:
            line = str(line)

        # Retour à la ligne automatique avec wrapping
        wrapped_lines = wrap(line, 32)
        for w in wrapped_lines:
            c.drawString(x, y, w)
            y -= line_spacing  # 🔹 interligne augmenté
        y -= 2  # petit espace supplémentaire entre les sous-blocs

    return y - section_spacing



# === HEADER DROIT ===
def _draw_header_right(c, personal, x, y, right_limit):
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#2e2e2e"))
    c.drawString(x, y, personal.get("name", "Nom Prénom"))
    y -= 25

    c.setFont("Helvetica-Oblique", 13)
    c.setFillColor(colors.HexColor("#6a0dad"))
    c.drawString(x, y, personal.get("title", "Développeur / Ingénieur"))
    y -= 15
    return y


# === SEPARATEUR ===
def _draw_separator(c, x, y, right_limit):
    c.setStrokeColor(colors.HexColor("#dcdcdc"))
    c.setLineWidth(0.5)
    c.line(x, y, right_limit - 15, y)
    return y - 10


# === SECTION DROITE ===
def _draw_section_right(c, title, items, x, y, right_limit):
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2e2e2e"))
    c.drawString(x, y, title)
    y -= 10

    for item in items:
        y = _draw_entry_right(c, item, x, y, right_limit)
        y -= 10
    return y


# === ENTRÉES (éducation, expérience, etc.) ===
def _draw_entry_right(c, item, x, y, right_limit):
    available_width = right_limit - x - 10
    title_line = item.get("title", "") or item.get("degree", "") or item.get("name", "")
    if "company" in item:
        title_line += f" – {item['company']}"
    if "institution" in item:
        title_line += f" – {item['institution']}"

    # === Titre principal (formation, poste, etc.)
    style_title = ParagraphStyle(
        name="EntryTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#000000"),
    )
    p_title = Paragraph(title_line, style_title)
    _, h_title = p_title.wrap(available_width, 1000)
    p_title.drawOn(c, x, y - h_title)
    y -= h_title + 2  # 🔹 réduit l’espace sous le titre

    # === Dates
    date = item.get("date") or f"{item.get('start_date', '')} - {item.get('end_date', '')}".strip(" -")
    if date:
        y -= 8  # 🔹 espace plus grand au-dessus de la date
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(x, y, date)
        y -= 16  # 🔹 espace légèrement plus grand sous la date
        c.setFillColor(colors.black)

    # === Description justifiée
    desc = item.get("description", "")
    if desc:
        style_desc = ParagraphStyle(
            name="DescJustified",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#333333"),
        )
        p_desc = Paragraph(desc, style_desc)
        _, h_desc = p_desc.wrap(available_width, 1000)
        p_desc.drawOn(c, x, y - h_desc)
        y -= h_desc + 6  # 🔹 resserre encore légèrement les blocs

    return y


# === FLATTEN DES COMPÉTENCES ===
def _flatten_skills(skills):
    if isinstance(skills, dict):
        lines = []
        for category, items in skills.items():
            if items:
                joined = ", ".join(items)
                lines.append(f"{category.capitalize()}: {joined}")
        return lines
    elif isinstance(skills, list):
        return skills
    else:
        return []
