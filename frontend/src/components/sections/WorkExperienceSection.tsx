import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { Briefcase, Plus } from 'lucide-react';
import { Input, Textarea, Button } from '@/components/ui';
import { FormSection, EntryCard, DateRangeField, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultWorkExperience } from '@/types/form.types';

export function WorkExperienceSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'workExperience',
  });

  return (
    <FormSection
      id="experience"
      title="Work Experience"
      description="Your professional journey"
      icon={Briefcase}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultWorkExperience)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Experience
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => (
          <EntryCard
            key={field.id}
            title="Work Experience"
            subtitle={`Position ${index + 1}`}
            index={index}
            onRemove={() => remove(index)}
            canRemove={fields.length > 1}
          >
            <FormField>
              <Controller
                name={`workExperience.${index}.companyName`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Company Name"
                    placeholder="Google"
                    required
                    {...field}
                    error={errors.workExperience?.[index]?.companyName?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`workExperience.${index}.position`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Position/Title"
                    placeholder="Software Engineer"
                    required
                    {...field}
                    error={errors.workExperience?.[index]?.position?.message}
                  />
                )}
              />
            </FormField>

            <FormField className="md:col-span-2">
              <Controller
                name={`workExperience.${index}.location`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Location"
                    placeholder="Mountain View, CA"
                    {...field}
                    value={field.value || ''}
                    error={errors.workExperience?.[index]?.location?.message}
                  />
                )}
              />
            </FormField>

            <DateRangeField
              startName={`workExperience.${index}.startDate`}
              endName={`workExperience.${index}.endDate`}
              presentName={`workExperience.${index}.isPresent`}
              presentLabel="Currently working here"
            />

            <FormField className="md:col-span-2">
              <Controller
                name={`workExperience.${index}.summary`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Summary"
                    placeholder="Brief summary of your role"
                    {...field}
                    value={field.value || ''}
                    error={errors.workExperience?.[index]?.summary?.message}
                    hint="One-line summary of your responsibilities"
                  />
                )}
              />
            </FormField>

            <FormField className="md:col-span-2">
              <Controller
                name={`workExperience.${index}.description`}
                control={control}
                render={({ field }) => (
                  <Textarea
                    label="Description"
                    placeholder="Describe your key achievements and responsibilities..."
                    {...field}
                    value={field.value || ''}
                    error={errors.workExperience?.[index]?.description?.message}
                    hint="Use bullet points or detailed paragraphs"
                  />
                )}
              />
            </FormField>
          </EntryCard>
        ))}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <Briefcase className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No work experience entries yet</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultWorkExperience)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Your First Position
          </Button>
        </div>
      )}
    </FormSection>
  );
}
