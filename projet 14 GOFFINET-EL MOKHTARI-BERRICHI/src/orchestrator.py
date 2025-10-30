from typing import Dict, Any
from src.agents.cv_agent import process_cv
from src.agents.invoice_agent import process_invoice
from src.agents.report_agent import process_report
from src.renderers.pdf_cv import render_pdf_cv
from src.renderers.pdf_invoice import render_pdf_invoice
from src.renderers.pdf_report import render_pdf_report
from src.utils.validate import validate_data


class Orchestrator:
    """Coordonne les agents pour générer différents types de documents."""

    def generate_document(self, doc_type: str, data: Dict[str, Any]) -> str:
        """Génère un document structuré (CV, facture, rapport)."""
        try:
            validate_data(data, doc_type)

            if doc_type == "cv":
                processed = process_cv(data)
                return render_pdf_cv(processed)

            elif doc_type == "invoice":
                processed = process_invoice(data)
                return render_pdf_invoice(processed)

            elif doc_type == "report":
                processed = process_report(data)
                return render_pdf_report(processed)

            else:
                raise ValueError(f"Type de document non pris en charge : {doc_type}")

        except Exception as e:
            raise RuntimeError(f"Erreur d'orchestration : {str(e)}")


# Instance unique à importer partout
orchestrator = Orchestrator()
