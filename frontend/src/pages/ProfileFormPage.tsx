import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, FormProvider, type Resolver, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { toast, Toaster } from 'sonner';
import { Send, RotateCcw, Upload } from 'lucide-react';

import { Button } from '@/components/ui';
import { Header, SectionNav } from '@/components/layout';
import {
  PersonalInfoSection,
  EducationSection,
  WorkExperienceSection,
  ProjectsSection,
  SkillsSection,
  CertificationsSection,
  VolunteerSection,
  LeadershipSection,
} from '@/components/sections';

import { profileFormSchema } from '@/lib/validation';
import { getProfile, importProfile, submitRegistration } from '@/lib/api';
import { useUIStore } from '@/stores/uiStore';
import type { ProfileFormData } from '@/types/form.types';
import { defaultProfileFormData } from '@/types/form.types';
import { useUser } from '@clerk/clerk-react';

function mapProfileToFormData(profile: any, fallbackEmail: string): ProfileFormData {
  return {
    ...defaultProfileFormData,
    personalInfo: {
      ...defaultProfileFormData.personalInfo,
      name: profile.personalInfo?.name ?? '',
      email: profile.personalInfo?.email ?? profile.email ?? fallbackEmail,
      portfolioWebsite: profile.personalInfo?.portfolioWebsite ?? '',
      githubUrl: profile.personalInfo?.githubUrl ?? '',
      linkedinUrl: profile.personalInfo?.linkedinUrl ?? '',
    },
    education: (profile.education ?? []).map((edu: any) => ({
      id: edu.id ?? '',
      universityName: edu.universityName ?? edu.school ?? '',
      courseName: edu.courseName ?? edu.degree ?? '',
      courseType: edu.courseType ?? edu.degree_type ?? edu.degreeType ?? '',
      major: edu.major ?? '',
      gpa:
        edu.gpa != null && edu.gpa !== ''
          ? String(edu.gpa)
          : '',
      location: edu.location ?? '',
      startDate: edu.startDate ?? edu.start_date ?? '',
      endDate: edu.endDate ?? edu.end_date ?? '',
      isPresent:
        edu.isPresent ?? edu.currently_enrolled ?? edu.currentlyEnrolled ?? false,
    })),
    workExperience: (profile.workExperience ?? []).map((work: any) => ({
      id: work.id ?? '',
      companyName: work.companyName ?? '',
      position: work.position ?? '',
      location: work.location ?? '',
      startDate: work.startDate ?? '',
      endDate: work.endDate ?? '',
      isPresent: work.isPresent ?? false,
      summary: work.summary ?? '',
      description: work.description ?? '',
    })),
    projects: (profile.projects ?? []).map((project: any) => ({
      id: project.id ?? '',
      projectName: project.projectName ?? '',
      link: project.link ?? '',
      techStack: project.techStack ?? [],
      summary: project.summary ?? '',
      description: project.description ?? '',
    })),
    skills: {
      ...defaultProfileFormData.skills,
      programmingLanguages:
        profile.skills?.programmingLanguages ??
        profile.skills?.programming_languages ??
        [],
      frameworks: profile.skills?.frameworks ?? [],
      databases: profile.skills?.databases ?? [],
      toolsAndTechnologies:
        profile.skills?.toolsAndTechnologies ??
        profile.skills?.tools ??
        [],
      cloud: profile.skills?.cloud ?? [],
      ai:
        profile.skills?.ai ??
        profile.skills?.ai_ml ??
        [],
      other: profile.skills?.other ?? [],
    },
    certifications: (
      profile.certifications ??
      profile.certification ??
      []
    ).map((cert: any) => ({
      id: cert.id ?? '',
      name: cert.name ?? '',
      issuingOrganization:
        cert.issuingOrganization ??
        cert.issuing_organization ??
        cert.organization ??
        '',
      issueDate:
        cert.issueDate ??
        cert.issue_date ??
        '',
      expiryDate:
        cert.expiryDate ??
        cert.expiry_date ??
        '',
      hasNoExpiry:
        cert.hasNoExpiry ??
        cert.has_no_expiry ??
        cert.no_expiry ??
        false,
      credentialId:
        cert.credentialId ??
        cert.credential_id ??
        '',
      credentialUrl:
        cert.credentialUrl ??
        cert.credential_url ??
        '',
    })),
    volunteer: (
      profile.volunteer ??
      profile.volunteerExperience ??
      profile.volunteer_experience ??
      []
    ).map((vol: any) => ({
      id: vol.id ?? '',
      organizationName:
        vol.organizationName ??
        vol.organization ??
        '',
      role: vol.role ?? '',
      cause: vol.cause ?? '',
      location: vol.location ?? '',
      startDate:
        vol.startDate ??
        vol.start_date ??
        '',
      endDate:
        vol.endDate ??
        vol.end_date ??
        '',
      isPresent:
        vol.isPresent ??
        vol.currentlyVolunteering ??
        vol.currently_volunteering ??
        false,
      description: vol.description ?? '',
    })),
    leadership: (profile.leadership ?? []).map((lead: any) => ({
      id: lead.id ?? '',
      title: lead.title ?? '',
      organization: lead.organization ?? '',
      startDate: lead.startDate ?? '',
      endDate: lead.endDate ?? '',
      isPresent: lead.isPresent ?? false,
      description: lead.description ?? '',
    })),
  };
}

export function ProfileFormPage() {
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const { isSubmitting, setIsSubmitting, setSubmitError } = useUIStore();
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  const methods = useForm<ProfileFormData>({
    resolver: zodResolver(profileFormSchema) as Resolver<ProfileFormData>,
    defaultValues: defaultProfileFormData,
    mode: 'onBlur',
  });

  const { handleSubmit, reset, formState } = methods;

  useEffect(() => {
    const loadProfile = async () => {
      if (!isLoaded) return;

      const userEmail = user?.primaryEmailAddress?.emailAddress;

      if (!userEmail) {
        setIsProfileLoading(false);
        return;
      }

      try {
        const profile = await getProfile(userEmail);
        
        if (profile) {
          reset(mapProfileToFormData(profile, userEmail));
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setIsProfileLoading(false);
      }
    };

    loadProfile();
  }, [isLoaded, user, reset]);

  const onSubmit: SubmitHandler<ProfileFormData> = useCallback(async (data) => {
    if (!user?.primaryEmailAddress?.emailAddress) {
      setSubmitError('User email not found');
      toast.error('Unable to get your email. Please log out and sign in again.');
      return;
    }

    const userEmail = user.primaryEmailAddress.emailAddress;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await submitRegistration(data, userEmail);
      toast.success('Profile saved successfully!');
      navigate('/success');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Something went wrong';
      setSubmitError(message);
      toast.error('Failed to save profile', {
        description: message,
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [navigate, user, setIsSubmitting, setSubmitError]);

  const handleResumeImport = useCallback(async () => {
    const userEmail = user?.primaryEmailAddress?.emailAddress;

    if (!resumeFile) {
      toast.error('Choose a resume file before importing.');
      return;
    }

    if (!userEmail) {
      toast.error('Unable to get your email. Please log out and sign in again.');
      return;
    }

    setIsImporting(true);

    try {
      const result = await importProfile({ resumeFile }, userEmail);
      reset(mapProfileToFormData(result.data, userEmail));

      if (result.warnings.length > 0) {
        toast.warning('Profile imported with warnings', {
          description: result.warnings.join(' '),
        });
      } else {
        toast.success('Profile imported from your resume.');
      }

      setResumeFile(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to import profile';
      toast.error('Resume import failed', {
        description: message,
      });
    } finally {
      setIsImporting(false);
    }
  }, [reset, resumeFile, user]);

  const handleReset = useCallback(() => {
    if (window.confirm('Are you sure you want to reset the form? All data will be lost.')) {
      reset(defaultProfileFormData);
      toast.info('Form reset');
    }
  }, [reset]);

  if (isProfileLoading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Toaster position="top-right" richColors closeButton />
        <Header />
        <SectionNav />
        <main className="max-w-4xl mx-auto px-4 pb-32 pt-6">
          <p className="text-slate-600">Loading profile...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Toaster position="top-right" richColors closeButton />
      <Header />
      <SectionNav />

      <main className="max-w-4xl mx-auto px-4 pb-32 pt-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Build Your Profile
          </h1>
          <p className="text-slate-600">
            Complete your professional profile to generate tailored resumes for any job.
          </p>
        </motion.div>

        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <div className="space-y-1">
                  <h2 className="text-xl font-semibold text-slate-900">
                    Import From Resume
                  </h2>
                  <p className="text-sm text-slate-600">
                    Upload a PDF, DOCX, or TXT resume to auto-fill this profile form.
                    Importing will replace the current form values.
                  </p>
                </div>

                <div className="flex w-full flex-col gap-3 md:w-auto md:min-w-[360px]">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.md"
                    onChange={(event) => {
                      setResumeFile(event.target.files?.[0] ?? null);
                    }}
                    className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-xl file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
                  />
                  <div className="flex items-center justify-between gap-3">
                    <span className="truncate text-sm text-slate-500">
                      {resumeFile ? resumeFile.name : 'No file selected'}
                    </span>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleResumeImport}
                      isLoading={isImporting}
                      disabled={!resumeFile}
                      leftIcon={<Upload className="h-4 w-4" />}
                    >
                      Import Resume
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>

            <PersonalInfoSection />
            <EducationSection />
            <WorkExperienceSection />
            <ProjectsSection />
            <SkillsSection />
            <CertificationsSection />
            <VolunteerSection />
            <LeadershipSection />

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="sticky bottom-6 z-50"
            >
              <div className="bg-white/95 backdrop-blur-lg rounded-2xl border border-slate-200 shadow-xl p-4">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={handleReset}
                      leftIcon={<RotateCcw className="w-4 h-4" />}
                    >
                      Reset
                    </Button>
                  </div>

                  <div className="flex items-center gap-3">
                    {formState.errors && Object.keys(formState.errors).length > 0 && (
                      <span className="text-sm text-red-500">
                        Please fix errors before submitting
                      </span>
                    )}
                    <Button
                      type="submit"
                      variant="secondary"
                      size="lg"
                      isLoading={isSubmitting}
                      rightIcon={<Send className="w-4 h-4" />}
                    >
                      Submit Profile
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          </form>
        </FormProvider>
      </main>
    </div>
  );
}
