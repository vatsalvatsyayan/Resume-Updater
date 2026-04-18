import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Briefcase, ChevronDown, ChevronUp } from 'lucide-react';
import { toast, Toaster } from 'sonner';
import { useUser } from '@clerk/clerk-react';

import { Header } from '@/components/layout';
import { TailorResumeModal, type TailorResumeFormData } from '@/components/modals';
import { cn } from '@/lib/cn';
import {
  buildCoverLetterPayload,
  buildResumePayload,
  base64ToBlob,
  createApplication,
  downloadPdfBlob,
  generateCoverLetter,
  generateCoverLetterPdf,
  generateResume,
  getApplications,
  getProfile,
  type Application,
} from '@/lib/api';
import { useFormStore } from '@/stores/formStore';
import { defaultProfileFormData, type ProfileFormData } from '@/types/form.types';

function getScoreColor(score: number) {
  if (score === 0) return 'text-slate-500 bg-slate-100';
  if (score <= 30) return 'text-red-600 bg-red-50';
  if (score <= 60) return 'text-amber-600 bg-amber-50';
  return 'text-green-600 bg-green-50';
}

function getScoreDisplay(score: number | undefined) {
  if (score === undefined || score === null) return '—';
  if (score === 0) return 'Pending';
  return `${score}%`;
}

function formatStoredIso(iso?: string) {
  if (!iso) return null;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

function StoredBlock({
  title,
  children,
  empty,
}: {
  title: string;
  children: ReactNode;
  empty?: boolean;
}) {
  if (empty) {
    return (
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">{title}</h4>
        <p className="text-sm text-slate-400 italic">Nothing stored.</p>
      </div>
    );
  }
  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">{title}</h4>
      {children}
    </div>
  );
}

function normalizeProfile(profile: any, fallbackEmail = ''): ProfileFormData {
  return {
    ...defaultProfileFormData,
    personalInfo: {
      ...defaultProfileFormData.personalInfo,
      name: profile?.personalInfo?.name ?? '',
      email: profile?.personalInfo?.email ?? profile?.email ?? fallbackEmail,
      portfolioWebsite: profile?.personalInfo?.portfolioWebsite ?? null,
      githubUrl: profile?.personalInfo?.githubUrl ?? null,
      linkedinUrl: profile?.personalInfo?.linkedinUrl ?? null,
    },
    education: profile?.education ?? defaultProfileFormData.education,
    workExperience: profile?.workExperience ?? defaultProfileFormData.workExperience,
    projects: profile?.projects ?? defaultProfileFormData.projects,
    skills: {
      ...defaultProfileFormData.skills,
      ...(profile?.skills ?? {}),
    },
    certifications: profile?.certifications ?? defaultProfileFormData.certifications,
    volunteer: profile?.volunteer ?? defaultProfileFormData.volunteer,
    leadership: profile?.leadership ?? defaultProfileFormData.leadership,
  };
}

export function ApplicationsPage() {
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [profile, setProfile] = useState<ProfileFormData>(defaultProfileFormData);
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [applications, setApplications] = useState<Application[]>([]);
  const [isAppsLoading, setIsAppsLoading] = useState(true);
  const [expandedKey, setExpandedKey] = useState<string | null>(null);

  const { loadDraft, saveDraft } = useFormStore();

  const refreshApplications = useCallback(async () => {
    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!userEmail) {
      setApplications([]);
      setIsAppsLoading(false);
      return;
    }
    setIsAppsLoading(true);
    try {
      const apps = await getApplications(userEmail);
      setApplications(apps);
    } catch (e) {
      console.error('Failed to load applications:', e);
      setApplications([]);
    } finally {
      setIsAppsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    const loadProfile = async () => {
      if (!isLoaded) return;

      const draft = loadDraft() || defaultProfileFormData;
      const userEmail = user?.primaryEmailAddress?.emailAddress;

      if (!userEmail) {
        setProfile(draft);
        setIsProfileLoading(false);
        return;
      }

      try {
        const savedProfile = await getProfile(userEmail);

        if (savedProfile) {
          const normalized = normalizeProfile(savedProfile, userEmail);
          setProfile(normalized);
          saveDraft(normalized);
          return;
        }
      } catch (error) {
        console.error('Failed to load saved profile for applications page:', error);
      }

      setProfile(draft);
      setIsProfileLoading(false);
    };

    loadProfile().finally(() => {
      setIsProfileLoading(false);
    });
  }, [isLoaded, loadDraft, saveDraft, user]);

  useEffect(() => {
    if (!isLoaded) return;
    void refreshApplications();
  }, [isLoaded, refreshApplications]);

  const hasUsableProfile =
    !!profile.personalInfo?.name &&
    !!profile.personalInfo?.email;

  const handleTailorSubmit = async (data: TailorResumeFormData) => {
    if (!hasUsableProfile) {
      toast.error('Please complete and save your profile first.');
      return;
    }

    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!userEmail) {
      toast.error('Unable to get your email. Please log out and sign in again.');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = buildResumePayload(profile, data);
      const gen = await generateResume(payload);

      const safeCompany = data.companyName.replace(/\s+/g, '-');
      const safeRole = data.roleName.replace(/\s+/g, '-');
      const resumeFilename = `resume-${safeCompany}-${safeRole}.pdf`;

      const pdfBlob = base64ToBlob(gen.pdf_base64);
      downloadPdfBlob(pdfBlob, resumeFilename);

      const tailoredResume = gen.tailored_resume as Record<string, unknown>;

      let coverLetterText: string | null = null;
      let coverLetterNotice = '';

      if (data.generateCoverLetter) {
        try {
          const clPayload = buildCoverLetterPayload(profile, data);
          const clResponse = await generateCoverLetter(clPayload);
          coverLetterText = clResponse.cover_letter;

          const pdfPayload = buildCoverLetterPayload(profile, data, {
            existing_cover_letter: coverLetterText,
          });
          const coverPdfBlob = await generateCoverLetterPdf(pdfPayload);
          downloadPdfBlob(
            coverPdfBlob,
            `cover-letter-${safeCompany}-${safeRole}.pdf`
          );
          coverLetterNotice = ' and cover letter';
        } catch (clErr) {
          toast.error('Cover letter generation failed', {
            description:
              clErr instanceof Error ? clErr.message : 'Resume was still downloaded.',
          });
        }
      }

      try {
        await createApplication({
          email: userEmail,
          companyName: data.companyName,
          roleName: data.roleName,
          jobDescription: data.jobDescription,
          tailoredResume,
          coverLetter: coverLetterText,
          status: 'generated',
        });
        await refreshApplications();
      } catch (saveErr) {
        toast.warning('Downloads saved locally; cloud save failed', {
          description:
            saveErr instanceof Error ? saveErr.message : 'Try again later.',
        });
      }

      setIsModalOpen(false);

      toast.success(
        `Resume${coverLetterNotice} for ${data.companyName} (${data.roleName}) downloaded!`
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to generate resume';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isProfileLoading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Toaster position="top-right" richColors closeButton />
        <Header />
        <main className="container mx-auto px-4 py-8">
          <p className="text-slate-600">Loading profile...</p>
        </main>
      </div>
    );
  }

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
              Track job applications and generated tailored resumes.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/profile')}
              className="rounded-full border border-slate-300 bg-white text-slate-900 px-4 py-2 hover:bg-slate-50"
            >
              View Profile
            </button>
            <button
              type="button"
              onClick={() => {
                if (isProfileLoading) {
                  toast.info('Loading your saved profile...');
                  return;
                }

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
        </div>

        <div className="space-y-4">
          {isAppsLoading ? (
            <p className="text-slate-600">Loading applications…</p>
          ) : applications.length === 0 ? (
            <p className="text-slate-600">
              No saved applications yet. Generate a tailored resume to store job details and output
              here.
            </p>
          ) : (
            applications.map((app, index) => {
              const rowKey = app._id ?? `app-${index}`;
              const isOpen = expandedKey === rowKey;
              const tailored = app.tailoredResume;
              const savedLabel = formatStoredIso(app.updatedAt);
              const summary =
                tailored && typeof tailored.professionalSummary === 'string'
                  ? tailored.professionalSummary
                  : null;

              return (
                <motion.div
                  key={rowKey}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="rounded-xl border bg-white shadow-sm overflow-hidden"
                >
                  <button
                    type="button"
                    onClick={() =>
                      setExpandedKey((prev) => (prev === rowKey ? null : rowKey))
                    }
                    className="flex w-full items-center justify-between gap-4 p-4 text-left hover:bg-slate-50/80 transition-colors"
                  >
                    <div className="flex items-start gap-3 min-w-0 flex-1">
                      <Briefcase className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
                      <div className="min-w-0">
                        <p className="font-medium text-slate-900">{app.companyName}</p>
                        <p className="text-sm text-slate-600">{app.roleName}</p>
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-slate-500">
                          {savedLabel && <span>Saved {savedLabel}</span>}
                          {app.status && (
                            <span className="rounded-full bg-slate-100 px-2 py-0.5 capitalize">
                              {app.status}
                            </span>
                          )}
                          {app.coverLetter && (
                            <span className="text-green-700">Cover letter</span>
                          )}
                          {tailored && (
                            <span className="text-blue-700">Tailored resume JSON</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span
                        className={cn(
                          'rounded-full px-3 py-1 text-sm font-medium hidden sm:inline-flex',
                          getScoreColor(app.matchScore ?? 0)
                        )}
                      >
                        {getScoreDisplay(app.matchScore)}
                      </span>
                      {isOpen ? (
                        <ChevronUp className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      )}
                    </div>
                  </button>

                  {isOpen && (
                    <div className="border-t border-slate-100 px-4 pb-4 pt-3 space-y-6 bg-slate-50/50">
                      <StoredBlock
                        title="Job description"
                        empty={!app.jobDescription?.trim()}
                      >
                        <pre className="text-sm whitespace-pre-wrap text-slate-800 bg-white border rounded-lg p-3 max-h-56 overflow-y-auto font-sans leading-relaxed">
                          {app.jobDescription}
                        </pre>
                      </StoredBlock>

                      <StoredBlock
                        title="Cover letter"
                        empty={!app.coverLetter?.trim()}
                      >
                        <pre className="text-sm whitespace-pre-wrap text-slate-800 bg-white border rounded-lg p-3 max-h-64 overflow-y-auto font-sans leading-relaxed">
                          {app.coverLetter ?? ''}
                        </pre>
                      </StoredBlock>

                      {summary && (
                        <StoredBlock title="Professional summary (from tailored resume)">
                          <pre className="text-sm whitespace-pre-wrap text-slate-800 bg-white border rounded-lg p-3 font-sans leading-relaxed">
                            {summary}
                          </pre>
                        </StoredBlock>
                      )}

                      <StoredBlock
                        title="Tailored resume (full JSON)"
                        empty={!tailored || typeof tailored !== 'object'}
                      >
                        <pre className="text-xs whitespace-pre-wrap font-mono text-slate-800 bg-slate-900 text-slate-100 rounded-lg p-3 max-h-80 overflow-auto">
                          {JSON.stringify(tailored, null, 2)}
                        </pre>
                      </StoredBlock>
                    </div>
                  )}
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </>
  );
}
