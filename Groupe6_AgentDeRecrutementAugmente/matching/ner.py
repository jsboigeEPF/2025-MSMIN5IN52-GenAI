import re
from typing import Dict, List, Set, Optional

# Petit lexique de démo ; à enrichir selon ton contexte
SKILLS = {
    "python","pandas","numpy","scikit-learn","tensorflow","pytorch",
    "sql","power bi","excel","databricks","spark","docker","kubernetes",
    "java","javascript","typescript","angular","react","flask","fastapi",
    "nlp","ocr","dataiku","airflow","git","azure","gcp","aws"
}

DEGREES = {"licence","bachelor","master","ingénieur","m2","bac+5","phd","doctorat"}

def normalize_lower(s:str)->str:
    return re.sub(r"\s+", " ", s.lower()).strip()

def rule_extract_skills(text:str)->Set[str]:
    t = normalize_lower(text)
    hits = set()
    for k in SKILLS:
        if k in t:
            hits.add(k)
    return hits

def rule_extract_years_exp(text:str)->float:
    # Ex: "3 ans d’expérience", "5+ years", "2 ans", "2-3 ans"
    t = normalize_lower(text)
    years = []
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(?:\+)?\s*(ans|an|years|year)", t):
        try:
            years.append(float(m.group(1).replace(",", ".")))
        except:
            pass
    return max(years) if years else 0.0

def rule_extract_degrees(text:str)->Set[str]:
    t = normalize_lower(text)
    return {d for d in DEGREES if d in t}

# spaCy optionnel
_nlp = None
def try_spacy(lang_code:Optional[str]="fr"):
    global _nlp
    if _nlp is not None:
        return _nlp
    try:
        import spacy
        model = "fr_core_news_sm" if lang_code=="fr" else "en_core_web_sm"
        _nlp = spacy.load(model)
        return _nlp
    except Exception:
        return None

def extract_entities(text:str, lang_code:str="fr")->Dict:
    """
    Retourne un dict: {skills:set, degrees:set, years_exp:float, persons:set, orgs:set}
    """
    skills = rule_extract_skills(text)
    degrees = rule_extract_degrees(text)
    years = rule_extract_years_exp(text)
    persons, orgs = set(), set()

    nlp = try_spacy(lang_code)
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in {"PER","PERSON"}:
                persons.add(ent.text)
            if ent.label_ in {"ORG","ORGANIZATION"}:
                orgs.add(ent.text)
    return {
        "skills": skills,
        "degrees": degrees,
        "years_exp": years,
        "persons": persons,
        "orgs": orgs
    }
