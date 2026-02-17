import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Trash2, GripVertical } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui';

export interface EntryCardProps {
  title: string;
  subtitle?: string;
  index: number;
  onRemove: () => void;
  canRemove?: boolean;
  children: ReactNode;
  className?: string;
}

export function EntryCard({
  title,
  subtitle,
  index,
  onRemove,
  canRemove = true,
  children,
  className,
}: EntryCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.98 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={cn(
        'relative bg-slate-50 rounded-xl border border-slate-200',
        'p-5 mb-4 last:mb-0',
        'hover:border-slate-300 transition-all duration-200',
        'group',
        className
      )}
    >
      {/* Entry Header */}
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-slate-400 cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100 transition-opacity">
            <GripVertical className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-3">
            <span className="w-7 h-7 rounded-lg bg-slate-900 text-white text-xs font-semibold flex items-center justify-center">
              {index + 1}
            </span>
            <div>
              <h4 className="text-sm font-semibold text-slate-700">{title}</h4>
              {subtitle && (
                <p className="text-xs text-slate-500">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
        {canRemove && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onRemove}
            className="text-slate-400 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
          >
            <Trash2 className="w-4 h-4" />
            <span className="sr-only">Remove</span>
          </Button>
        )}
      </div>

      {/* Entry Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {children}
      </div>
    </motion.div>
  );
}
