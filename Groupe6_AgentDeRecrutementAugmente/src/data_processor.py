# src/data_processor.py
from src.cv_parser import read_file
from src.entity_extractor import extract_entities
from src.job_matcher import total_score
from src.embeddings_index import SimpleFaissIndex
from src.report_generator import generate_report

def process_job_and_cv(job_path, cv_path):
    job_text = read_file(job_path)
    cv_text = read_file(cv_path)
    # extractions
    job_entities = extract_entities(job_text, lang='fr')
    cv_entities = extract_entities(cv_text, lang='fr')
    required_skills = job_entities.get('skills', [])
    req_years = job_entities.get('years', 0)
    cand_skills = cv_entities.get('skills', [])
    cand_years = cv_entities.get('years', 0)
    # score
    total, breakdown = total_score(required_skills, req_years, cand_skills, cand_years)
    # RAG: get top passages (for now, split CV into paragraphs)
    paragraphs = [p.strip() for p in cv_text.split("\n\n") if p.strip()][:50]
    index = SimpleFaissIndex()
    index.add(paragraphs)
    passages = [r['text'] for r in index.search(" ".join(required_skills) or job_text[:200], top_k=3)]
    # report
    report = generate_report(job_text, passages, breakdown)
    result = {
        "job_path": job_path,
        "cv_path": cv_path,
        "score": total,
        "breakdown": breakdown,
        "report": report,
        "matched_skills": list(set(required_skills).intersection(set(cand_skills))),
        "cv_passages": passages
    }
    return result
