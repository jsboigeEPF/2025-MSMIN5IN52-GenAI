from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from src.utils.validate import validate_data
from src.orchestrator import orchestrator
from src.agents.semantic_agent import process_prompt_to_json
from pathlib import Path


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
from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from pathlib import Path
import json
from src.utils.validate import validate_data
from src.orchestrator import orchestrator
from src.agents.semantic_agent import process_prompt_to_json

router = APIRouter()

@router.post("/semantic/{doc_type}")
async def generate_from_prompt(
    request: Request,
    doc_type: str,
    prompt: str = Form(None),
    photo: UploadFile = File(None)
):
    try:
        print("\n🧠 [DEBUG] Nouvelle requête reçue !")
        print("   ➤ Type de document :", doc_type)
        content_type = request.headers.get("content-type", "")
        print("   ➤ Content-Type :", content_type)

        # ============================================================
        # 🔹 Cas 1 : Requête multipart (CV avec photo)
        # ============================================================
        if "multipart/form-data" in content_type:
            if not prompt:
                raise ValueError("Le champ 'prompt' est manquant dans le formulaire multipart.")
            prompt_value = prompt

            # Gestion de la photo
            photo_path = None
            if photo and doc_type.lower() == "cv":
                tmp_dir = Path("out/tmp")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                photo_path = tmp_dir / photo.filename
                with open(photo_path, "wb") as f:
                    f.write(await photo.read())
                print("   ➤ Photo sauvegardée :", photo_path)

        # ============================================================
        # 🔹 Cas 2 : Requête JSON (report ou invoice)
        # ============================================================
        elif "application/json" in content_type:
            raw_body = await request.body()
            print("   ➤ RAW BODY reçu :", raw_body.decode())

            try:
                payload = json.loads(raw_body.decode()) if raw_body else {}
            except json.JSONDecodeError:
                raise ValueError("Impossible de parser le JSON reçu.")

            prompt_value = payload.get("prompt")
            if not prompt_value:
                raise ValueError("Le champ 'prompt' est manquant dans le JSON.")
            photo_path = None

        else:
            raise ValueError(f"Type de contenu non supporté : {content_type}")

        # ============================================================
        # 🔹 Étape 2 : Transformation sémantique via OpenAI
        # ============================================================
        structured_data = await process_prompt_to_json(prompt_value, doc_type)

        if photo_path:
            structured_data.setdefault("personal_info", {})["photo"] = str(photo_path)

        # ============================================================
        # 🔹 Étape 3 : Génération du PDF
        # ============================================================
        output_path = orchestrator.generate_document(doc_type, structured_data)
        print("✅ PDF généré :", output_path)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=Path(output_path).name,
            headers={"Content-Disposition": f"attachment; filename={Path(output_path).name}"}
        )

    except Exception as e:
        print("❌ ERREUR :", str(e))
        raise HTTPException(status_code=400, detail=str(e))

