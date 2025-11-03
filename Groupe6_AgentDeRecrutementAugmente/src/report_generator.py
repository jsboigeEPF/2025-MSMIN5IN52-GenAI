# src/report_generator.py
import os
import openai
from dotenv import load_dotenv
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

PROMPT_TEMPLATE = """
Tu es un assistant qui justifie pourquoi un candidat est classé pour un poste.
Job: {job_text}

Extraits du CV pertinents:
{cv_passages}

Scores calculés:
{scores}

Rédige une justification courte (2-3 phrases) en français.
"""

def generate_report(job_text, cv_passages, scores):
    prompt = PROMPT_TEMPLATE.format(job_text=job_text[:2000], cv_passages="\n".join(cv_passages), scores=scores)
    if not OPENAI_KEY:
        # fallback: simple template without LLM
        return f"Justification (bêta): matched_skills={scores.get('skill')}, exp={scores.get('experience')}"
    resp = openai.Completion.create(  # type: ignore
    model="text-davinci-003",
    prompt="Bonjour",
    max_tokens=50
)

    return resp.choices[0].text.strip()
