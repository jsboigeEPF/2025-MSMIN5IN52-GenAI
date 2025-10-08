# src/entity_extractor.py
import re
import os
import json
from collections import Counter

import spacy
nlp_en = spacy.load("en_core_web_sm") if spacy.util.is_package("en_core_web_sm") else None
nlp_fr = spacy.load("fr_core_news_sm") if spacy.util.is_package("fr_core_news_sm") else None

SKILLS_FILE = "data/skills.json"

def load_skills():
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"Warning: {SKILLS_FILE} not found. Using empty skills list.")
        return []

SKILLS = load_skills()

def extract_years_of_experience(text):
    # cherche "X ans" ou "X years" et retourne la valeur maximale trouvée
    years = re.findall(r"(\d{1,2})\s*(?:ans|an|years|yrs)", text, flags=re.I)
    if years:
        return max(int(y) for y in years)
    return 0

def extract_skills(text, skills_list=SKILLS):
    low = text.lower()
    found = []
    for s in skills_list:
        if s.lower() in low:
            found.append(s)
    return list(sorted(set(found)))

def extract_entities(text, lang='en'):
    # retourne dict de base (skills, years, titles approximatifs)
    out = {}
    out['skills'] = extract_skills(text)
    out['years'] = extract_years_of_experience(text)
    # NER: récupère ORG, PERSON, etc si available
    ents = []
    nlp = nlp_fr if lang.startswith('fr') and nlp_fr else (nlp_en if nlp_en else None)
    if nlp:
        doc = nlp(text[:20000])  # limiter taille
        for ent in doc.ents:
            ents.append((ent.label_, ent.text))
    out['entities'] = ents
    return out
