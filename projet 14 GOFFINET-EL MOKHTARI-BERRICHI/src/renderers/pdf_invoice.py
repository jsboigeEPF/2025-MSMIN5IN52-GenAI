from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def render_pdf_invoice(data: dict) -> str:
    """Facture PDF — alignement final équilibré (rendu exact comme la 2ᵉ image)."""

    # === Valeurs par défaut ===
    defaults = {
        "invoice_number": "INV-0000",
        "issue_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": "",
        "seller": {
            "name": "IMSA Solutions",
            "address": "10 rue des Startups, Paris",
            "siret": "FR000000000",
            "vat_number": "FR000000000",
            "email": "contact@imsa.com",
            "phone": "+33 1 23 45 67 89",
            "bank": {
                "bank_name": "Crédit Agricole",
                "account_holder": "IMSA Solutions",
                "iban": "FR76 0000 0000 0000 0000 0000 000",
                "bic": "AGRIFRPPXXX"
            }
        },
        "client": {
            "name": "EPF École d’ingénieurs",
            "contact_person": "",
            "email": "",
            "address": "3 rue Lakanal, Cachan",
            "vat_number": ""
        },
        "items": [],
        "subtotal_ht": 0.0,
        "tax_rate": 20.0,
        "tax_amount": 0.0,
        "total_ttc": 0.0,
        "currency": "EUR",
        "payment_terms": "Virement sous 30 jours",
        "late_penalties": {
            "rate": "10% par mois de retard",
            "fixed_fee": "40 euros",
            "legal_reference": "article L441-10 du Code de commerce"
        }
    }

    data = {**defaults, **data}

    # === Création PDF ===
    os.makedirs("out/invoice", exist_ok=True)
    path = f"out/invoice/invoice_{data['invoice_number']}.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    Y_OFFSET = 35  # valeur en points, ~9 mm


    # Bande lavande
    c.setFillColor(colors.HexColor("#EAE6FF"))
    c.rect(0, 0, 20 * mm, height, fill=1, stroke=0)

    # Titre et méta
    c.setFillColor(colors.HexColor("#4B0082"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(35 * mm, height - (40 + Y_OFFSET), "FACTURE")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawRightString(width - 40, height - 40, f"N° {data['invoice_number']}")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, height - 55, f"Date d’émission : {data['issue_date']}")
    if data.get("due_date"):
        c.drawRightString(width - 40, height - 70, f"Date d’échéance : {data['due_date']}")

    # Émetteur
    seller = data["seller"]
    c.setFont("Helvetica-Bold", 11)
    c.drawString(35 * mm, height - (100 + Y_OFFSET), seller["name"])
    c.setFont("Helvetica", 9)
    y = height - (115 + Y_OFFSET)
    for line in [
        seller["address"],
        f"SIRET : {seller.get('siret','')}",
        f"TVA : {seller.get('vat_number','')}",
        f"Email : {seller.get('email','')}",
        f"Téléphone : {seller.get('phone','')}"
    ]:
        c.drawString(35 * mm, y, line)
        y -= 12

    # Client
    client = data["client"]
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.red)
    c.drawString(120 * mm, height - (100 + Y_OFFSET), "Facturé à :")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    y_client = height - (115 + Y_OFFSET)
    for line in [
        client.get("name", ""),
        f"Contact : {client.get('contact_person','')}" if client.get("contact_person") else "",
        client.get("address", ""),
        f"Email : {client.get('email','')}" if client.get("email") else "",
        f"TVA : {client.get('vat_number','')}" if client.get("vat_number") else ""
    ]:
        if line:
            c.drawString(120 * mm, y_client, line)
            y_client -= 12

    # === Colonnes (recentrées proprement) ===
    X_DESC = 35 * mm
    X_QTY = 120 * mm
    X_UNIT = 140 * mm   # ← +10 mm (recentré)
    X_TOTAL = 170 * mm  # ← +10 mm (recentré)

    # En-tête du tableau
    y = height - (230 + Y_OFFSET)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(X_DESC, y, "Description")
    c.drawString(X_QTY, y, "Qté")
    c.drawString(X_UNIT, y, "Prix U. (€)")
    c.drawString(X_TOTAL, y, "Total (€)")

    # Ligne sous entête
    c.setLineWidth(1)
    c.line(X_DESC, y - 3, width - 25 * mm, y - 3)
    y -= 15

    # Lignes du tableau
    c.setFont("Helvetica", 9)
    alt_color = colors.HexColor("#F5F5F5")
    row_height = 7 * mm
    for i, item in enumerate(data["items"]):
        if i % 2 == 1:
            c.setFillColor(alt_color)
            c.rect(X_DESC, y - 2.5 * mm, width - 60 * mm, row_height, fill=1, stroke=0)
            c.setFillColor(colors.black)

        c.drawString(X_DESC, y, item.get("description", ""))
        c.drawRightString(X_QTY + 8, y, str(item.get("quantity", 1)))
        c.drawRightString(X_UNIT + 35, y, f"{item.get('unit_price_ht', 0):.2f}")
        c.drawRightString(X_TOTAL + 35, y, f"{item.get('total_ht', 0):.2f}")
        y -= row_height

    # === Bloc des totaux — poussé à droite ===
    y -= 6
    X_RIGHT_MARGIN = width - 25 * mm  # marge droite esthétique

    # Ligne de séparation
    c.line(X_UNIT, y, X_RIGHT_MARGIN, y)

    # Texte aligné à droite (proche du bord droit)
    y -= 12
    c.setFont("Helvetica", 9)
    c.drawRightString(X_RIGHT_MARGIN, y, f"Sous-total HT : {data['subtotal_ht']:.2f} €")
    y -= 10
    c.drawRightString(X_RIGHT_MARGIN, y, f"TVA ({data['tax_rate']}%) : {data['tax_amount']:.2f} €")

    # Total TTC — en violet, gras et souligné
    y -= 18
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#4B0082"))
    c.drawRightString(X_RIGHT_MARGIN, y, f"TOTAL TTC : {data['total_ttc']:.2f} €")


    # Coordonnées bancaires
    c.setFillColor(colors.black)
    y -= 30
    bank = seller["bank"]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35 * mm, y, "Coordonnées bancaires :")
    y -= 10
    c.setFont("Helvetica", 9)
    for line in [
        f"Banque : {bank.get('bank_name','')}",
        f"Titulaires : {bank.get('account_holder','')}",
        f"IBAN : {bank.get('iban','')}",
        f"BIC : {bank.get('bic','')}"
    ]:
        c.drawString(35 * mm, y, line)
        y -= 9

    # Conditions
    y -= 15
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(35 * mm, y, f"Conditions de paiement : {data['payment_terms']}")
    y -= 10
    p = data["late_penalties"]
    if p.get("rate"):
        c.drawString(35 * mm, y, f"Pénalités de retard : {p['rate']}")
        y -= 10
    if p.get("fixed_fee"):
        c.drawString(35 * mm, y, f"Indemnité fixe : {p['fixed_fee']}")
        y -= 10
    if p.get("legal_reference"):
        c.drawString(35 * mm, y, f"Référence légale : {p['legal_reference']}")

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 15 * mm, "Document généré automatiquement — EPF Semantic Agent")

    c.save()
    return path
