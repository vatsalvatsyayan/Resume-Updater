import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { GraduationCap, Plus } from 'lucide-react';
import { Input, Select, Button } from '@/components/ui';
import { FormSection, EntryCard, DateRangeField, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultEducation } from '@/types/form.types';

const courseTypeOptions = [
  { value: '', label: 'Select type' },
  { value: "Bachelor's", label: "Bachelor's" },
  { value: "Master's", label: "Master's" },
  { value: 'PhD', label: 'PhD' },
  { value: 'Diploma', label: 'Diploma' },
  { value: 'Certificate', label: 'Certificate' },
  { value: 'Associate', label: 'Associate' },
];

export function EducationSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'education',
  });

  return (
    <FormSection
      id="education"
      title="Education"
      description="Your academic background"
      icon={GraduationCap}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultEducation)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Education
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => (
          <EntryCard
            key={field.id}
            title="Education"
            subtitle={`Entry ${index + 1}`}
            index={index}
            onRemove={() => remove(index)}
            canRemove={fields.length > 1}
          >
            <FormField>
              <Controller
                name={`education.${index}.universityName`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="University/Institution"
                    placeholder="Stanford University"
                    required
                    {...field}
                    error={errors.education?.[index]?.universityName?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`education.${index}.courseName`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Degree/Course Name"
                    placeholder="Bachelor of Science"
                    required
                    {...field}
                    error={errors.education?.[index]?.courseName?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`education.${index}.courseType`}
                control={control}
                render={({ field }) => (
                  <Select
                    label="Type of Degree"
                    options={courseTypeOptions}
                    {...field}
                    error={errors.education?.[index]?.courseType?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`education.${index}.major`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Major/Field of Study"
                    placeholder="Computer Science"
                    required
                    {...field}
                    error={errors.education?.[index]?.major?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`education.${index}.gpa`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="GPA"
                    placeholder="3.85"
                    {...field}
                    value={field.value || ''}
                    error={errors.education?.[index]?.gpa?.message}
                    hint="Optional - On a 4.0 scale"
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`education.${index}.location`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Location"
                    placeholder="Stanford, CA"
                    {...field}
                    value={field.value || ''}
                    error={errors.education?.[index]?.location?.message}
                  />
                )}
              />
            </FormField>

            <DateRangeField
              startName={`education.${index}.startDate`}
              endName={`education.${index}.endDate`}
              presentName={`education.${index}.isPresent`}
              presentLabel="Currently enrolled"
            />
          </EntryCard>
        ))}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <GraduationCap className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No education entries yet</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultEducation)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Your First Education
          </Button>
        </div>
      )}
    </FormSection>
  );
}
