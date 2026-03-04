from schemas.cover_letter import CoverLetterRequest
from services import llm_client


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


def _build_prompt(request: CoverLetterRequest, profile: dict) -> str:
    tone_guidance = {
        "professional": "formal, polished, and business-appropriate",
        "enthusiastic": "warm, energetic, and passion-forward while remaining professional",
        "concise": "direct and succinct — every sentence earns its place",
    }

    return f"""You are an expert career coach and professional cover letter writer.

Write a compelling cover letter for {profile['name']} applying to the role of {request.role_name} at {request.company_name}.

## Candidate Profile (from optimized resume)
Name: {profile['name']}

### Work Experience
{profile['experience']}

### Key Skills
{profile['skills']}

### Education
{profile['education']}

### Notable Projects
{profile['projects']}

## Job Description
{request.job_description}

## Writing Instructions
- Tone: {tone_guidance[request.tone]}
- Length: 3–4 paragraphs, under 400 words total
- Paragraph 1 (Opening): State the specific role and company; explain why {profile['name']} is excited about this particular opportunity at {request.company_name}
- Paragraph 2–3 (Body): Directly connect 2–3 of the strongest experiences or skills above to the requirements in the job description; use specific, concrete examples and quantified achievements where available
- Paragraph 4 (Closing): Reiterate enthusiasm, include a call to action, and express readiness to discuss further
- Do NOT invent facts, credentials, or experiences that are not present in the candidate profile above
- Do NOT include any placeholder text like "[Your Name]" — use the actual name provided
- Output plain text only; no markdown, no bullet points, no headers
"""


def generate_cover_letter(request: CoverLetterRequest) -> str:
    """Build a prompt from the request and call the LLM to generate a cover letter."""
    profile = _extract_profile_summary(request.profile_data)
    prompt = _build_prompt(request, profile)
    return llm_client.generate(prompt)
