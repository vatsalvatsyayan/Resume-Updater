# Resume Generator Service

FastAPI service that takes a user profile and job description, uses an LLM to select and rewrite content for the role, and returns a tailored resume (JSON) and a one-page PDF.

---

## How it works

### Request flow

1. **Request**  
   Client sends a single JSON body to `POST /generate` or `POST /generate/pdf`. The body must include the full profile (personal info, education, work experience, projects, skills, certifications, volunteer, leadership) and a **job description** (required, min 50 characters). Optional fields: `roleName`, `companyName`, `maxProjects`.

2. **Validation**  
   The body is validated against the `ResumeGeneratorInput` Pydantic schema. Invalid or missing required fields (e.g. `jobDescription` too short) return 400.

3. **Tailoring (LLM)**  
   The **TailorService** builds a system prompt (resume-writing and ATS rules) and a user prompt containing the candidate profile and job context. If `maxProjects` is set, the prompt instructs the LLM to include at most that many projects and to choose the most relevant for the job.  
   The configured LLM provider (default: Gemini) is called once. The model returns a single JSON object: the tailored resume with reordered/selected sections, rewritten bullet points, a short professional summary, and a flattened skills list ordered by relevance.

4. **Response parsing**  
   The raw LLM response is stripped of markdown code fences (if present) and parsed as JSON. The result is mapped into a `TailoredResume` Pydantic model. Invalid or malformed JSON raises `ValueError` and the API returns 500 (or 400 when wrapped as validation).

5. **PDF generation**  
   The **PDFBuilder** renders the `TailoredResume` to a single A4 page using fpdf2.  
   - **One-page guarantee:** Auto page break is disabled. Before each section (and before each item in variable-length sections), the builder checks whether enough vertical space remains below the current Y position. If not, that section or item is skipped. Summary and skills text are truncated by character count so they do not overflow.  
   - **Font safety:** All dynamic text is passed through `_pdf_safe()` to replace Unicode characters that Helvetica does not support (e.g. en-dash, smart quotes), avoiding PDF render errors.

6. **Response**  
   - `POST /generate`: Returns JSON with `tailored_resume` (dict) and `pdf_base64` (string).  
   - `POST /generate/pdf`: Returns the PDF bytes with `Content-Disposition: attachment; filename=resume.pdf`.

### Component roles

- **`resume_generator.generator`** – Entry point. Validates input, runs TailorService, runs PDFBuilder, returns tailored resume and PDF path or bytes.  
- **`resume_generator.services.tailor_service`** – Builds prompts, calls the LLM, parses JSON into `TailoredResume`. Encodes selection rules (e.g. `maxProjects`) in the user prompt.  
- **`resume_generator.llm`** – Model-agnostic LLM layer. `LLMProvider` interface and registry; default implementation is Gemini. Provider and model are chosen via config (env or `ResumeGeneratorConfig`).  
- **`resume_generator.pdf.builder`** – Renders `TailoredResume` to one PDF page with fixed layout, space checks, and Unicode sanitization.

### Optional: project cap (`maxProjects`)

When the client sends `maxProjects` (integer between 1 and 20), the tailoring prompt tells the LLM to include **at most** that many projects and to **select the most relevant** for the job. Other projects are omitted from the tailored resume. This allows the client to e.g. request “show only 2 projects” and have the service pick the two that best match the job description.

---

## Quick start

### Install and run server

```bash
cd resume-generator
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key
uvicorn app:app --host 0.0.0.0 --port 8001
```

- API: **http://localhost:8001**
- Docs: **http://localhost:8001/docs**
- Health: **http://localhost:8001/health**

### Test

**Via test script (server running):**

```bash
python run_test.py --api http://localhost:8001
```

**Direct (no server):**

```bash
python run_test.py --input sample_input.json --output out.pdf
python run_test.py --no-pdf --input sample_input_ai_engineer.json
```

**curl:**

```bash
curl -s -X POST http://localhost:8001/generate -H "Content-Type: application/json" -d @sample_input.json
curl -s -X POST http://localhost:8001/generate/pdf -H "Content-Type: application/json" -d @sample_input.json -o resume.pdf
```

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns `{"status":"ok","service":"resume-generator"}`. |
| POST | `/generate` | Body: JSON (see Input). Returns `{ "tailored_resume": {...}, "pdf_base64": "..." }`. |
| POST | `/generate/pdf` | Same body. Returns binary PDF with `Content-Disposition: attachment; filename=resume.pdf`. |

---

## Input (request body)

Single JSON object matching **ResumeGeneratorInput**. Same shape as the frontend profile form, plus job context and optional project cap.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| personalInfo | object | Yes | name, email, portfolioWebsite?, githubUrl?, linkedinUrl? |
| education | array | Yes | List of education entries. |
| workExperience | array | Yes | List of work experience entries. |
| projects | array | Yes | List of project entries. |
| skills | object | Yes | programmingLanguages, frameworks, databases, toolsAndTechnologies, cloud, ai, other (each string array). |
| certifications | array | Yes | List of certification entries. |
| volunteer | array | Yes | List of volunteer entries. |
| leadership | array | Yes | List of leadership entries. |
| jobDescription | string | Yes | Full job description; min length 50. Used to tailor and select content. |
| roleName | string | No | Job title. |
| companyName | string | No | Company name for this application. |
| maxProjects | integer | No | If set (1–20), at most this many projects are included; the LLM selects the most relevant. |

Exact field names and nested shapes match the frontend form. See **resume_generator/schemas/input_schema.py** and the sample files **sample_input.json**, **sample_input_ai_engineer.json**.

---

## Output

- **tailored_resume**: Same sections as input, but filtered and reordered for the job, with rewritten bullets and an optional professional summary. Skills are a single list, most relevant first.
- **pdf_base64** (POST /generate): Base64-encoded PDF. Decode to obtain bytes for storage or download.
- **POST /generate/pdf**: Response body is the raw PDF bytes.

---

## Configuration

| Env var | Default | Description |
|---------|--------|-------------|
| GOOGLE_API_KEY or GEMINI_API_KEY | — | Required for default Gemini provider. |
| RESUME_LLM_PROVIDER | gemini | LLM provider name. |
| RESUME_LLM_MODEL | gemini-2.0-flash | Model name. |
| RESUME_PDF_OUTPUT_DIR | — | Optional; used when writing PDF to disk via Python API. |

To add a provider: implement `LLMProvider` in **resume_generator/llm/**, register it in **resume_generator/llm/providers.py**, and set `RESUME_LLM_PROVIDER` (and any provider-specific API key).

---

## Project layout

```
resume-generator/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py
├── run_test.py
├── sample_input.json
├── sample_input_ai_engineer.json
└── resume_generator/
    ├── __init__.py
    ├── config.py
    ├── generator.py
    ├── schemas/
    │   ├── input_schema.py
    │   └── output_schema.py
    ├── llm/
    │   ├── base.py
    │   ├── registry.py
    │   ├── gemini_provider.py
    │   └── providers.py
    ├── services/
    │   └── tailor_service.py
    └── pdf/
        └── builder.py
```

Generated PDFs (e.g. from `run_test.py`) are ignored via `.gitignore` and should not be committed.
