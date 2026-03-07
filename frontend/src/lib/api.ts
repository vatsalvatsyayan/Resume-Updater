import type { ProfileFormData } from '@/types/form.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface TailorFormData {
  companyName: string;
  roleName: string;
  jobDescription: string;
}

export interface ResumeGeneratorPayload {
  personalInfo: ProfileFormData['personalInfo'];
  education: Omit<ProfileFormData['education'][number], 'id'>[];
  workExperience: Omit<ProfileFormData['workExperience'][number], 'id'>[];
  projects: Omit<ProfileFormData['projects'][number], 'id'>[];
  skills: ProfileFormData['skills'];
  certifications: Omit<ProfileFormData['certifications'][number], 'id'>[];
  volunteer: Omit<ProfileFormData['volunteer'][number], 'id'>[];
  leadership: Omit<ProfileFormData['leadership'][number], 'id'>[];
  jobDescription: string;
  roleName: string;
  companyName: string;
  maxProjects?: number;
}

function stripId<T extends object>(obj: T): Omit<T, 'id'> {
  const { id: _, ...rest } = obj as T & { id?: string };
  return rest;
}

export function buildResumePayload(
  profile: ProfileFormData,
  tailor: TailorFormData
): ResumeGeneratorPayload {
  return {
    personalInfo: profile.personalInfo,
    education: profile.education.map((e) => stripId(e)),
    workExperience: profile.workExperience.map((e) => stripId(e)),
    projects: profile.projects.map((p) => stripId(p)),
    skills: profile.skills,
    certifications: profile.certifications.map((c) => stripId(c)),
    volunteer: profile.volunteer.map((v) => stripId(v)),
    leadership: profile.leadership.map((l) => stripId(l)),
    jobDescription: tailor.jobDescription,
    roleName: tailor.roleName,
    companyName: tailor.companyName,
    maxProjects: 2,
  };
}

function parseError(detail: unknown, fallback: string) {
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((d) =>
        typeof d === 'object' && d && 'msg' in d
          ? String((d as { msg?: string }).msg)
          : JSON.stringify(d)
      )
      .join(', ');
  }

  return fallback;
}

export async function submitRegistration(data: ProfileFormData) {
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

export async function generateResumePdf(
  payload: ResumeGeneratorPayload
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/resumes/generate/pdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(parseError(err.detail, 'Failed to generate PDF'));
  }

  return response.blob();
}

export function downloadPdfBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');

  a.href = url;
  a.download = filename;
  a.style.display = 'none';

  document.body.appendChild(a);
  a.click();

  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 200);
}