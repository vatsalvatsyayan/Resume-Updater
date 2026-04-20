import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Briefcase, ChevronDown, ChevronUp, Download, Loader2, Save, ThumbsDown, ThumbsUp } from 'lucide-react';
import { toast, Toaster } from 'sonner';
import { useUser } from '@clerk/clerk-react';

import { FormattedTailoredResume } from '@/components/FormattedTailoredResume';
import {
  GenerationProgressOverlay,
  type GenerationPhase,
} from '@/components/GenerationProgressOverlay';
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
  evaluateResumeMatch,
  getApplications,
  getProfile,
  patchApplication,
  renderTailoredResumePdf,
  type Application,
  type ResumeMatchEvaluation,
} from '@/lib/api';
import { useFormStore } from '@/stores/formStore';
import { defaultProfileFormData, type ProfileFormData } from '@/types/form.types';

function getScoreColor(score: number | undefined) {
  if (score === undefined || score === null) {
    return 'text-slate-500 bg-slate-100';
  }
  if (score === 0) return 'text-slate-500 bg-slate-100';
  if (score <= 30) return 'text-red-600 bg-red-50';
  if (score <= 60) return 'text-amber-600 bg-amber-50';
  return 'text-green-600 bg-green-50';
}

function getScoreDisplay(score: number | undefined) {
  if (score === undefined || score === null) return '—';
  return `${score}%`;
}

function getEffectiveScore(app: Application): number | undefined {
  return app.matchEvaluation?.final_score ?? app.matchScore;
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
      phone: profile?.personalInfo?.phone ?? null,
      location: profile?.personalInfo?.location ?? null,
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
  const [generationPhase, setGenerationPhase] = useState<GenerationPhase | null>(null);
  const [profile, setProfile] = useState<ProfileFormData>(defaultProfileFormData);
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [applications, setApplications] = useState<Application[]>([]);
  const [isAppsLoading, setIsAppsLoading] = useState(true);
  const [expandedKey, setExpandedKey] = useState<string | null>(null);
  const [coverDraft, setCoverDraft] = useState('');
  const [resumeJsonDraft, setResumeJsonDraft] = useState('');
  const [busyCover, setBusyCover] = useState<'save' | 'download' | null>(null);
  const [busyResume, setBusyResume] = useState<'save' | 'download' | null>(null);
  const [busyAnalysis, setBusyAnalysis] = useState<string | null>(null);
  const [busyFeedback, setBusyFeedback] = useState<string | null>(null);

  const { loadDraft, saveDraft } = useFormStore();

  const getExpandedApp = useCallback((): Application | null => {
    if (!expandedKey) return null;
    const idx = applications.findIndex((a, i) => (a._id ?? `app-${i}`) === expandedKey);
    return idx === -1 ? null : applications[idx] ?? null;
  }, [applications, expandedKey]);

  useEffect(() => {
    if (!expandedKey) return;
    const idx = applications.findIndex((a, i) => (a._id ?? `app-${i}`) === expandedKey);
    if (idx === -1) return;
    const app = applications[idx];
    setCoverDraft(app.coverLetter ?? '');
    setResumeJsonDraft(
      app.tailoredResume && typeof app.tailoredResume === 'object'
        ? JSON.stringify(app.tailoredResume, null, 2)
        : '{}'
    );
  }, [expandedKey, applications]);

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

  const parsedResumeDraft = useMemo(() => {
    try {
      const p = JSON.parse(resumeJsonDraft);
      if (p !== null && typeof p === 'object' && !Array.isArray(p)) {
        return { ok: true as const, data: p as Record<string, unknown> };
      }
      return { ok: false as const, error: 'Tailored resume must be a JSON object.' };
    } catch {
      return {
        ok: false as const,
        error: 'Invalid JSON — fix raw JSON below to update the preview.',
      };
    }
  }, [resumeJsonDraft]);

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
    setGenerationPhase('resume');

    try {
      const payload = buildResumePayload(profile, data);
      const gen = await generateResume(payload);

      const safeCompany = data.companyName.replace(/\s+/g, '-');
      const safeRole = data.roleName.replace(/\s+/g, '-');
      const resumeFilename = `resume-${safeCompany}-${safeRole}.pdf`;

      const pdfBlob = base64ToBlob(gen.pdf_base64);
      downloadPdfBlob(pdfBlob, resumeFilename);

      const tailoredResume = gen.tailored_resume as Record<string, unknown>;
      const matchEvaluation = gen.match_evaluation as ResumeMatchEvaluation | undefined;
      const rawMatch = gen.match_score ?? (gen as { matchScore?: number }).matchScore;
      const matchScore = typeof rawMatch === 'number' ? rawMatch : undefined;

      let coverLetterText: string | null = null;
      let coverLetterNotice = '';

      if (data.generateCoverLetter) {
        setGenerationPhase('cover');
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

      setGenerationPhase('saving');
      try {
        await createApplication({
          email: userEmail,
          companyName: data.companyName,
          roleName: data.roleName,
          jobDescription: data.jobDescription,
          tailoredResume,
          coverLetter: coverLetterText,
          matchScore,
          matchEvaluation,
          sourceProfile: profile,
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
        `Resume${coverLetterNotice} for ${data.companyName} (${data.roleName}) downloaded!${
          matchScore != null ? ` Job match: ${matchScore}%.` : ''
        }`
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Failed to generate resume';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
      setGenerationPhase(null);
    }
  };

  const handleSaveCoverLetter = useCallback(async () => {
    const app = getExpandedApp();
    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!app?._id || !userEmail) {
      toast.error('Cannot save: missing application id or sign-in.');
      return;
    }
    setBusyCover('save');
    try {
      await patchApplication(userEmail, app._id, { coverLetter: coverDraft });
      await refreshApplications();
      toast.success('Cover letter saved.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to save cover letter.');
    } finally {
      setBusyCover(null);
    }
  }, [coverDraft, getExpandedApp, refreshApplications, user]);

  const handleDownloadCoverLetterPdf = useCallback(async () => {
    const app = getExpandedApp();
    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!app || !userEmail) {
      toast.error('Unable to download.');
      return;
    }
    if (!hasUsableProfile) {
      toast.error('Complete your profile (name and email) first.');
      return;
    }
    const trimmed = coverDraft.trim();
    if (!trimmed) {
      toast.error('Add cover letter text before downloading.');
      return;
    }
    setBusyCover('download');
    try {
      const blob = await generateCoverLetterPdf(
        buildCoverLetterPayload(
          profile,
          {
            companyName: app.companyName,
            roleName: app.roleName,
            jobDescription: app.jobDescription,
          },
          { existing_cover_letter: trimmed }
        )
      );
      const safeCompany = app.companyName.replace(/\s+/g, '-');
      const safeRole = app.roleName.replace(/\s+/g, '-');
      downloadPdfBlob(blob, `cover-letter-${safeCompany}-${safeRole}.pdf`);
      toast.success('Cover letter PDF downloaded.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to download PDF.');
    } finally {
      setBusyCover(null);
    }
  }, [coverDraft, getExpandedApp, hasUsableProfile, profile, user]);

  const handleRunAnalysis = useCallback(async () => {
    const app = getExpandedApp();
    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!app?._id || !userEmail) {
      toast.error('Cannot run analysis: missing application id or sign-in.');
      return;
    }
    if (!app.tailoredResume || typeof app.tailoredResume !== 'object') {
      toast.error('Generate or save a tailored resume first.');
      return;
    }
    const rowKey = app._id;
    setBusyAnalysis(rowKey);
    try {
      const result = await evaluateResumeMatch({
        jobDescription: app.jobDescription,
        tailoredResume: app.tailoredResume,
        originalProfile: (app.sourceProfile ?? profile) as unknown as object,
      });
      await patchApplication(userEmail, app._id, {
        matchScore: result.match_score,
        matchEvaluation: result.match_evaluation,
      });
      await refreshApplications();
      toast.success('ATS analysis completed.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to run ATS analysis.');
    } finally {
      setBusyAnalysis(null);
    }
  }, [getExpandedApp, profile, refreshApplications, user]);

  const handleArtifactFeedback = useCallback(
    async (app: Application, target: 'coverLetter' | 'resume', selected: 'up' | 'down') => {
      const userEmail = user?.primaryEmailAddress?.emailAddress;
      if (!app._id || !userEmail) {
        toast.error('Cannot save feedback: missing application id or sign-in.');
        return;
      }
      const current = target === 'coverLetter' ? app.coverLetterFeedback : app.resumeFeedback;
      const next = current === selected ? null : selected;
      const busyKey = `${app._id}:${target}`;
      setBusyFeedback(busyKey);
      try {
        const updated = await patchApplication(userEmail, app._id, {
          ...(target === 'coverLetter'
            ? { coverLetterFeedback: next }
            : { resumeFeedback: next }),
        });
        setApplications((prev) =>
          prev.map((item) => (item._id === updated._id ? { ...item, ...updated } : item))
        );
      } catch (e) {
        toast.error(e instanceof Error ? e.message : 'Failed to save feedback.');
      } finally {
        setBusyFeedback(null);
      }
    },
    [user]
  );

  const handleSaveTailoredResume = useCallback(async () => {
    const app = getExpandedApp();
    const userEmail = user?.primaryEmailAddress?.emailAddress;
    if (!app?._id || !userEmail) {
      toast.error('Cannot save: missing application id or sign-in.');
      return;
    }
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(resumeJsonDraft) as Record<string, unknown>;
    } catch {
      toast.error('Invalid JSON. Fix syntax before saving.');
      return;
    }
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      toast.error('Tailored resume must be a JSON object.');
      return;
    }
    setBusyResume('save');
    try {
      await patchApplication(userEmail, app._id, { tailoredResume: parsed });
      await refreshApplications();
      toast.success('Tailored resume saved.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to save resume.');
    } finally {
      setBusyResume(null);
    }
  }, [getExpandedApp, refreshApplications, resumeJsonDraft, user]);

  const handleDownloadTailoredResumePdf = useCallback(async () => {
    const app = getExpandedApp();
    if (!app) return;
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(resumeJsonDraft) as Record<string, unknown>;
    } catch {
      toast.error('Invalid JSON. Fix syntax before downloading.');
      return;
    }
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      toast.error('Tailored resume must be a JSON object.');
      return;
    }
    setBusyResume('download');
    try {
      const blob = await renderTailoredResumePdf(parsed);
      const safeCompany = app.companyName.replace(/\s+/g, '-');
      const safeRole = app.roleName.replace(/\s+/g, '-');
      downloadPdfBlob(blob, `resume-${safeCompany}-${safeRole}.pdf`);
      toast.success('Resume PDF downloaded.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to render PDF.');
    } finally {
      setBusyResume(null);
    }
  }, [getExpandedApp, resumeJsonDraft]);

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
        onOpenChange={(next) => {
          if (!next && isSubmitting) return;
          setIsModalOpen(next);
        }}
        onSubmit={handleTailorSubmit}
        isLoading={isSubmitting}
      />

      <GenerationProgressOverlay open={isSubmitting} phase={generationPhase} />

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
              const canPersist = Boolean(app._id);
              const effectiveScore = getEffectiveScore(app);

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
                            <span className="text-blue-700">Tailored resume</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span
                        title="Job match"
                        className={cn(
                          'rounded-full px-3 py-1 text-sm font-medium hidden sm:inline-flex',
                          getScoreColor(effectiveScore)
                        )}
                      >
                        {getScoreDisplay(effectiveScore)}
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

                      {/* Never use StoredBlock empty= here: without analysis we still show the run button */}
                      <StoredBlock title="ATS match analysis">
                        {app.matchEvaluation ? (
                          <div className="rounded-lg border border-slate-200 bg-white p-3 space-y-3 text-sm">
                            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                              <div className="rounded-md bg-slate-50 px-2.5 py-2">
                                <p className="text-[11px] uppercase tracking-wide text-slate-500">Final</p>
                                <p className="font-semibold text-slate-900">{app.matchEvaluation.final_score}%</p>
                              </div>
                              <div className="rounded-md bg-slate-50 px-2.5 py-2">
                                <p className="text-[11px] uppercase tracking-wide text-slate-500">ATS match</p>
                                <p className="font-semibold text-slate-900">{app.matchEvaluation.ats_match_score}%</p>
                              </div>
                              <div className="rounded-md bg-slate-50 px-2.5 py-2">
                                <p className="text-[11px] uppercase tracking-wide text-slate-500">Format</p>
                                <p className="font-semibold text-slate-900">{app.matchEvaluation.ats_format_score}%</p>
                              </div>
                              <div className="rounded-md bg-slate-50 px-2.5 py-2">
                                <p className="text-[11px] uppercase tracking-wide text-slate-500">Hallucination risk</p>
                                <p className="font-semibold text-slate-900">{app.matchEvaluation.hallucination_risk_score}%</p>
                              </div>
                            </div>

                            {app.matchEvaluation.summary && (
                              <p className="text-slate-700 text-sm">{app.matchEvaluation.summary}</p>
                            )}

                            {(app.matchEvaluation.ats_strengths.length > 0 ||
                              app.matchEvaluation.ats_gaps.length > 0 ||
                              app.matchEvaluation.format_issues.length > 0 ||
                              app.matchEvaluation.hallucination_findings.length > 0) && (
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                <span className="inline-flex w-fit items-center rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                                  {app.matchEvaluation.ats_strengths.length} strengths
                                </span>
                                <span className="inline-flex w-fit items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                                  {app.matchEvaluation.ats_gaps.length} gaps
                                </span>
                                <span className="inline-flex w-fit items-center rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700">
                                  {app.matchEvaluation.format_issues.length} format issues
                                </span>
                                <span className="inline-flex w-fit items-center rounded-full bg-rose-50 px-2 py-0.5 text-xs font-medium text-rose-700">
                                  {app.matchEvaluation.hallucination_findings.length} hallucination checks
                                </span>
                              </div>
                            )}

                            {app.matchEvaluation.ats_strengths.length > 0 && (
                              <details className="rounded-md border border-slate-200 bg-white">
                                <summary className="cursor-pointer px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 hover:bg-slate-50">
                                  Strengths ({app.matchEvaluation.ats_strengths.length})
                                </summary>
                                <ul className="list-disc border-t border-slate-100 px-6 py-2 space-y-1 text-sm text-slate-700">
                                  {app.matchEvaluation.ats_strengths.map((s, i) => (
                                    <li key={`strength-${i}`}>{s}</li>
                                  ))}
                                </ul>
                              </details>
                            )}

                            {app.matchEvaluation.ats_gaps.length > 0 && (
                              <details className="rounded-md border border-slate-200 bg-white">
                                <summary className="cursor-pointer px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 hover:bg-slate-50">
                                  Gaps ({app.matchEvaluation.ats_gaps.length})
                                </summary>
                                <ul className="list-disc border-t border-slate-100 px-6 py-2 space-y-1 text-sm text-slate-700">
                                  {app.matchEvaluation.ats_gaps.map((s, i) => (
                                    <li key={`gap-${i}`}>{s}</li>
                                  ))}
                                </ul>
                              </details>
                            )}

                            {app.matchEvaluation.format_issues.length > 0 && (
                              <details className="rounded-md border border-slate-200 bg-white">
                                <summary className="cursor-pointer px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 hover:bg-slate-50">
                                  Format issues ({app.matchEvaluation.format_issues.length})
                                </summary>
                                <ul className="list-disc border-t border-slate-100 px-6 py-2 space-y-1 text-sm text-slate-700">
                                  {app.matchEvaluation.format_issues.map((s, i) => (
                                    <li key={`format-${i}`}>{s}</li>
                                  ))}
                                </ul>
                              </details>
                            )}

                            {app.matchEvaluation.hallucination_findings.length > 0 && (
                              <details className="rounded-md border border-slate-200 bg-white">
                                <summary className="cursor-pointer px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 hover:bg-slate-50">
                                  Hallucination checks ({app.matchEvaluation.hallucination_findings.length})
                                </summary>
                                <div className="space-y-2 border-t border-slate-100 p-2">
                                  {app.matchEvaluation.hallucination_findings.map((f, i) => (
                                    <div key={`hallucination-${i}`} className="rounded border border-slate-200 bg-slate-50 p-2">
                                      <p className="text-sm text-slate-800">{f.claim}</p>
                                      <p className="text-xs mt-1 text-slate-600">
                                        <span
                                          className={cn(
                                            'inline-flex rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase',
                                            f.status === 'supported'
                                              ? 'bg-emerald-100 text-emerald-800'
                                              : f.status === 'unsupported'
                                                ? 'bg-rose-100 text-rose-800'
                                                : 'bg-amber-100 text-amber-800'
                                          )}
                                        >
                                          {f.status}
                                        </span>
                                        {f.reason ? `  ${f.reason}` : ''}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </details>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-slate-600">
                            Analysis is now on-demand to keep generation fast.
                          </p>
                        )}
                        <div className="mt-2 mb-3">
                          <button
                            type="button"
                            onClick={handleRunAnalysis}
                            disabled={!canPersist || !tailored || busyAnalysis === rowKey}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
                          >
                            {busyAnalysis === rowKey ? (
                              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                            ) : null}
                            {app.matchEvaluation ? 'Re-run ATS analysis' : 'Run ATS analysis'}
                          </button>
                        </div>
                      </StoredBlock>

                      <div>
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Cover letter
                          </h4>
                          <div className="flex items-center gap-1">
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                void handleArtifactFeedback(app, 'coverLetter', 'up');
                              }}
                              disabled={!canPersist || busyFeedback === `${rowKey}:coverLetter`}
                              className={cn(
                                'rounded-md border px-1.5 py-1 text-slate-500 hover:bg-slate-100 disabled:opacity-50',
                                app.coverLetterFeedback === 'up' && 'border-emerald-300 bg-emerald-50 text-emerald-700'
                              )}
                              aria-label="Thumbs up cover letter"
                              title="Thumbs up cover letter"
                            >
                              <ThumbsUp className="h-3.5 w-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                void handleArtifactFeedback(app, 'coverLetter', 'down');
                              }}
                              disabled={!canPersist || busyFeedback === `${rowKey}:coverLetter`}
                              className={cn(
                                'rounded-md border px-1.5 py-1 text-slate-500 hover:bg-slate-100 disabled:opacity-50',
                                app.coverLetterFeedback === 'down' && 'border-rose-300 bg-rose-50 text-rose-700'
                              )}
                              aria-label="Thumbs down cover letter"
                              title="Thumbs down cover letter"
                            >
                              <ThumbsDown className="h-3.5 w-3.5" />
                            </button>
                          </div>
                          {!canPersist && (
                            <span className="text-xs text-amber-700">
                              Cloud save needs a synced application (re-open after saving from Tailor).
                            </span>
                          )}
                        </div>
                        <textarea
                          value={coverDraft}
                          onChange={(e) => setCoverDraft(e.target.value)}
                          disabled={!isOpen}
                          placeholder="No cover letter yet. Paste or generate one from Tailor Resume."
                          className="w-full min-h-[200px] text-sm text-slate-800 bg-white border border-slate-200 rounded-lg p-3 font-sans leading-relaxed focus:outline-none focus:ring-2 focus:ring-slate-300 disabled:bg-slate-50"
                          spellCheck
                        />
                        <div className="flex flex-wrap gap-2 mt-2">
                          <button
                            type="button"
                            onClick={handleSaveCoverLetter}
                            disabled={!canPersist || busyCover !== null}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
                          >
                            {busyCover === 'save' ? (
                              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                            ) : (
                              <Save className="w-4 h-4" aria-hidden />
                            )}
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={handleDownloadCoverLetterPdf}
                            disabled={busyCover !== null}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 text-white px-3 py-1.5 text-sm hover:bg-slate-800 disabled:opacity-50"
                          >
                            {busyCover === 'download' ? (
                              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                            ) : (
                              <Download className="w-4 h-4" aria-hidden />
                            )}
                            Download PDF
                          </button>
                        </div>
                      </div>

                      <div>
                        <div className="mb-2 flex items-center justify-between gap-2">
                          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Tailored resume
                          </h4>
                          <div className="flex items-center gap-1">
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                void handleArtifactFeedback(app, 'resume', 'up');
                              }}
                              disabled={!canPersist || busyFeedback === `${rowKey}:resume`}
                              className={cn(
                                'rounded-md border px-1.5 py-1 text-slate-500 hover:bg-slate-100 disabled:opacity-50',
                                app.resumeFeedback === 'up' && 'border-emerald-300 bg-emerald-50 text-emerald-700'
                              )}
                              aria-label="Thumbs up resume"
                              title="Thumbs up resume"
                            >
                              <ThumbsUp className="h-3.5 w-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                void handleArtifactFeedback(app, 'resume', 'down');
                              }}
                              disabled={!canPersist || busyFeedback === `${rowKey}:resume`}
                              className={cn(
                                'rounded-md border px-1.5 py-1 text-slate-500 hover:bg-slate-100 disabled:opacity-50',
                                app.resumeFeedback === 'down' && 'border-rose-300 bg-rose-50 text-rose-700'
                              )}
                              aria-label="Thumbs down resume"
                              title="Thumbs down resume"
                            >
                              <ThumbsDown className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </div>
                        <p className="text-xs text-slate-500 mb-3">
                          Readable preview below matches your saved JSON. Open{' '}
                          <span className="font-medium text-slate-600">Edit raw JSON</span> for precise edits. Save
                          updates your application; download renders a PDF without calling the AI again.
                        </p>

                        {parsedResumeDraft.ok ? (
                          <FormattedTailoredResume
                            data={parsedResumeDraft.data}
                            className="mb-3"
                          />
                        ) : (
                          <div className="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
                            {parsedResumeDraft.error}
                          </div>
                        )}

                        <details className="overflow-hidden rounded-lg border border-slate-200 bg-white">
                          <summary className="cursor-pointer select-none px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
                            Edit raw JSON
                          </summary>
                          <div className="border-t border-slate-100 p-3">
                            <textarea
                              value={resumeJsonDraft}
                              onChange={(e) => setResumeJsonDraft(e.target.value)}
                              disabled={!isOpen}
                              placeholder='{ "name": "", "email": "", ... }'
                              className="w-full min-h-[220px] rounded-lg border border-slate-700 bg-slate-900 p-3 font-mono text-xs leading-relaxed text-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-60 whitespace-pre"
                              spellCheck={false}
                            />
                          </div>
                        </details>

                        <div className="flex flex-wrap gap-2 mt-3">
                          <button
                            type="button"
                            onClick={handleSaveTailoredResume}
                            disabled={!canPersist || busyResume !== null}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
                          >
                            {busyResume === 'save' ? (
                              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                            ) : (
                              <Save className="w-4 h-4" aria-hidden />
                            )}
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={handleDownloadTailoredResumePdf}
                            disabled={busyResume !== null}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 text-white px-3 py-1.5 text-sm hover:bg-slate-800 disabled:opacity-50"
                          >
                            {busyResume === 'download' ? (
                              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                            ) : (
                              <Download className="w-4 h-4" aria-hidden />
                            )}
                            Download PDF
                          </button>
                        </div>
                      </div>
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
