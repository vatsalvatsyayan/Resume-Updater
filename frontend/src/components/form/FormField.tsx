import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface FormFieldProps {
  children: ReactNode;
  className?: string;
  fullWidth?: boolean;
}

export function FormField({ children, className, fullWidth = false }: FormFieldProps) {
  return (
    <div className={cn(fullWidth ? 'col-span-full' : '', className)}>
      {children}
    </div>
  );
}
