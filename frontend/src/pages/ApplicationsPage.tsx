import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Briefcase } from 'lucide-react';
import { toast, Toaster } from 'sonner';

import { Header } from '@/components/layout';
import { TailorResumeModal, type TailorResumeFormData } from '@/components/modals';
import { cn } from '@/lib/cn';
import {
  buildResumePayload,
  generateResumePdf,
  downloadPdfBlob,
} from '@/lib/api';
import { useFormStore } from '@/stores/formStore';
import { defaultProfileFormData } from '@/types/form.types';

interface Application {
  id: number;
  company: string;
  jobTitle: string;
  score: number;
}

const mockApplications: Application[] = [
  { id: 1, company: 'Google', jobTitle: 'Software Engineer', score: 0 },
  { id: 2, company: 'Apple', jobTitle: 'iOS Developer', score: 42 },
  { id: 3, company: 'Netflix', jobTitle: 'Senior Backend Engineer', score: 69 },
];

function getScoreColor(score: number) {
  if (score === 0) return 'text-slate-500 bg-slate-100';
  if (score <= 30) return 'text-red-600 bg-red-50';
  if (score <= 60) return 'text-amber-600 bg-amber-50';
  return 'text-green-600 bg-green-50';
}

function getScoreDisplay(score: number) {
  if (score === 0) return 'Pending';
  return `${score}%`;
}

export function ApplicationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { loadDraft } = useFormStore();
  const profile = useMemo(() => loadDraft() || defaultProfileFormData, [loadDraft]);

  const hasUsableProfile =
    !!profile.personalInfo?.name &&
    !!profile.personalInfo?.email;

  const handleTailorSubmit = async (data: TailorResumeFormData) => {
    if (!hasUsableProfile) {
      toast.error('Please complete and save your profile first.');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = buildResumePayload(profile, data);
      const blob = await generateResumePdf(payload);

      const safeCompany = data.companyName.replace(/\s+/g, '-');
      const safeRole = data.roleName.replace(/\s+/g, '-');
      const filename = `resume-${safeCompany}-${safeRole}.pdf`;

      downloadPdfBlob(blob, filename);
      setIsModalOpen(false);

      toast.success(`Resume for ${data.companyName} (${data.roleName}) downloaded!`);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to generate resume';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header />
      <Toaster richColors position="top-right" />

      <TailorResumeModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        onSubmit={handleTailorSubmit}
        isLoading={isSubmitting}
      />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Your Applications</h1>
            <p className="text-muted-foreground">
              Track all your job applications and generate tailored resumes.
            </p>
          </div>

          <button
            onClick={() => {
              if (!hasUsableProfile) {
                toast.error('Fill and save your profile first.');
                return;
              }
              setIsModalOpen(true);
            }}
            className="rounded-full bg-black text-white px-4 py-2"
          >
            Tailor Resume
          </button>
        </div>

        <div className="space-y-4">
          {mockApplications.map((app, index) => (
            <motion.div
              key={app.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between rounded-xl border p-4"
            >
              <div className="flex items-center gap-3">
                <Briefcase className="w-5 h-5 text-slate-500" />
                <div>
                  <p className="font-medium">{app.company}</p>
                  <p className="text-sm text-slate-500">{app.jobTitle}</p>
                </div>
              </div>

              <span
                className={cn(
                  'rounded-full px-3 py-1 text-sm font-medium',
                  getScoreColor(app.score)
                )}
              >
                {getScoreDisplay(app.score)}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </>
  );
}