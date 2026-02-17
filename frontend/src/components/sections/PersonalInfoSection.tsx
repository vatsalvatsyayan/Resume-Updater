import { useFormContext, Controller } from 'react-hook-form';
import { User, Mail, Globe, Github, Linkedin } from 'lucide-react';
import { Input } from '@/components/ui';
import { FormSection, FormField } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';

export function PersonalInfoSection() {
  const { control, formState: { errors } } = useFormContext<ProfileFormData>();

  return (
    <FormSection
      id="personal"
      title="Personal Information"
      description="Your basic contact details"
      icon={User}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField fullWidth>
          <Controller
            name="personalInfo.name"
            control={control}
            render={({ field }) => (
              <Input
                label="Full Name"
                placeholder="John Doe"
                required
                {...field}
                error={errors.personalInfo?.name?.message}
                leftAddon={<User className="w-4 h-4" />}
              />
            )}
          />
        </FormField>

        <FormField fullWidth>
          <Controller
            name="personalInfo.email"
            control={control}
            render={({ field }) => (
              <Input
                type="email"
                label="Email Address"
                placeholder="john@example.com"
                required
                {...field}
                error={errors.personalInfo?.email?.message}
                leftAddon={<Mail className="w-4 h-4" />}
              />
            )}
          />
        </FormField>

        <FormField>
          <Controller
            name="personalInfo.portfolioWebsite"
            control={control}
            render={({ field }) => (
              <Input
                type="url"
                label="Portfolio Website"
                placeholder="https://yourportfolio.com"
                {...field}
                value={field.value || ''}
                error={errors.personalInfo?.portfolioWebsite?.message}
                leftAddon={<Globe className="w-4 h-4" />}
              />
            )}
          />
        </FormField>

        <FormField>
          <Controller
            name="personalInfo.githubUrl"
            control={control}
            render={({ field }) => (
              <Input
                type="url"
                label="GitHub Profile"
                placeholder="https://github.com/username"
                {...field}
                value={field.value || ''}
                error={errors.personalInfo?.githubUrl?.message}
                leftAddon={<Github className="w-4 h-4" />}
              />
            )}
          />
        </FormField>

        <FormField className="md:col-span-2">
          <Controller
            name="personalInfo.linkedinUrl"
            control={control}
            render={({ field }) => (
              <Input
                type="url"
                label="LinkedIn Profile"
                placeholder="https://linkedin.com/in/username"
                {...field}
                value={field.value || ''}
                error={errors.personalInfo?.linkedinUrl?.message}
                leftAddon={<Linkedin className="w-4 h-4" />}
              />
            )}
          />
        </FormField>
      </div>
    </FormSection>
  );
}
