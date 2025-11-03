import os, shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd

from matching.parse import is_allowed, read_any, normalize_text
from matching.ner import extract_entities, rule_extract_skills, rule_extract_years_exp
from matching.ranker import build_ranking
from matching.rag import chunk_requirements, retrieve_top_requirements

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "change-me"

def safe_filename(name:str)->str:
    return name.replace(" ", "_")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/match", methods=["POST"])
def match():
    # 1) Fiche de poste (texte ou fichier)
    jd_text = request.form.get("jd_text","").strip()
    jd_required_years = request.form.get("jd_years","").strip()
    try:
        jd_required_years = float(jd_required_years) if jd_required_years else 0.0
    except:
        jd_required_years = 0.0

    jd_file = request.files.get("jd_file")
    if jd_file and jd_file.filename and is_allowed(jd_file.filename):
        path = os.path.join(UPLOAD_DIR, safe_filename(jd_file.filename))
        jd_file.save(path)
        jd_text_file = read_any(path)
        if jd_text_file:
            jd_text = (jd_text + "\n" + jd_text_file).strip() if jd_text else jd_text_file

    if not jd_text:
        flash("Merci de fournir une fiche de poste (texte ou fichier PDF/DOCX/TXT).")
        return redirect(url_for("index"))

    jd_text = normalize_text(jd_text)
    jd_skills = rule_extract_skills(jd_text)

    # 2) Lot de CV
    cv_files = request.files.getlist("cv_files")
    cvs = []
    for f in cv_files:
        if not f or not f.filename:
            continue
        if not is_allowed(f.filename):
            continue
        path = os.path.join(UPLOAD_DIR, safe_filename(f.filename))
        f.save(path)
        text = normalize_text(read_any(path))
        if not text:
            continue
        ents = extract_entities(text, lang_code="fr")
        name_guess = os.path.splitext(os.path.basename(path))[0]
        cvs.append({
            "name": name_guess,
            "text": text,
            "skills": ents["skills"],
            "years_exp": ents["years_exp"],
            "path": path
        })

    if not cvs:
        flash("Aucun CV valide reçu (formats acceptés: PDF, DOCX, TXT).")
        return redirect(url_for("index"))

    # 3) RAG-lite: exigences récupérées
    jd_chunks = chunk_requirements(jd_text)

    # 4) Matching + ranking
    jd_dict = {"text": jd_text, "skills": jd_skills, "years_exp_required": jd_required_years}
    df = build_ranking(jd_dict, cvs)

    # 5) Justification détaillée par candidat (top exigences “retrouvées”)
    justifs = {}
    for cv in cvs:
        tops = retrieve_top_requirements(jd_chunks, cv["text"], k=3)
        justifs[cv["path"]] = [{"requirement": r, "score": round(s,3)} for r,s in tops]

    # 6) Export CSV
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = os.path.join(OUTPUT_DIR, f"classement_{stamp}.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8")

    return render_template("results.html",
                           df=df.to_dict(orient="records"),
                           jd_skills=sorted(list(jd_skills)),
                           jd_years=jd_required_years,
                           justifs=justifs,
                           csv_path=os.path.basename(out_csv))

@app.route("/download/<path:filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.isfile(path):
        return send_file(path, as_attachment=True)
    return "Not found", 404

if __name__ == "__main__":
    print(">>> starting Flask")
    app.run(host="0.0.0.0", port=5000, debug=True)

