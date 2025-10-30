from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
import json

def render_pdf_invoice(data: dict) -> str:
    """
    Génère un PDF de facture à partir d'un dictionnaire structuré.
    Si des données manquent, des valeurs par défaut sont utilisées.
    """

    # === 🔍 Étape 1 : fallback automatique ===
    defaults = {
        "invoice_number": "INV-0000",
        "date": "2025-10-30",
        "company": {"name": "IMSA Solutions", "address": "10 rue des Startups, Paris", "vat_number": "FR000000000"},
        "client": {"name": "EPF École d’ingénieurs", "address": "3 rue Lakanal, Cachan"},
        "items": [
            {"description": "Développement Web", "quantity": 10, "unit_price": 50, "total": 500},
            {"description": "Maintenance", "quantity": 5, "unit_price": 60, "total": 300},
        ],
        "subtotal": 800,
        "tax_rate": 20,
        "tax_amount": 160,
        "total": 960,
        "payment_terms": "Virement sous 30 jours",
    }

    # Fusionner données réelles et valeurs par défaut
    def merge_data(base, override):
        for k, v in override.items():
            if isinstance(v, dict):
                base[k] = merge_data(base.get(k, {}), v)
            else:
                base.setdefault(k, v)
        return base

    data = merge_data(data if isinstance(data, dict) else {}, defaults)

    # === 🔍 Étape 2 : log JSON brut pour debug ===
    os.makedirs("out/invoice", exist_ok=True)
    with open("out/invoice/last_invoice_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # === 🧾 Étape 3 : création du PDF ===
    output_path = f"out/invoice/out_invoice_{data['invoice_number']}.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)

    width, height = A4

    # --- En-tête ---
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(400, height - 50, f"INVOICE #{data['invoice_number']}")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(400, height - 65, f"Date: {data['date']}")

    # --- Émetteur ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 100, data["company"]["name"])
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 115, data["company"]["address"])
    c.drawString(40, height - 130, f"TVA: {data['company']['vat_number']}")

    # --- Client ---
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.red)
    c.drawString(40, height - 160, "Bill To:")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 160, data["client"]["name"])
    c.drawString(100, height - 175, data["client"]["address"])

    # --- Tableau des articles ---
    y = height - 220
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Description")
    c.drawString(250, y, "Qty")
    c.drawString(300, y, "Unit Price (€)")
    c.drawString(400, y, "Total (€)")
    y -= 15
    c.setFont("Helvetica", 10)

    for item in data["items"]:
        c.drawString(40, y, item["description"])
        c.drawString(260, y, str(item["quantity"]))
        c.drawString(310, y, f"{item['unit_price']:.2f}")
        c.drawString(410, y, f"{item['total']:.2f}")
        y -= 15

    # --- Totaux ---
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(500, y, f"Subtotal: {data['subtotal']:.2f}")
    y -= 15
    c.drawRightString(500, y, f"Tax ({data['tax_rate']}%): {data['tax_amount']:.2f}")
    y -= 15
    c.setFillColor(colors.darkblue)
    c.drawRightString(500, y, f"TOTAL: {data['total']:.2f}")
    c.setFillColor(colors.black)

    # --- Conditions ---
    y -= 30
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, y, f"Conditions de paiement : {data['payment_terms']}")

    c.save()
    return output_path
