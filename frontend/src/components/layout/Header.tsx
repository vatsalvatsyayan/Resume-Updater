import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Sparkles } from 'lucide-react';
import { cn } from '@/lib/cn';

interface HeaderProps {
  variant?: 'default' | 'minimal';
  className?: string;
}

export function Header({ variant = 'default', className }: HeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'sticky top-0 z-50',
        'backdrop-blur-xl bg-white/80 border-b border-slate-200/50',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-amber-400 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative p-2 bg-slate-900 rounded-xl">
                <FileText className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold text-slate-900 tracking-tight">
                ResumeFlow
              </span>
              {variant === 'default' && (
                <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">
                  Career Builder
                </span>
              )}
            </div>
          </Link>

          {/* Actions */}
          {variant === 'default' && (
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-full">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span className="text-xs font-medium text-amber-700">AI-Powered</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.header>
  );
}
