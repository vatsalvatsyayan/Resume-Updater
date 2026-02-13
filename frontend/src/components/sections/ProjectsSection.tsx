import { useFormContext, useFieldArray, Controller } from 'react-hook-form';
import { AnimatePresence } from 'framer-motion';
import { FolderKanban, Plus, ExternalLink } from 'lucide-react';
import { Input, Textarea, Button, TagInput } from '@/components/ui';
import { FormSection, EntryCard, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { defaultProject } from '@/types/form.types';

export function ProjectsSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'projects',
  });

  return (
    <FormSection
      id="projects"
      title="Projects"
      description="Showcase your work"
      icon={FolderKanban}
      action={
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append(defaultProject)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Project
        </Button>
      }
    >
      <AnimatePresence mode="popLayout">
        {fields.map((field, index) => (
          <EntryCard
            key={field.id}
            title="Project"
            subtitle={`Project ${index + 1}`}
            index={index}
            onRemove={() => remove(index)}
            canRemove={fields.length > 1}
          >
            <FormField>
              <Controller
                name={`projects.${index}.projectName`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Project Name"
                    placeholder="E-commerce Platform"
                    required
                    {...field}
                    error={errors.projects?.[index]?.projectName?.message}
                  />
                )}
              />
            </FormField>

            <FormField>
              <Controller
                name={`projects.${index}.link`}
                control={control}
                render={({ field }) => (
                  <Input
                    type="url"
                    label="Project Link"
                    placeholder="https://github.com/username/project"
                    {...field}
                    value={field.value || ''}
                    error={errors.projects?.[index]?.link?.message}
                    rightAddon={<ExternalLink className="w-4 h-4" />}
                  />
                )}
              />
            </FormField>

            <FormField className="md:col-span-2">
              <Controller
                name={`projects.${index}.techStack`}
                control={control}
                render={({ field }) => (
                  <TagInput
                    label="Tech Stack"
                    placeholder="React, Node.js, PostgreSQL..."
                    value={field.value || []}
                    onChange={field.onChange}
                    hint="Press Enter or comma to add technologies"
                  />
                )}
              />
            </FormField>

            <FormField className="md:col-span-2">
              <Controller
                name={`projects.${index}.summary`}
                control={control}
                render={({ field }) => (
                  <Input
                    label="Summary"
                    placeholder="Brief one-line description"
                    {...field}
                    value={field.value || ''}
                    error={errors.projects?.[index]?.summary?.message}
                  />
                )}
              />
            </FormField>

            <FormField className="md:col-span-2">
              <Controller
                name={`projects.${index}.description`}
                control={control}
                render={({ field }) => (
                  <Textarea
                    label="Description"
                    placeholder="Describe the project, your role, key features, and outcomes..."
                    {...field}
                    value={field.value || ''}
                    error={errors.projects?.[index]?.description?.message}
                  />
                )}
              />
            </FormField>
          </EntryCard>
        ))}
      </AnimatePresence>

      {fields.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          <FolderKanban className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No projects yet</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => append(defaultProject)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Your First Project
          </Button>
        </div>
      )}
    </FormSection>
  );
}
