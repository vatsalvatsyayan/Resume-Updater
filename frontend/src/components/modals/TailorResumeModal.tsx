import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Sparkles } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalBody,
  ModalFooter,
} from './Modal';

const tailorResumeSchema = z.object({
  companyName: z
    .string()
    .min(1, 'Company name is required')
    .max(100, 'Company name is too long'),
  roleName: z
    .string()
    .min(1, 'Role name is required')
    .max(150, 'Role name is too long'),
  jobDescription: z
    .string()
    .min(50, 'Please provide a more detailed job description (at least 50 characters)')
    .max(10000, 'Job description is too long'),
});

export type TailorResumeFormData = z.infer<typeof tailorResumeSchema>;

interface TailorResumeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TailorResumeFormData) => void;
  isLoading?: boolean;
}

export function TailorResumeModal({
  open,
  onOpenChange,
  onSubmit,
  isLoading = false,
}: TailorResumeModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid },
  } = useForm<TailorResumeFormData>({
    resolver: zodResolver(tailorResumeSchema),
    mode: 'onChange',
    defaultValues: {
      companyName: '',
      roleName: '',
      jobDescription: '',
    },
  });

  const handleFormSubmit = (data: TailorResumeFormData) => {
    onSubmit(data);
    reset();
  };

  const handleClose = () => {
    reset();
    onOpenChange(false);
  };

  return (
    <Modal open={open} onOpenChange={handleClose}>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <ModalHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-amber-100 to-amber-50 rounded-xl">
              <Sparkles className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <ModalTitle>Tailor Your Resume</ModalTitle>
              <ModalDescription>
                Create a perfectly matched resume for this role
              </ModalDescription>
            </div>
          </div>
        </ModalHeader>

        <ModalBody className="space-y-4">
          <Input
            label="Company Name"
            placeholder="e.g., Google, Apple, Netflix"
            error={errors.companyName?.message}
            required
            {...register('companyName')}
          />

          <Input
            label="Role / Position"
            placeholder="e.g., Senior Software Engineer"
            error={errors.roleName?.message}
            required
            {...register('roleName')}
          />

          <Textarea
            label="Job Description"
            placeholder="Paste the full job description here. Include responsibilities, requirements, and qualifications for best results..."
            error={errors.jobDescription?.message}
            required
            className="min-h-[200px]"
            {...register('jobDescription')}
          />
        </ModalBody>

        <ModalFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            disabled={!isValid || isLoading}
            rightIcon={<Sparkles className="w-4 h-4" />}
          >
            Tailor Resume
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
