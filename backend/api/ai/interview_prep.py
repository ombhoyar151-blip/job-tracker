import json
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)

PREP_PROMPT = """You are an expert interview coach. Based on the following job description and required skills, generate 8 relevant interview practice questions.

Return a JSON object with these fields:
- role: the target job title
- questions: array of objects, each with:
  - question: string, the interview question
  - type: "technical" | "behavioral" | "situational" | "general"
  - focus_area: string, what skill or trait this tests
  - suggested_answer: string, a brief strong answer outline

Job title: {job_title}
Job description:
---
{description}
---
Required skills: {skills}

Return ONLY valid JSON, no markdown, no explanation."""

MOCK_QUESTIONS = [
    {"question": "Walk me through your experience with the core technologies listed in this role.", "type": "technical", "focus_area": "Technical proficiency", "suggested_answer": "Structure your answer chronologically, mention specific projects and technologies used, and connect each experience back to the job requirements."},
    {"question": "Describe a challenging technical problem you solved recently.", "type": "technical", "focus_area": "Problem-solving", "suggested_answer": "Use the STAR method: Situation, Task, Action, Result. Highlight your analytical process and the outcome."},
    {"question": "How do you stay current with industry trends and new technologies?", "type": "behavioral", "focus_area": "Continuous learning", "suggested_answer": "Mention specific resources (blogs, courses, conferences), side projects, and how you've applied new learning to your work."},
    {"question": "Tell me about a time you had to work under a tight deadline.", "type": "situational", "focus_area": "Time management", "suggested_answer": "Describe how you prioritized tasks, communicated with stakeholders, and what the outcome was."},
    {"question": "Why are you interested in this role and our company?", "type": "general", "focus_area": "Motivation and fit", "suggested_answer": "Research the company beforehand. Connect their mission or recent work to your own career goals and skills."},
    {"question": "Describe a situation where you disagreed with a team member.", "type": "behavioral", "focus_area": "Collaboration", "suggested_answer": "Focus on respectful communication, finding common ground, and reaching a constructive resolution."},
    {"question": "How do you approach testing and quality assurance in your work?", "type": "technical", "focus_area": "Quality mindset", "suggested_answer": "Discuss your testing strategy (unit, integration, e2e), tooling, and how you balance speed with quality."},
    {"question": "Where do you see your career in the next 3-5 years?", "type": "general", "focus_area": "Career vision", "suggested_answer": "Align your aspirations with what the role and company can offer. Show ambition but also commitment."},
]


async def generate_questions(job_title: str, description: str, skills: list | None = None) -> dict:
    settings = get_settings()

    if not settings.gemini_api_key:
        logger.warning("No GEMINI_API_KEY set, returning mock questions")
        return _mock_questions(job_title)

    skill_text = ", ".join(skills) if skills else "Not specified"
    prompt = PREP_PROMPT.format(
        job_title=job_title,
        description=(description or "")[:5000],
        skills=skill_text,
    )

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Gemini question generation failed: {e}")
        return _mock_questions(job_title)


def _mock_questions(job_title: str) -> dict:
    return {
        "role": job_title,
        "questions": MOCK_QUESTIONS,
    }
