import type { ProfileFormData } from '@/types/form.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface ApiResponse<T = unknown> {
  message: string;
  data?: T;
  error?: string;
}

export async function submitRegistration(data: ProfileFormData, email: string): Promise<ApiResponse> {
  console.log('Request email:', email);
  const bodyData = {
    ...data,
    email: email,
  };
  const response = await fetch(`${API_BASE_URL}/user/registration`, {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    'X-User-Email': email,
  },
    body: JSON.stringify(bodyData),
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
