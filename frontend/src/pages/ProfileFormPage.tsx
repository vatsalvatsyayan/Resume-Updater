import { useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { toast, Toaster } from 'sonner';
import { Save, Send, RotateCcw, Clock } from 'lucide-react';

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
import { submitRegistration } from '@/lib/api';
import { useFormStore } from '@/stores/formStore';
import { useUIStore } from '@/stores/uiStore';
import type { ProfileFormData } from '@/types/form.types';
import { defaultProfileFormData } from '@/types/form.types';

export function ProfileFormPage() {
  const navigate = useNavigate();
  const { draft, saveDraft, clearDraft, lastSaved, hasDraft } = useFormStore();
  const { isSubmitting, setIsSubmitting, setSubmitError } = useUIStore();

  const methods = useForm<ProfileFormData>({
    // @ts-expect-error - zodResolver types are complex with nested schemas
    resolver: zodResolver(profileFormSchema),
    defaultValues: draft || defaultProfileFormData,
    mode: 'onBlur',
  });

  const { handleSubmit, watch, reset, formState } = methods;

  // Auto-save draft with debounce
  const debouncedSave = useMemo(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    return (data: ProfileFormData) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        saveDraft(data);
      }, 2000);
    };
  }, [saveDraft]);

  useEffect(() => {
    const subscription = watch((data) => {
      debouncedSave(data as ProfileFormData);
    });
    return () => subscription.unsubscribe();
  }, [watch, debouncedSave]);

  // Restore draft on mount
  useEffect(() => {
    if (hasDraft() && draft) {
      toast.info('Draft restored', {
        description: 'Your previous work has been loaded.',
        action: {
          label: 'Start Fresh',
          onClick: () => {
            reset(defaultProfileFormData);
            clearDraft();
          },
        },
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSubmit = useCallback(async (data: ProfileFormData) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await submitRegistration(data);
      clearDraft();
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
  }, [clearDraft, navigate, setIsSubmitting, setSubmitError]);

  const handleReset = useCallback(() => {
    if (window.confirm('Are you sure you want to reset the form? All data will be lost.')) {
      reset(defaultProfileFormData);
      clearDraft();
      toast.info('Form reset');
    }
  }, [reset, clearDraft]);

  const handleSaveDraft = useCallback(() => {
    const data = methods.getValues();
    saveDraft(data);
    toast.success('Draft saved');
  }, [methods, saveDraft]);

  return (
    <div className="min-h-screen bg-slate-50">
      <Toaster position="top-right" richColors closeButton />
      <Header variant="minimal" />
      <SectionNav />

      <main className="max-w-4xl mx-auto px-4 pb-32 pt-6">
        {/* Page Header */}
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
          {lastSaved && (
            <div className="flex items-center gap-2 mt-3 text-sm text-slate-500">
              <Clock className="w-4 h-4" />
              <span>
                Last saved: {new Date(lastSaved).toLocaleTimeString()}
              </span>
            </div>
          )}
        </motion.div>

        {/* Form */}
        <FormProvider {...methods}>
          {/* @ts-expect-error - handleSubmit type inference issue */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <PersonalInfoSection />
            <EducationSection />
            <WorkExperienceSection />
            <ProjectsSection />
            <SkillsSection />
            <CertificationsSection />
            <VolunteerSection />
            <LeadershipSection />

            {/* Form Actions */}
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
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleSaveDraft}
                      leftIcon={<Save className="w-4 h-4" />}
                    >
                      Save Draft
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
