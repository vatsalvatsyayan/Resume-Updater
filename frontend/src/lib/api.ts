import type {
  Certification,
  Education,
  Leadership,
  ProfileFormData,
  Project,
  Volunteer,
  WorkExperience,
} from '@/types/form.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

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

export interface ApplicationPayload {
  email: string;
  companyName: string;
  roleName: string;
  jobDescription: string;
}

export interface Application {
  _id?: string;
  companyName: string;
  roleName: string;
  jobDescription: string;
  matchScore?: number;
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

export function normalizeApplications(apps: any[]): Application[] {
  return apps.map((app) => ({
    _id: app._id,
    companyName: app.companyName ?? app.company_name ?? '',
    roleName: app.roleName ?? app.role_name ?? '',
    jobDescription: app.jobDescription ?? app.job_description ?? '',
    matchScore: app.matchScore ?? app.match_score ?? 0,
  }));
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
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/resumes/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const result = await parseJsonSafe(response);

  if (!response.ok) {
    throw new Error(parseError(result.detail, 'Failed to generate resume'));
  }

  return result;
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