import json
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """You are an expert resume analyst. Analyze the following resume text and return a JSON object with these fields:
- strengths: array of strings, what the resume does well
- weaknesses: array of strings, what is lacking or unclear
- missing_skills: array of strings, in-demand skills not present
- ats_score: integer 0-100, estimated Applicant Tracking System compatibility
- recommendations: array of strings, specific actionable improvements
- suggested_roles: array of strings, which job roles this resume best suits

Resume text:
---
{resume_text}
---

Return ONLY valid JSON, no markdown, no explanation."""


async def analyze_resume(resume_text: str) -> dict:
    settings = get_settings()

    if not settings.gemini_api_key:
        logger.warning("No GEMINI_API_KEY set, returning mock analysis")
        return _mock_analysis(resume_text)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(
            ANALYSIS_PROMPT.format(resume_text=resume_text[:10000])
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return _mock_analysis(resume_text)


def _mock_analysis(resume_text: str) -> dict:
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    skill_keywords = ["python", "javascript", "react", "node", "sql", "aws", "docker", "git", "java", "typescript"]
    found_skills = [s for s in skill_keywords if s.lower() in resume_text.lower()]

    return {
        "strengths": [
            "Clear work experience chronology",
            "Relevant technical skills identified",
            "Good use of action verbs",
        ],
        "weaknesses": [
            "Quantifiable achievements are limited",
            "Summary/objective section could be stronger",
            "Some formatting may not be ATS-friendly",
        ],
        "missing_skills": [s for s in skill_keywords[:5] if s not in found_skills],
        "ats_score": min(65 + len(found_skills) * 5, 95),
        "recommendations": [
            "Add measurable outcomes to each role (e.g., 'Increased X by Y%')",
            "Include a professional summary at the top",
            "Use industry-specific keywords from job descriptions",
            "Consider adding a projects section",
        ],
        "suggested_roles": [
            "Software Engineer",
            "Full Stack Developer",
            "Technical Lead",
        ],
    }
