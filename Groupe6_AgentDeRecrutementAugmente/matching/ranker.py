from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_similarity(jd_text:str, cv_text:str)->float:
    vec = TfidfVectorizer(min_df=1)
    M = vec.fit_transform([jd_text, cv_text])
    return float(cosine_similarity(M[0], M[1])[0,0])

def skill_overlap(jd_skills:set, cv_skills:set)->float:
    if not jd_skills: 
        return 0.0
    return len(jd_skills & cv_skills) / len(jd_skills)

def score_candidate(jd:Dict, cv:Dict, w_tfidf=0.5, w_skills=0.35, w_exp=0.15)->Tuple[float,Dict]:
    """
    jd: {"text", "skills", "years_exp_required"}
    cv: {"name","text","skills","years_exp","path"}
    """
    s_text = tfidf_similarity(jd["text"], cv["text"])
    s_sk = skill_overlap(jd.get("skills",set()), cv.get("skills",set()))

    exp_req = jd.get("years_exp_required", 0.0) or 0.0
    exp_have = cv.get("years_exp", 0.0) or 0.0
    # bonus saturé à 1 si exp >= req, sinon proportion
    s_exp = min(exp_have / (exp_req if exp_req>0 else max(1.0, exp_have)), 1.0)

    total = w_tfidf*s_text + w_skills*s_sk + w_exp*s_exp
    explain = {
        "tfidf_similarity": round(s_text,3),
        "skill_overlap": round(s_sk,3),
        "exp_score": round(s_exp,3),
        "years_required": exp_req,
        "years_have": exp_have
    }
    return float(total), explain

def build_ranking(jd:Dict, cvs:List[Dict])->pd.DataFrame:
    rows = []
    for cv in cvs:
        score, expl = score_candidate(jd, cv)
        rows.append({
            "Candidat": cv.get("name","(CV)"),
            "Score": round(score, 4),
            "TextSim": expl["tfidf_similarity"],
            "Skills": expl["skill_overlap"],
            "Exp": expl["exp_score"],
            "Années_req": expl["years_required"],
            "Années_cv": expl["years_have"],
            "Fichier": cv.get("path","")
        })
    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
    return df
