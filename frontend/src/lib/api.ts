import type {
  Certification,
  Education,
  Leadership,
  ProfileFormData,
  Project,
  Volunteer,
  WorkExperience,
} from '@/types/form.types';

/** Dev default uses Vite proxy (see vite.config.ts) so API calls stay same-origin and avoid CORS when the dev server binds to a port other than 5173. */
function resolveApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_URL;
  if (typeof fromEnv === 'string' && fromEnv.trim() !== '') {
    return fromEnv.trim();
  }
  if (import.meta.env.DEV) {
    return '/api';
  }
  return 'http://127.0.0.1:8000';
}

const API_BASE_URL = resolveApiBaseUrl();

export interface ApiResponse<T = unknown> {
  message: string;
  data?: T;
  error?: string;
}

export interface TailorFormData {
  companyName: string;
  roleName: string;
  jobDescription: string;
}

export function buildCoverLetterPayload(
  profile: ProfileFormData,
  tailor: Pick<TailorFormData, 'jobDescription' | 'companyName' | 'roleName'>,
  options?: { existing_cover_letter?: string | null }
): CoverLetterRequestPayload {
  return {
    profile_data: profile as unknown as object,
    job_description: tailor.jobDescription,
    company_name: tailor.companyName,
    role_name: tailor.roleName,
    tone: 'professional',
    existing_cover_letter: options?.existing_cover_letter ?? undefined,
  };
}

export interface ApplicationPayload {
  email: string;
  companyName: string;
  roleName: string;
  jobDescription: string;
  /** Tailored resume JSON from POST /resumes/generate */
  tailoredResume?: Record<string, unknown>;
  /** Plain-text cover letter when generation was requested and succeeded */
  coverLetter?: string | null;
  /** Match percentage saved when the tailored resume was generated */
  matchScore?: number;
  /** Detailed LLM analysis and hallucination checks */
  matchEvaluation?: ResumeMatchEvaluation;
  /** Snapshot of profile used to generate this application's outputs */
  sourceProfile?: ProfileFormData;
  coverLetterFeedback?: 'up' | 'down' | null;
  resumeFeedback?: 'up' | 'down' | null;
  status?: string;
}

export interface HallucinationFinding {
  claim: string;
  status: 'supported' | 'uncertain' | 'unsupported';
  reason: string;
}

export interface ResumeMatchEvaluation {
  final_score: number;
  ats_match_score: number;
  ats_format_score: number;
  hallucination_risk_score: number;
  summary: string;
  ats_strengths: string[];
  ats_gaps: string[];
  format_issues: string[];
  hallucination_findings: HallucinationFinding[];
  source?: string;
}

export interface Application {
  _id?: string;
  companyName: string;
  roleName: string;
  jobDescription: string;
  matchScore?: number;
  matchEvaluation?: ResumeMatchEvaluation;
  sourceProfile?: ProfileFormData;
  coverLetterFeedback?: 'up' | 'down' | null;
  resumeFeedback?: 'up' | 'down' | null;
  tailoredResume?: Record<string, unknown>;
  coverLetter?: string | null;
  status?: string;
  /** ISO timestamp from Mongo when present */
  updatedAt?: string;
  createdAt?: string;
}

export interface ResumeGeneratorPayload {
  personalInfo: ProfileFormData['personalInfo'];
  education: Omit<Education, 'id'>[];
  workExperience: Omit<WorkExperience, 'id'>[];
  projects: Omit<Project, 'id'>[];
  skills: ProfileFormData['skills'];
  certifications: Omit<Certification, 'id'>[];
  volunteer: Omit<Volunteer, 'id'>[];
  leadership: Omit<Leadership, 'id'>[];
  jobDescription: string;
  roleName: string;
  companyName: string;
  maxProjects?: number;
}

export interface ResumeEvaluationPayload {
  jobDescription: string;
  tailoredResume: Record<string, unknown>;
  originalProfile: object;
}

export interface ProfileImportPayload {
  resumeFile?: File;
  resumeText?: string;
}

export interface ProfileImportResponse {
  message: string;
  data: Partial<ProfileFormData>;
  warnings: string[];
  sources: string[];
}

export interface CoverLetterRequestPayload {
  profile_data: object;
  job_description: string;
  company_name: string;
  role_name: string;
  tone?: 'professional' | 'enthusiastic' | 'concise';
  /** When set, PDF endpoint renders this text without another LLM call */
  existing_cover_letter?: string | null;
}

export interface CoverLetterResponsePayload {
  cover_letter: string;
  company_name: string;
  role_name: string;
}

export interface ResumeGenerateResponsePayload {
  tailored_resume: Record<string, unknown>;
  pdf_base64: string;
  match_score?: number;
  match_evaluation?: ResumeMatchEvaluation;
}

function stripId<T extends { id?: string }>(obj: T): Omit<T, 'id'> {
  const { id: _id, ...rest } = obj;
  return rest;
}

function parseError(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'object' && item && 'msg' in item) {
          return String((item as { msg?: string }).msg ?? fallback);
        }
        return JSON.stringify(item);
      })
      .join(', ');
  }

  return fallback;
}

async function parseJsonSafe(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return {};
  }
}

function getAuthHeaders(email?: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(email ? { 'X-User-Email': email } : {}),
  };
}

export function buildResumePayload(
  profile: ProfileFormData,
  tailor: TailorFormData
): ResumeGeneratorPayload {
  return {
    personalInfo: profile.personalInfo,
    education: profile.education.map((item) => stripId(item)),
    workExperience: profile.workExperience.map((item) => stripId(item)),
    projects: profile.projects.map((item) => stripId(item)),
    skills: profile.skills,
    certifications: profile.certifications.map((item) => stripId(item)),
    volunteer: profile.volunteer.map((item) => stripId(item)),
    leadership: profile.leadership.map((item) => stripId(item)),
    jobDescription: tailor.jobDescription,
    roleName: tailor.roleName,
    companyName: tailor.companyName,
    maxProjects: 2,
  };
}

/** Parse stored match score; missing or invalid → undefined (shows as —), never fake 0. */
function coerceApplicationMatchScore(raw: unknown): number | undefined {
  if (raw === null || raw === undefined) return undefined;
  const n = typeof raw === 'number' ? raw : Number(raw);
  if (!Number.isFinite(n) || n <= 0) return undefined;
  return Math.round(n);
}

function coerceMatchEvaluation(raw: unknown): ResumeMatchEvaluation | undefined {
  if (!raw || typeof raw !== 'object') return undefined;
  const obj = raw as Record<string, unknown>;
  const asNum = (v: unknown, fallback = 0): number => {
    const n = typeof v === 'number' ? v : Number(v);
    return Number.isFinite(n) ? Math.max(0, Math.min(100, Math.round(n))) : fallback;
  };
  const asList = (v: unknown): string[] =>
    Array.isArray(v) ? v.map((x) => String(x)).filter((x) => x.trim() !== '') : [];
  const rawFindings = Array.isArray(obj.hallucination_findings) ? obj.hallucination_findings : [];
  const hallucination_findings: HallucinationFinding[] = rawFindings
    .map((entry) => {
      if (!entry || typeof entry !== 'object') return null;
      const e = entry as Record<string, unknown>;
      const statusRaw = String(e.status ?? 'uncertain').toLowerCase();
      const status: HallucinationFinding['status'] =
        statusRaw === 'supported' || statusRaw === 'unsupported' ? statusRaw : 'uncertain';
      return {
        claim: String(e.claim ?? ''),
        status,
        reason: String(e.reason ?? ''),
      };
    })
    .filter((x): x is HallucinationFinding => !!x);
  return {
    final_score: asNum(obj.final_score),
    ats_match_score: asNum(obj.ats_match_score),
    ats_format_score: asNum(obj.ats_format_score),
    hallucination_risk_score: asNum(obj.hallucination_risk_score),
    summary: String(obj.summary ?? ''),
    ats_strengths: asList(obj.ats_strengths),
    ats_gaps: asList(obj.ats_gaps),
    format_issues: asList(obj.format_issues),
    hallucination_findings,
    source: obj.source ? String(obj.source) : undefined,
  };
}

export function normalizeApplications(apps: any[]): Application[] {
  return apps.map((app) => ({
    _id: app._id,
    companyName: app.companyName ?? app.company_name ?? '',
    roleName: app.roleName ?? app.role_name ?? '',
    jobDescription: app.jobDescription ?? app.job_description ?? '',
    matchScore: coerceApplicationMatchScore(app.matchScore ?? app.match_score),
    matchEvaluation: coerceMatchEvaluation(app.matchEvaluation ?? app.match_evaluation),
    sourceProfile: (app.sourceProfile ?? app.source_profile) as ProfileFormData | undefined,
    coverLetterFeedback: (app.coverLetterFeedback ?? app.cover_letter_feedback ?? null) as
      | 'up'
      | 'down'
      | null,
    resumeFeedback: (app.resumeFeedback ?? app.resume_feedback ?? null) as
      | 'up'
      | 'down'
      | null,
    tailoredResume: app.tailoredResume ?? app.tailored_resume,
    coverLetter: app.coverLetter ?? app.cover_letter ?? null,
    status: app.status,
    updatedAt: app.updatedAt ?? app.updated_at,
    createdAt: app.createdAt ?? app.created_at,
  }));
}

export function normalizeApplication(raw: any): Application {
  return normalizeApplications([raw])[0];
}

export type ApplicationPatch = Partial<{
  coverLetter: string | null;
  tailoredResume: Record<string, unknown>;
  companyName: string;
  roleName: string;
  jobDescription: string;
  status: string;
  matchScore: number;
  matchEvaluation: ResumeMatchEvaluation;
  sourceProfile: ProfileFormData;
  coverLetterFeedback: 'up' | 'down' | null;
  resumeFeedback: 'up' | 'down' | null;
}>;

export async function patchApplication(
  email: string,
  applicationId: string,
  patch: ApplicationPatch
): Promise<Application> {
  const response = await fetch(
    `${API_BASE_URL}/applications/${encodeURIComponent(email)}/${encodeURIComponent(applicationId)}`,
    {
      method: 'PATCH',
      headers: getAuthHeaders(email),
      body: JSON.stringify(patch),
    }
  );

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to update application'));
  }

  return normalizeApplication(result);
}

export async function renderTailoredResumePdf(
  tailoredResume: Record<string, unknown>
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/resumes/render/pdf`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ tailoredResume }),
  });

  if (!response.ok) {
    const err = await parseJsonSafe(response);
    throw new Error(parseError(err.detail, 'Failed to render resume PDF'));
  }

  return response.blob();
}

export async function submitRegistration(
  data: ProfileFormData,
  email: string
): Promise<any> {
  const bodyData = {
    ...data,
    email,
  };

  const response = await fetch(`${API_BASE_URL}/user/registration`, {
    method: 'POST',
    headers: getAuthHeaders(email),
    body: JSON.stringify(bodyData),
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(result.detail || result.message || 'Registration failed');
  }

  return result;
}

export async function getProfile(email: string): Promise<any | null> {
  const response = await fetch(
    `${API_BASE_URL}/user/profile/${encodeURIComponent(email)}`,
    {
      method: 'GET',
      headers: getAuthHeaders(email),
    }
  );

  if (response.status === 404) {
    return null;
  }

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(result.detail || result.message || 'Failed to load profile');
  }

  return result;
}

export async function importProfile(
  payload: ProfileImportPayload,
  email?: string
): Promise<ProfileImportResponse> {
  const formData = new FormData();

  if (payload.resumeFile) {
    formData.append('resume_file', payload.resumeFile);
  }

  if (payload.resumeText) {
    formData.append('resume_text', payload.resumeText);
  }

  const response = await fetch(`${API_BASE_URL}/user/profile-import`, {
    method: 'POST',
    headers: email ? { 'X-User-Email': email } : undefined,
    body: formData,
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to import profile'));
  }

  return result;
}

export async function createApplication(
  payload: ApplicationPayload
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/applications`, {
    method: 'POST',
    headers: getAuthHeaders(payload.email),
    body: JSON.stringify(payload),
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(result.detail || result.message || 'Failed to create application');
  }

  return result;
}

export async function getApplications(email: string): Promise<Application[]> {
  const response = await fetch(
    `${API_BASE_URL}/applications/${encodeURIComponent(email)}`,
    {
      method: 'GET',
      headers: getAuthHeaders(email),
    }
  );

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(result.detail || result.message || 'Failed to fetch applications');
  }

  return normalizeApplications(result.applications || []);
}

export async function generateResume(
  payload: ResumeGeneratorPayload
): Promise<ResumeGenerateResponsePayload> {
  const response = await fetch(`${API_BASE_URL}/resumes/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to generate resume'));
  }

  return result as ResumeGenerateResponsePayload;
}

export async function evaluateResumeMatch(
  payload: ResumeEvaluationPayload
): Promise<{ match_score: number; match_evaluation?: ResumeMatchEvaluation }> {
  const response = await fetch(`${API_BASE_URL}/resumes/evaluate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const result = await parseJsonSafe(response);
  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to evaluate resume'));
  }

  return {
    match_score: Number(result.match_score ?? 0),
    match_evaluation: coerceMatchEvaluation(result.match_evaluation),
  };
}

export async function generateResumePdf(
  payload: ResumeGeneratorPayload
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/resumes/generate/pdf`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await parseJsonSafe(response);
    throw new Error(parseError(err.detail, 'Failed to generate PDF'));
  }

  return response.blob();
}

export async function generateCoverLetter(
  payload: CoverLetterRequestPayload
): Promise<CoverLetterResponsePayload> {
  const response = await fetch(`${API_BASE_URL}/cover-letter/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to generate cover letter'));
  }

  return result;
}

export async function generateCoverLetterPdf(
  payload: CoverLetterRequestPayload
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/cover-letter/generate/pdf`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await parseJsonSafe(response);
    throw new Error(parseError(err.detail, 'Failed to generate cover letter PDF'));
  }

  return response.blob();
}

export function base64ToBlob(base64: string, mimeType = 'application/pdf'): Blob {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: mimeType });
}

export function downloadPdfBlob(blob: Blob, filename = 'tailored_resume.pdf'): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = filename;
  anchor.style.display = 'none';

  document.body.appendChild(anchor);
  anchor.click();

  window.setTimeout(() => {
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  }, 200);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
