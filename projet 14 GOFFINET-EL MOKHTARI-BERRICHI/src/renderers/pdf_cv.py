from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from typing import Dict, Any
from pathlib import Path
from src.utils.file_utils import ensure_dir

def render_pdf_cv(data: Dict[str, Any]) -> str:
    """Render CV data to PDF format using ReportLab."""
    try:
        # Create output directory
        output_dir = Path("out/cv")
        ensure_dir(output_dir)
        name = data.get("personal", {}).get("name", "cv").replace(" ", "_")
        output_path = output_dir / f"{name}_cv.pdf"

        # Setup canvas
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4
        y = height - 40

        # === Personal Information ===
        _add_personal_info(c, data.get("personal", {}), y)
        y -= 100

        # === Experience ===
        if "experience" in data:
            y = _add_section(c, "Experience", data["experience"], y - 10)

        # === Education ===
        if "education" in data:
            y = _add_section(c, "Education", data["education"], y - 10)

        # === Skills ===
        if "skills" in data:
            y = _add_section(c, "Skills", data["skills"], y - 10)

        c.showPage()
        c.save()
        return str(output_path)

    except Exception as e:
        raise RuntimeError(f"CV PDF rendering failed: {str(e)}")


def _add_personal_info(c: canvas.Canvas, personal: Dict[str, Any], y: int):
    """Add personal information section"""
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(105 * mm, y, personal.get("name", "Unnamed"))
    y -= 15

    c.setFont("Helvetica", 11)
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    location = personal.get("location", "")

    if email:
        c.drawCentredString(105 * mm, y, f"Email: {email}")
        y -= 12
    if phone:
        c.drawCentredString(105 * mm, y, f"Phone: {phone}")
        y -= 12
    if location:
        c.drawCentredString(105 * mm, y, f"Location: {location}")
        y -= 12


def _add_section(c: canvas.Canvas, title: str, items: list, y: int) -> int:
    """Add a formatted section with multiple items"""
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawString(30, y, title)
    y -= 20

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)

    for item in items:
        if isinstance(item, dict):
            for key, value in item.items():
                if key in ["title", "position"]:
                    c.setFont("Helvetica-Bold", 11)
                    c.drawString(40, y, value)
                    y -= 14
                elif key in ["company", "institution"]:
                    c.setFont("Helvetica-Oblique", 10)
                    c.drawString(45, y, value)
                    y -= 12
                elif key == "date":
                    c.setFont("Helvetica", 9)
                    c.drawString(45, y, f"Date: {value}")
                    y -= 12
                elif key == "description":
                    c.setFont("Helvetica", 10)
                    for line in value.split("\n"):
                        c.drawString(50, y, line)
                        y -= 12
        else:
            c.drawString(40, y, str(item))
            y -= 12
        y -= 6  # space between entries

        if y < 100:  # Add a new page if reaching bottom
            c.showPage()
            y = A4[1] - 50
            c.setFont("Helvetica", 11)
    return y
