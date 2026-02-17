import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { Heart, Plus } from 'lucide-react';
import { Input, Textarea, Button } from '@/components/ui';
import { FormSection, EntryCard, DateRangeField, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultVolunteer } from '@/types/form.types';

export function VolunteerSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'volunteer',
  });

  return (
    <FormSection
      id="volunteer"
      title="Volunteer Experience"
      description="Your community contributions"
      icon={Heart}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultVolunteer)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Volunteer
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => (
          <EntryCard
            key={field.id}
            title="Volunteer Experience"
            subtitle={`Entry ${index + 1}`}
            index={index}
            onRemove={() => remove(index)}
          >
            <FormField>
              <Controller
                name={`volunteer.${index}.organizationName`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Organization Name"
                    placeholder="Code.org"
                    required
                    {...field}
                    error={errors.volunteer?.[index]?.organizationName?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`volunteer.${index}.role`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Role"
                    placeholder="Teaching Assistant"
                    required
                    {...field}
                    error={errors.volunteer?.[index]?.role?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`volunteer.${index}.cause`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Cause"
                    placeholder="Education"
                    {...field}
                    value={field.value || ''}
                    error={errors.volunteer?.[index]?.cause?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`volunteer.${index}.location`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Location"
                    placeholder="Remote"
                    {...field}
                    value={field.value || ''}
                    error={errors.volunteer?.[index]?.location?.message}
                  />
                )}
              />
            </FormField>

            <DateRangeField
              startName={`volunteer.${index}.startDate`}
              endName={`volunteer.${index}.endDate`}
              presentName={`volunteer.${index}.isPresent`}
              presentLabel="Currently volunteering"
            />

            <FormField className="md:col-span-2">
              <Controller
                name={`volunteer.${index}.description`}
                control={control}
                render={({ field }) => (
                  <Textarea
                    label="Description"
                    placeholder="Describe your volunteer work and impact..."
                    {...field}
                    value={field.value || ''}
                    error={errors.volunteer?.[index]?.description?.message}
                  />
                )}
              />
            </FormField>
          </EntryCard>
        ))}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <Heart className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No volunteer experience yet</p>
          <p className="text-sm text-slate-400 mt-1">Showcase your community involvement</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultVolunteer)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Volunteer Experience
          </Button>
        </div>
      )}
    </FormSection>
  );
}
