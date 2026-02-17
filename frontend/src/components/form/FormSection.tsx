import { forwardRef, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface FormSectionProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  id?: string;
}

export const FormSection = forwardRef<HTMLDivElement, FormSectionProps>(
  ({ title, description, icon: Icon, action, children, className, id }, ref) => {
    return (
      <motion.section
        ref={ref as React.Ref<HTMLElement>}
        id={id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className={cn(
          'bg-white rounded-2xl border border-slate-200',
          'shadow-sm hover:shadow-md transition-shadow duration-300',
          'overflow-hidden',
          className
        )}
      >
        {/* Section Header */}
        <div className="px-6 py-5 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {Icon && (
                <div className="p-2 bg-slate-900 rounded-xl">
                  <Icon className="w-5 h-5 text-white" />
                </div>
              )}
              <div>
                <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
                {description && (
                  <p className="text-sm text-slate-500 mt-0.5">{description}</p>
                )}
              </div>
            </div>
            {action && <div>{action}</div>}
          </div>
        </div>

        {/* Section Content */}
        <div className="p-6">
          {children}
        </div>
      </motion.section>
    );
  }
);

FormSection.displayName = 'FormSection';
