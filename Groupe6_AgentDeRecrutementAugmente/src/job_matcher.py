# src/job_matcher.py
from typing import Dict, List

def skill_score(required: List[str], candidate: List[str]) -> float:
    if not required:
        return 0.0
    req = set([r.lower() for r in required])
    cand = set([c.lower() for c in candidate])
    matched = req & cand
    return len(matched) / len(req)

def experience_score(required_years: int, candidate_years: int) -> float:
    if required_years <= 0:
        return 0.0
    return min(1.0, candidate_years / required_years)

def total_score(required_skills, required_years, candidate_skills, candidate_years, weights=None):
    if weights is None:
        weights = {"skills": 0.6, "experience": 0.3, "others": 0.1}
    s_skill = skill_score(required_skills, candidate_skills)
    s_exp = experience_score(required_years, candidate_years)
    s_others = 0.0
    total = weights["skills"]*s_skill + weights["experience"]*s_exp + weights["others"]*s_others
    return round(total, 4), {"skill": round(s_skill,3), "experience": round(s_exp,3), "others": s_others}
