import { useFormContext, Controller } from 'react-hook-form';
import { Wrench, Code2, Layers, Database, Cloud, Cpu, MoreHorizontal } from 'lucide-react';
import { TagInput } from '@/components/ui';
import { FormSection } from '@/components/form';
import type { ProfileFormData } from '@/types/form.types';
import { cn } from '@/lib/cn';

interface SkillCategoryProps {
  name: keyof ProfileFormData['skills'];
  label: string;
  icon: React.ReactNode;
  placeholder: string;
  hint?: string;
}

const skillCategories: SkillCategoryProps[] = [
  {
    name: 'programmingLanguages',
    label: 'Programming Languages',
    icon: <Code2 className="w-4 h-4" />,
    placeholder: 'Python, JavaScript, Go...',
    hint: 'Languages you write code in',
  },
  {
    name: 'frameworks',
    label: 'Frameworks & Libraries',
    icon: <Layers className="w-4 h-4" />,
    placeholder: 'React, Django, FastAPI...',
    hint: 'Frameworks you use for development',
  },
  {
    name: 'databases',
    label: 'Databases',
    icon: <Database className="w-4 h-4" />,
    placeholder: 'PostgreSQL, MongoDB, Redis...',
    hint: 'Database systems you work with',
  },
  {
    name: 'toolsAndTechnologies',
    label: 'Tools & Technologies',
    icon: <Wrench className="w-4 h-4" />,
    placeholder: 'Git, Docker, Kubernetes...',
    hint: 'Development tools and platforms',
  },
  {
    name: 'cloud',
    label: 'Cloud Platforms',
    icon: <Cloud className="w-4 h-4" />,
    placeholder: 'AWS, GCP, Azure...',
    hint: 'Cloud services you have experience with',
  },
  {
    name: 'ai',
    label: 'AI / Machine Learning',
    icon: <Cpu className="w-4 h-4" />,
    placeholder: 'TensorFlow, PyTorch, OpenAI...',
    hint: 'AI/ML frameworks and tools',
  },
  {
    name: 'other',
    label: 'Other Skills',
    icon: <MoreHorizontal className="w-4 h-4" />,
    placeholder: 'Agile, Scrum, Communication...',
    hint: 'Soft skills and other competencies',
  },
];

function SkillCategory({ name, label, icon, placeholder, hint }: SkillCategoryProps) {
  const { control } = useFormContext<ProfileFormData>();

  return (
    <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-slate-900 rounded-lg text-white">
          {icon}
        </div>
        <span className="text-sm font-semibold text-slate-700">{label}</span>
      </div>
      <Controller
        name={`skills.${name}`}
        control={control}
        render={({ field }) => (
          <TagInput
            value={field.value || []}
            onChange={field.onChange}
            placeholder={placeholder}
            hint={hint}
          />
        )}
      />
    </div>
  );
}

export function SkillsSection() {
  const { watch } = useFormContext<ProfileFormData>();
  const skills = watch('skills');

  const totalSkills = Object.values(skills || {}).reduce(
    (acc, arr) => acc + (Array.isArray(arr) ? arr.length : 0),
    0
  );

  return (
    <FormSection
      id="skills"
      title="Skills"
      description="Your technical expertise"
      icon={Wrench}
      action={
        <div className={cn(
          'px-3 py-1.5 rounded-full text-sm font-medium',
          totalSkills > 0
            ? 'bg-slate-900 text-white'
            : 'bg-slate-100 text-slate-500'
        )}>
          {totalSkills} skill{totalSkills !== 1 ? 's' : ''} added
        </div>
      }
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {skillCategories.map((category) => (
          <SkillCategory key={category.name} {...category} />
        ))}
      </div>

      <p className="text-xs text-slate-500 mt-4 text-center">
        Press Enter or comma after each skill to add it
      </p>
    </FormSection>
  );
}
