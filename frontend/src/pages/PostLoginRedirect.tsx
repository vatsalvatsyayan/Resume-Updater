import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

import { getProfile } from '@/lib/api';

/**
 * Clerk sends users here after sign-in / sign-up.
 * Returning users (profile exists in API) → Applications.
 * New users → Profile builder.
 */
export function PostLoginRedirect() {
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();

  useEffect(() => {
    if (!isLoaded) return;

    const email = user?.primaryEmailAddress?.emailAddress;
    if (!email) {
      navigate('/', { replace: true });
      return;
    }

    let cancelled = false;

    (async () => {
      try {
        const profile = await getProfile(email);
        if (cancelled) return;
        if (profile) {
          navigate('/applications', { replace: true });
        } else {
          navigate('/profile', { replace: true });
        }
      } catch {
        if (cancelled) return;
        navigate('/profile', { replace: true });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [isLoaded, user, navigate]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4">
      <div className="rounded-xl border bg-white px-8 py-10 shadow-sm text-center max-w-md">
        <div className="mx-auto mb-4 h-10 w-10 animate-pulse rounded-full bg-slate-200" />
        <p className="text-slate-700 font-medium">Setting up your workspace…</p>
        <p className="mt-2 text-sm text-slate-500">One moment.</p>
      </div>
    </div>
  );
}
