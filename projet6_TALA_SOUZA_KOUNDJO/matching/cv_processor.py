"""
Enhanced CV processing module for extracting structured information from CVs
and generating standardized descriptions using LLM.
"""
import re
import os
import json
import asyncio
from typing import Dict, List, Set, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# OpenAI API configuration
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

async def extract_cv_info_with_llm(cv_text: str, api_key: str) -> Dict:
    """Use LLM to extract structured information from CV"""
    
    prompt = f"""Analyze this CV and extract the following information in JSON format:
- name: Full name of the candidate
- email: Email address
- phone: Phone number
- location: City/Location
- summary: Brief professional summary (2-3 sentences)
- experience: List of work experiences with role, company, and period
- education: List of educational qualifications
- skills: List of technical skills

CV Text:
{cv_text[:3000]}

Return ONLY valid JSON with this structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1234567890",
  "location": "City, Country",
  "summary": "Professional summary here",
  "experience": ["Role at Company (Period)", "Role at Company (Period)"],
  "education": ["Degree from University (Year)"],
  "skills": ["skill1", "skill2", "skill3"]
}}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert HR assistant that extracts structured information from CVs. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENAI_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"[DEBUG] OpenAI response status: {response.status_code}")
            
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"].strip()
                print(f"[DEBUG] LLM raw response: {content[:500]}...")
                
                # Try to extract JSON from response
                # Sometimes LLM wraps JSON in markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                try:
                    cv_data = json.loads(content)
                    print(f"[DEBUG] Successfully parsed JSON: {list(cv_data.keys())}")
                    return cv_data
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON decode error: {e}")
                    print(f"[ERROR] Content: {content}")
                    return get_fallback_data()
            
            print(f"[ERROR] No choices in response: {result}")
            return get_fallback_data()
            
    except Exception as e:
        print(f"[ERROR] Exception calling LLM: {e}")
        import traceback
        traceback.print_exc()
        return get_fallback_data()

def get_fallback_data() -> Dict:
    """Return default structure when LLM extraction fails"""
    return {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "experience": [],
        "education": [],
        "skills": []
    }

def generate_standardized_description(cv_data: Dict, candidate_id: int = None) -> str:
    """Generate a standardized CV description from extracted data"""
    parts = []
    
    # Add name with fallback
    name = cv_data.get("name", "").strip()
    if name:
        parts.append(f"Name: {name}")
    elif candidate_id:
        parts.append(f"Name: Candidat {candidate_id}")
    
    # Add contact information
    contact_lines = []
    if cv_data.get("email"):
        contact_lines.append(f"Email: {cv_data['email']}")
    if cv_data.get("phone"):
        contact_lines.append(f"Phone: {cv_data['phone']}")
    if cv_data.get("location"):
        contact_lines.append(f"Location: {cv_data['location']}")
    if contact_lines:
        parts.append("Contact Information:\n" + "\n".join(contact_lines))
    
    # Add summary
    if cv_data.get("summary"):
        parts.append(f"Summary:\n{cv_data['summary']}")
    
    # Add work experience
    if cv_data.get("experience") and len(cv_data["experience"]) > 0:
        parts.append("Work Experience:")
        for exp in cv_data["experience"]:
            if isinstance(exp, str):
                parts.append(f"- {exp}")
            elif isinstance(exp, dict):
                exp_line = exp.get("role", "")
                if exp.get("company"):
                    exp_line += f" at {exp['company']}"
                if exp.get("period"):
                    exp_line += f" ({exp['period']})"
                if exp_line:
                    parts.append(f"- {exp_line}")
    
    # Add education
    if cv_data.get("education") and len(cv_data["education"]) > 0:
        parts.append("Education:")
        for edu in cv_data["education"]:
            if isinstance(edu, str):
                parts.append(f"- {edu}")
            elif isinstance(edu, dict):
                edu_line = edu.get("degree", "")
                if edu.get("institution"):
                    edu_line += f" from {edu['institution']}"
                if edu.get("year"):
                    edu_line += f" ({edu['year']})"
                if edu_line:
                    parts.append(f"- {edu_line}")
    
    # Add skills
    if cv_data.get("skills") and len(cv_data["skills"]) > 0:
        skills_list = cv_data["skills"]
        if isinstance(skills_list, list):
            parts.append(f"Skills:\n{', '.join(skills_list)}")
        elif isinstance(skills_list, str):
            parts.append(f"Skills:\n{skills_list}")
    
    return "\n\n".join(parts)

def process_cv_text(text: str, api_key: str) -> Dict:
    """Process CV text and return structured data using LLM"""
    try:
        # Run async function in sync context
        cv_data = asyncio.run(extract_cv_info_with_llm(text, api_key))
        print(f"[DEBUG] Extracted CV data: {cv_data}")
        return cv_data
    except Exception as e:
        print(f"Error processing CV: {e}")
        import traceback
        traceback.print_exc()
        return get_fallback_data()

def create_cv_entry(text: str, file_id: int, api_key: str) -> Dict:
    """Create a complete CV entry for the CSV"""
    cv_data = process_cv_text(text, api_key)
    standardized_desc = generate_standardized_description(cv_data, candidate_id=file_id)
    
    # If the standardized description is too short (LLM failed), use raw text
    if len(standardized_desc) < 50:
        print(f"[WARNING] Generated description too short for CV {file_id}, using raw text")
        # Clean and truncate the raw text
        cleaned_text = " ".join(text.split())  # Remove extra whitespace
        standardized_desc = f"Name: Candidat {file_id}\n\nRaw CV Text:\n{cleaned_text[:2000]}"
    
    return {
        "ID": file_id,
        "Resume": standardized_desc
    }
