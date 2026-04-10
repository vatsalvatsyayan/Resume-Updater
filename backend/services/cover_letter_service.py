from schemas.cover_letter import CoverLetterRequest
from services import llm_client, company_research_service


def _extract_profile_summary(profile_data: dict) -> dict:
    """Extract fields needed for the prompt from the optimized resume JSON.

    Handles the optimized resume schema produced by the resume optimization
    service, which differs from the raw ProfileFormData frontend shape.
    """
    name = profile_data.get("Name", "Applicant")

    # --- Experience ---
    experience_lines = []
    for job in profile_data.get("Experience", []):
        role = job.get("Role", "")
        company = job.get("Company", "")
        duration = job.get("Duration", "")
        header = f"- {role} at {company} ({duration})"
        experience_lines.append(header)

        # job1 style: flat list of responsibility strings
        responsibilities = job.get("Responsibilities", [])
        for r in responsibilities:
            experience_lines.append(f"    • {r}")

        # job2 style: nested projects, each with a Name and Details list
        for proj in job.get("Projects", []):
            proj_name = proj.get("Name", "")
            if proj_name:
                experience_lines.append(f"    [{proj_name}]")
            for detail in proj.get("Details", []):
                experience_lines.append(f"      • {detail}")

    # --- Skills ---
    # Both jobs use a dict of {category: [skill, ...]} with varying category names
    all_skills: list[str] = []
    for category_skills in profile_data.get("Skills", {}).values():
        if isinstance(category_skills, list):
            all_skills.extend(str(s) for s in category_skills if s)
    skills_text = ", ".join(all_skills[:25])  # cap to keep prompt concise

    # --- Education ---
    education_lines = []
    for edu in profile_data.get("Education", []):
        degree = edu.get("Degree", "")
        institution = edu.get("Institution", "")
        duration = edu.get("Duration", "")
        gpa = edu.get("GPA", "")
        line = f"{degree} — {institution} ({duration})"
        if gpa:
            line += f", GPA: {gpa}"
        if line.strip(" —()"):
            education_lines.append(line)

    # --- Projects (top-level, not nested inside Experience) ---
    project_lines = []
    for proj in profile_data.get("Projects", []):
        proj_name = proj.get("Name", "")
        # job1 uses "Description" (string), job2 uses "Details" (list of strings)
        description = proj.get("Description", "")
        details = proj.get("Details", [])
        if proj_name:
            if description:
                project_lines.append(f"- {proj_name}: {description}")
            elif details:
                project_lines.append(f"- {proj_name}: {' | '.join(details)}")

    return {
        "name": name,
        "experience": "\n".join(experience_lines) or "N/A",
        "skills": skills_text or "N/A",
        "education": "\n".join(education_lines) or "N/A",
        "projects": "\n".join(project_lines[:4]) or "N/A",
    }


def _build_prompt(
    request: CoverLetterRequest,
    profile: dict,
    company_research: str | None,
) -> str:
    tone_guidance = {
        "professional": "Clear, honest, and business-appropriate — no fluff or corporate jargon",
        "enthusiastic": "Warm, energetic, and passion-forward — honest and conversational, never over-the-top",
        "concise": "Direct and succinct — every sentence earns its place, no filler",
    }

    company_research_block = (
        f"{company_research}"
        if company_research
        else "Not available. Do not reference any company-specific mission, values, or initiatives beyond what is explicitly stated in the job description."
    )

    return f"""# Role
You are an expert Career Coach and Copywriter specializing in "honest conversation" cover letters. Your goal is to write a cover letter that feels human, avoids corporate jargon, and focuses on solving the hiring manager's specific pain points.

# Task
Write a cover letter for {profile['name']} applying to the role of {request.role_name} at {request.company_name}.

# Instructions & Logic
1. Identify Pain Points: Analyze the [Job Description] below. Pick the top 3 tasks or responsibilities mentioned. These are the hiring manager's pain points.
2. The Two-Column Match: Connect those 3 tasks to specific achievements from [My Resume/Experience]. Use numbers and outcomes wherever present (e.g., "improved accuracy by 91%", "saved $4.25M annually").
3. Speak the Dialect: Use the exact terminology from the job description (e.g., if they say "RAG pipeline," don't say "retrieval system").
4. Company Research: Use the [Company Research] section to show genuine interest in their mission or a specific initiative. If company research is not available, skip this — do not invent details.
5. Structure:
   - Paragraph 1: Who {profile['name']} is and the specific problem they can help {request.company_name} solve.
   - Paragraph 2–3: Evidence-based achievements directly linked to the top 3 JD tasks. Be specific and quantified.
   - Paragraph 4: Why this specific company or initiative resonates — reference [Company Research] if available.
   - Closing: A clear, confident call to action.

# Constraints
- Tone: {tone_guidance[request.tone]}
- Length: Strictly under 4 paragraphs (plus a one-line closing). Under 400 words total.
- Focus: Context over a list of jobs. Answer "why should they care about my skills?"
- Honesty: If a JD requirement is missing from the resume, do not include it in the cover letter. Do not pretend the skill exists.
- Avoid corporate buzzwords, generic phrases like 'I am passionate about' and any fluff or gimmicky language.
- Do NOT invent facts, credentials, or experiences not present in the resume or company research.
- Do NOT use placeholder text like "[Your Name]" — use {profile['name']} throughout.
- Output plain text only — no markdown, no bullet points, no section headers.

# Input Data

[Job Description]:
{request.job_description}

[My Resume/Experience]:
Name: {profile['name']}

Work Experience:
{profile['experience']}

Key Skills:
{profile['skills']}

Education:
{profile['education']}

Notable Projects:
{profile['projects']}

[Company Research]:
{company_research_block}
"""


def generate_cover_letter(request: CoverLetterRequest) -> str:
    """Generate a cover letter by combining profile extraction, company research,
    and LLM-based writing.

    Flow:
        1. Extract structured profile summary from the optimized resume JSON
        2. Attempt company research (non-blocking — skipped gracefully on failure)
        3. Build the prompt and call Gemini → cover letter

    For quality evaluation of the generated cover letter, use the offline
    LLM-as-a-judge tool in tests/evaluation/cover_letter_evaluator.py.
    """
    profile = _extract_profile_summary(request.profile_data)
    company_research = company_research_service.research(request.company_name, role=request.role_name)
    print(f"Company research: {company_research}")
    prompt = _build_prompt(request, profile, company_research)
    return llm_client.generate(prompt)
