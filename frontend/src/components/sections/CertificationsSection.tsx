import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { Award, Plus, ExternalLink } from 'lucide-react';
import { Input, Checkbox, Button } from '@/components/ui';
import { FormSection, EntryCard, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultCertification } from '@/types/form.types';

export function CertificationsSection() {
  const { control, formState: { errors }, watch } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'certifications',
  });

  return (
    <FormSection
      id="certifications"
      title="Certifications"
      description="Professional credentials"
      icon={Award}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultCertification)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Certification
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => {
          const hasNoExpiry = watch(`certifications.${index}.hasNoExpiry`);

          return (
            <EntryCard
              key={field.id}
              title="Certification"
              subtitle={`Credential ${index + 1}`}
              index={index}
              onRemove={() => remove(index)}
            >
              <FormField>
                <Controller
                  name={`certifications.${index}.name`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      label="Certification Name"
                      placeholder="AWS Solutions Architect"
                      required
                      {...field}
                      error={errors.certifications?.[index]?.name?.message}
                    />
                  )}
                />
              </FormField>

              <FormField>
                <Controller
                  name={`certifications.${index}.issuingOrganization`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      label="Issuing Organization"
                      placeholder="Amazon Web Services"
                      required
                      {...field}
                      error={errors.certifications?.[index]?.issuingOrganization?.message}
                    />
                  )}
                />
              </FormField>

              <FormField>
                <Controller
                  name={`certifications.${index}.issueDate`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      type="date"
                      label="Issue Date"
                      {...field}
                      value={field.value || ''}
                      error={errors.certifications?.[index]?.issueDate?.message}
                    />
                  )}
                />
              </FormField>

              <FormField>
                <div className="space-y-2">
                  <Controller
                    name={`certifications.${index}.expiryDate`}
                    control={control}
                    render={({ field }) => (
                      <Input
                        type="date"
                        label="Expiry Date"
                        {...field}
                        value={field.value || ''}
                        disabled={hasNoExpiry}
                        error={errors.certifications?.[index]?.expiryDate?.message}
                        className={hasNoExpiry ? 'opacity-50' : ''}
                      />
                    )}
                  />
                  <Controller
                    name={`certifications.${index}.hasNoExpiry`}
                    control={control}
                    render={({ field }) => (
                      <Checkbox
                        label="No expiry date"
                        checked={field.value}
                        onChange={field.onChange}
                      />
                    )}
                  />
                </div>
              </FormField>

              <FormField>
                <Controller
                  name={`certifications.${index}.credentialId`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      label="Credential ID"
                      placeholder="ABC123"
                      {...field}
                      value={field.value || ''}
                      error={errors.certifications?.[index]?.credentialId?.message}
                    />
                  )}
                />
              </FormField>

              <FormField>
                <Controller
                  name={`certifications.${index}.credentialUrl`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      type="url"
                      label="Credential URL"
                      placeholder="https://verify.example.com/abc123"
                      {...field}
                      value={field.value || ''}
                      error={errors.certifications?.[index]?.credentialUrl?.message}
                      rightAddon={<ExternalLink className="w-4 h-4" />}
                    />
                  )}
                />
              </FormField>
            </EntryCard>
          );
        })}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <Award className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No certifications yet</p>
          <p className="text-sm text-slate-400 mt-1">Add professional certifications to stand out</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultCertification)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Certification
          </Button>
        </div>
      )}
    </FormSection>
  );
}
