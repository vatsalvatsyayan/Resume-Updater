import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { Crown, Plus } from 'lucide-react';
import { Input, Textarea, Button } from '@/components/ui';
import { FormSection, EntryCard, DateRangeField, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultLeadership } from '@/types/form.types';

export function LeadershipSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'leadership',
  });

  return (
    <FormSection
      id="leadership"
      title="Leadership Experience"
      description="Your leadership roles"
      icon={Crown}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultLeadership)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Leadership
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => (
          <EntryCard
            key={field.id}
            title="Leadership Role"
            subtitle={`Entry ${index + 1}`}
            index={index}
            onRemove={() => remove(index)}
          >
            <FormField>
              <Controller
                name={`leadership.${index}.title`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Title/Position"
                    placeholder="President"
                    required
                    {...field}
                    error={errors.leadership?.[index]?.title?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`leadership.${index}.organization`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Organization"
                    placeholder="CS Club"
                    required
                    {...field}
                    error={errors.leadership?.[index]?.organization?.message}
                  />
                )}
              />
            </FormField>

            <DateRangeField
              startName={`leadership.${index}.startDate`}
              endName={`leadership.${index}.endDate`}
              presentName={`leadership.${index}.isPresent`}
              presentLabel="Current position"
            />

            <FormField className="md:col-span-2">
              <Controller
                name={`leadership.${index}.description`}
                control={control}
                render={({ field }) => (
                  <Textarea
                    label="Description"
                    placeholder="Describe your leadership responsibilities and achievements..."
                    {...field}
                    value={field.value || ''}
                    error={errors.leadership?.[index]?.description?.message}
                  />
                )}
              />
            </FormField>
          </EntryCard>
        ))}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <Crown className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No leadership experience yet</p>
          <p className="text-sm text-slate-400 mt-1">Add leadership roles from clubs, teams, or organizations</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultLeadership)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Leadership Role
          </Button>
        </div>
      )}
    </FormSection>
  );
}
