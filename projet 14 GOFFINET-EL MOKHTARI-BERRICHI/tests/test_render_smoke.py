import os
from src.renderers.pdf_cv import render_pdf_cv
from src.renderers.pdf_invoice import render_pdf_invoice
from src.renderers.pdf_report import render_pdf_report

def test_render_cv():
    data = {
        "personal": {"name": "John Doe", "email": "john@ex.com", "phone": "000", "location": "Paris"},
        "experience": [],
        "education": [],
        "skills": []
    }
    path = render_pdf_cv(data)
    assert os.path.exists(path)
    os.remove(path)

def test_render_invoice():
    data = {
        "invoice_number": "INV-001",
        "company": {"name": "TechCorp", "address": "1 Rue Exemple", "city": "Paris", "vat_number": "FR123"},
        "client": {"name": "ACME", "address": "NYC", "city": "New York"},
        "items": [],
        "subtotal": 0,
        "tax_rate": 0,
        "tax_amount": 0,
        "total": 0
    }
    path = render_pdf_invoice(data)
    assert os.path.exists(path)
    os.remove(path)

def test_render_report():
    data = {
        "title": "Annual Report",
        "author": "Jane Smith",
        "date": "2025-10-30",
        "report_id": "R001",
        "sections": []
    }
    path = render_pdf_report(data)
    assert os.path.exists(path)
    os.remove(path)
