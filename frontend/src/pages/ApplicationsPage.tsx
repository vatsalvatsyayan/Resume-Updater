import { useState } from 'react';
import { motion } from 'framer-motion';
import { Briefcase } from 'lucide-react';
import { toast } from 'sonner';
import { Header } from '@/components/layout';
import { TailorResumeModal, type TailorResumeFormData } from '@/components/modals';
import { cn } from '@/lib/cn';

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

export function ApplicationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleTailorSubmit = async (data: TailorResumeFormData) => {
    setIsSubmitting(true);
    try {
      // TODO: Send to API for resume tailoring
      console.log('Tailoring resume for:', data);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setIsModalOpen(false);
      toast.success(`Resume tailoring started for ${data.companyName}!`);
    } catch (error) {
      toast.error('Failed to start resume tailoring. Please try again.');
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

        {/* Applications List */}
        <div className="space-y-3">
          {mockApplications.map((app, index) => (
            <motion.div
              key={app.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                'flex items-center justify-between p-4 rounded-xl',
                'bg-sky-100 border border-sky-200',
                'cursor-default'
              )}
            >
              <div className="flex items-center gap-4">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <Briefcase className="w-5 h-5 text-slate-600" />
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-slate-900">
                    Application {app.id}.
                  </span>
                  <span className="text-slate-700">{app.company}.</span>
                  <span className="text-slate-600">{app.jobTitle}.</span>
                </div>
              </div>
              <div className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-full font-medium',
                getScoreColor(app.score)
              )}>
                <span>{getScoreDisplay(app.score)}</span>
                <span>{getScoreEmoji(app.score)}</span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Empty state hint */}
        {mockApplications.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <Briefcase className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-600 mb-2">
              No applications yet
            </h3>
            <p className="text-slate-500">
              Click the + button to create your first application.
            </p>
          </motion.div>
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
