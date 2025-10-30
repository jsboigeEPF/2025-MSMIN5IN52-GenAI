from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from src.utils.validate import validate_data
from src.orchestrator import orchestrator
from src.agents.semantic_agent import process_prompt_to_json

router = APIRouter()

# ---------- CV ----------
@router.post("/cv")
async def create_cv(data: dict = Body(...)):
    """Generate a CV PDF from structured data"""
    try:
        output_path = orchestrator.generate_document("cv", data)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.split("/")[-1]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- INVOICE ----------
@router.post("/invoice")
async def create_invoice(data: dict = Body(...)):
    """Generate an Invoice PDF from structured data"""
    try:
        output_path = orchestrator.generate_document("invoice", data)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.split("/")[-1]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- REPORT ----------
@router.post("/report")
async def create_report(data: dict = Body(...)):
    """Generate a Report PDF from structured data"""
    try:
        output_path = orchestrator.generate_document("report", data)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.split("/")[-1]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- SEMANTIC AGENT ----------
@router.post("/semantic/{doc_type}")
async def generate_from_prompt(doc_type: str, payload: dict = Body(...)):
    """
    Generate a structured document from a natural language prompt.
    Example:
    {
        "prompt": "Crée un CV pour Safae Berrichi, ingénieure en informatique à l'EPF..."
    }
    """
    try:
        # 1️⃣ Extraire le prompt du body
        prompt = payload.get("prompt")
        if not prompt:
            raise ValueError("Le champ 'prompt' est requis.")

        # 2️⃣ Convertir le texte en données structurées via Semantic Agent
        structured_data = await process_prompt_to_json(prompt, doc_type)

        # 3️⃣ Générer le PDF via Orchestrator
        output_path = orchestrator.generate_document(doc_type, structured_data)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.split("/")[-1]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
