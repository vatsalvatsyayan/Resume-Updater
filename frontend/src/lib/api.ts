import type { ProfileFormData } from '@/types/form.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface ApiResponse<T = unknown> {
  message: string;
  data?: T;
  error?: string;
}

/** Payload for POST /resumes/generate/pdf – matches backend ResumeGeneratorInput */
export interface ResumeGeneratorPayload {
  personalInfo: ProfileFormData['personalInfo'];
  education: ProfileFormData['education'];
  workExperience: ProfileFormData['workExperience'];
  projects: ProfileFormData['projects'];
  skills: ProfileFormData['skills'];
  certifications: ProfileFormData['certifications'];
  volunteer: ProfileFormData['volunteer'];
  leadership: ProfileFormData['leadership'];
  jobDescription: string;
  roleName: string;
  companyName: string;
}

/** Tailor form fields (company, role, job description) */
export interface TailorFormData {
  companyName: string;
  roleName: string;
  jobDescription: string;
}

/** Build JSON body for resume generation from profile + tailor form. */
export function buildResumePayload(
  profile: ProfileFormData,
  tailor: TailorFormData
): ResumeGeneratorPayload {
  const stripId = (obj: object): Record<string, unknown> => {
    const { id: _, ...rest } = obj as Record<string, unknown>;
    return rest;
  };
  return {
    personalInfo: profile.personalInfo,
    education: profile.education.map((e) => stripId(e)) as unknown as ProfileFormData['education'],
    workExperience: profile.workExperience.map((e) => stripId(e)) as unknown as ProfileFormData['workExperience'],
    projects: profile.projects.map((p) => stripId(p)) as unknown as ProfileFormData['projects'],
    skills: profile.skills,
    certifications: profile.certifications.map((c) => stripId(c)) as unknown as ProfileFormData['certifications'],
    volunteer: profile.volunteer.map((v) => stripId(v)) as unknown as ProfileFormData['volunteer'],
    leadership: profile.leadership.map((l) => stripId(l)) as unknown as ProfileFormData['leadership'],
    jobDescription: tailor.jobDescription,
    roleName: tailor.roleName,
    companyName: tailor.companyName,
  };
}

/** POST /resumes/generate/pdf with payload; returns PDF blob. */
export async function generateResumePdf(payload: ResumeGeneratorPayload): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/resumes/generate/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    const detail = err.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join(', ')
          : response.statusText || 'Failed to generate PDF';
    throw new Error(message);
  }
  return response.blob();
}

export async function submitRegistration(data: ProfileFormData): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE_URL}/user/registration`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || result.message || 'Registration failed');
  }

  return result;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
