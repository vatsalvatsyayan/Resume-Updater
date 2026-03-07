import { useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, FormProvider, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast, Toaster } from 'sonner';
import { Send, RotateCcw } from 'lucide-react';

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
import { useUIStore } from '@/stores/uiStore';
import { useFormStore } from '@/stores/formStore';
import type { ProfileFormData } from '@/types/form.types';
import { defaultProfileFormData } from '@/types/form.types';

export function ProfileFormPage() {
  const navigate = useNavigate();
  const { isSubmitting, setIsSubmitting, setSubmitError } = useUIStore();
  const { saveDraft, loadDraft, clearDraft } = useFormStore();

  const methods = useForm<ProfileFormData>({
    // resolver typing can be noisy with nested zod schemas
    resolver: zodResolver(profileFormSchema) as never,
    defaultValues: loadDraft() ?? defaultProfileFormData,
    mode: 'onBlur',
  });

  const { handleSubmit, reset, watch, formState } = methods;

  useEffect(() => {
    const subscription = watch((value) => {
      saveDraft(value as ProfileFormData);
    });

    return () => subscription.unsubscribe();
  }, [watch, saveDraft]);

  const onSubmit: SubmitHandler<ProfileFormData> = async (data) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      saveDraft(data);
      await submitRegistration(data);
      toast.success('Profile saved successfully!');
      navigate('/applications');
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Something went wrong';

      setSubmitError(message);
      toast.error('Failed to save profile', {
        description: message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = useCallback(() => {
    if (window.confirm('Are you sure you want to reset the form? All data will be lost.')) {
      reset(defaultProfileFormData);
      clearDraft();
      toast.info('Form reset');
    }
  }, [reset, clearDraft]);

  return (
    <>
      <Header />
      <Toaster richColors position="top-right" />

      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <SectionNav />

          <PersonalInfoSection />
          <EducationSection />
          <WorkExperienceSection />
          <ProjectsSection />
          <SkillsSection />
          <CertificationsSection />
          <VolunteerSection />
          <LeadershipSection />

          <div className="flex justify-between mt-8">
            <Button type="button" variant="outline" onClick={handleReset}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </Button>

            <Button type="submit" disabled={isSubmitting}>
              <Send className="w-4 h-4 mr-2" />
              Submit Profile
            </Button>
          </div>

          {Object.keys(formState.errors).length > 0 && (
            <p className="mt-4 text-sm text-red-600">
              Please fix errors before submitting.
            </p>
          )}
        </form>
      </FormProvider>
    </>
  );
}