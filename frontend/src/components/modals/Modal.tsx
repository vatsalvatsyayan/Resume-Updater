import * as Dialog from '@radix-ui/react-dialog';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';

interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

interface ModalHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface ModalTitleProps {
  children: React.ReactNode;
  className?: string;
}

interface ModalDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

interface ModalBodyProps {
  children: React.ReactNode;
  className?: string;
}

interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function Modal({ open, onOpenChange, children, className }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
              />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className={cn(
                  'fixed inset-0 z-50 flex items-center justify-center p-4',
                  'focus:outline-none'
                )}
              >
                <div
                  className={cn(
                    'w-full max-w-lg',
                    'bg-white rounded-2xl shadow-2xl',
                    className
                  )}
                >
                  {children}
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}

export function ModalHeader({ children, className }: ModalHeaderProps) {
  return (
    <div className={cn('relative px-6 pt-6 pb-4', className)}>
      {children}
      <Dialog.Close asChild>
        <button
          className={cn(
            'absolute right-4 top-4 p-2 rounded-xl',
            'text-slate-400 hover:text-slate-600 hover:bg-slate-100',
            'transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400'
          )}
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>
      </Dialog.Close>
    </div>
  );
}

export function ModalTitle({ children, className }: ModalTitleProps) {
  return (
    <Dialog.Title
      className={cn('text-xl font-bold text-slate-900', className)}
    >
      {children}
    </Dialog.Title>
  );
}

export function ModalDescription({ children, className }: ModalDescriptionProps) {
  return (
    <Dialog.Description
      className={cn('text-sm text-slate-500 mt-1', className)}
    >
      {children}
    </Dialog.Description>
  );
}

export function ModalBody({ children, className }: ModalBodyProps) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  );
}

export function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-end gap-3 px-6 pb-6 pt-2',
        className
      )}
    >
      {children}
    </div>
  );
}
