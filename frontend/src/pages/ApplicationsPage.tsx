import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Briefcase } from 'lucide-react';
import { toast } from 'sonner';
import { Header } from '@/components/layout';
import { TailorResumeModal, type TailorResumeFormData } from '@/components/modals';
import { cn } from '@/lib/cn';
import { useUser } from '@clerk/clerk-react';

interface Application {
  _id?: string;
  companyName: string;
  roleName: string;
  jobDescription: string;
  matchScore?: number;
}

function getScoreColor(score: number) {
  if (score === 0) return 'text-slate-500 bg-slate-100';
  if (score <= 30) return 'text-red-600 bg-red-50';
  if (score <= 60) return 'text-amber-600 bg-amber-50';
  return 'text-green-600 bg-green-50';
}

function getScoreEmoji(score: number) {
  if (score === 0) return '⏳';
  if (score <= 30) return '😡';
  if (score <= 60) return '😐';
  if (score <= 80) return '🙂';
  return '🤩';
}

function getScoreDisplay(score: number) {
  if (score === 0) return 'Pending';
  return `${score}%`;
}

function normalizeApplications(apps: any[]): Application[] {
  return apps.map((app) => ({
    _id: app._id,
    companyName: app.companyName ?? app.company_name ?? '',
    roleName: app.roleName ?? app.role_name ?? '',
    jobDescription: app.jobDescription ?? app.job_description ?? '',
    matchScore: app.matchScore ?? app.match_score ?? 0,
  }));
}

export function ApplicationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoadingApplications, setIsLoadingApplications] = useState(true);
  const [openApplicationId, setOpenApplicationId] = useState<string | null>(null);

  const { user } = useUser();

  useEffect(() => {
    const fetchApplications = async () => {
      const email = user?.primaryEmailAddress?.emailAddress;

      if (!email) {
        setIsLoadingApplications(false);
        return;
      }

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/applications/${encodeURIComponent(email)}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'X-User-Email': email,
            },
          }
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || 'Failed to fetch applications');
        }

        setApplications(normalizeApplications(result.applications || []));
      } catch (error) {
        console.error(error);
        toast.error('Failed to load applications');
      } finally {
        setIsLoadingApplications(false);
      }
    };

    fetchApplications();
  }, [user]);

  const handleTailorSubmit = async (data: TailorResumeFormData) => {
    const email = user?.primaryEmailAddress?.emailAddress;

    if (!email) {
      toast.error('No signed-in user email found.');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        email,
        companyName: data.companyName,
        roleName: data.roleName,
        jobDescription: data.jobDescription,
      };

      const response = await fetch('http://127.0.0.1:8000/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Email': email,
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Failed to create application');
      }

      setIsModalOpen(false);

      const listResponse = await fetch(
        `http://127.0.0.1:8000/applications/${encodeURIComponent(email)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-User-Email': email,
          },
        }
      );

      const listResult = await listResponse.json();

      if (listResponse.ok) {
        setApplications(normalizeApplications(listResult.applications || []));
      }

      toast.success(`Application created for ${data.companyName}`);
    } catch (error) {
      console.error(error);
      toast.error('Failed to start resume tailoring.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header onAddClick={() => setIsModalOpen(true)} />

      <main className="max-w-4xl mx-auto px-4 py-8">

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Your Applications
          </h1>

          <p className="text-slate-600">
            Track all your job applications and their match scores.
          </p>
        </motion.div>

        {isLoadingApplications && (
          <div className="text-slate-600">Loading applications...</div>
        )}

        {!isLoadingApplications && applications.length > 0 && (
          <div className="space-y-3">
            {applications.map((app, index) => {
              const appKey = app._id || String(index);
              const score = app.matchScore ?? 0;
              const isOpen = openApplicationId === appKey;

              return (
                <motion.div
                  key={appKey}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="rounded-xl bg-sky-100 border border-sky-200 overflow-hidden"
                >

                  <button
                    type="button"
                    onClick={() =>
                      setOpenApplicationId(isOpen ? null : appKey)
                    }
                    className="w-full flex items-center justify-between p-4 text-left"
                  >

                    <div className="flex items-center gap-4">

                      <div className="p-2 bg-white rounded-lg shadow-sm">
                        <Briefcase className="w-5 h-5 text-slate-600" />
                      </div>

                      <div className="flex flex-col">

                        <span className="font-semibold text-slate-900">
                          {app.companyName}
                        </span>

                        <span className="text-sm text-slate-600">
                          {app.roleName}
                        </span>

                      </div>
                    </div>

                    <div
                      className={cn(
                        'flex items-center gap-2 px-3 py-1.5 rounded-full font-medium',
                        getScoreColor(score)
                      )}
                    >
                      <span>{getScoreDisplay(score)}</span>
                      <span>{getScoreEmoji(score)}</span>
                    </div>
                  </button>

                  {isOpen && (
                    <div className="px-4 pb-4">

                      <div className="ml-14 rounded-lg bg-white/70 border border-sky-100 p-4">

                        <h3 className="text-sm font-semibold text-slate-900 mb-2">
                          Job Description
                        </h3>

                        <p className="text-sm text-slate-700 whitespace-pre-wrap">
                          {app.jobDescription || 'No job description available.'}
                        </p>

                      </div>

                    </div>
                  )}

                </motion.div>
              );
            })}
          </div>
        )}

        {!isLoadingApplications && applications.length === 0 && (
          <div className="text-center py-16">
            <Briefcase className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-600 mb-2">
              No applications yet
            </h3>
            <p className="text-slate-500">
              Click the + button to create your first application.
            </p>
          </div>
        )}
      </main>

      <TailorResumeModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        onSubmit={handleTailorSubmit}
        isLoading={isSubmitting}
      />
    </div>
  );
}