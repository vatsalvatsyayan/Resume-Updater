import { useState, useRef, type KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  hint?: string;
  maxTags?: number;
  className?: string;
}

export function TagInput({
  value,
  onChange,
  placeholder = 'Type and press Enter',
  label,
  error,
  hint,
  maxTags = 20,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Enter' || e.key === ',') && inputValue.trim()) {
      e.preventDefault();
      const tag = inputValue.trim();
      if (!value.includes(tag) && value.length < maxTags) {
        onChange([...value, tag]);
        setInputValue('');
      }
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const addTag = () => {
    const tag = inputValue.trim();
    if (tag && !value.includes(tag) && value.length < maxTags) {
      onChange([...value, tag]);
      setInputValue('');
      inputRef.current?.focus();
    }
  };

  return (
    <div className={cn('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-2">
          {label}
        </label>
      )}
      <div
        className={cn(
          'min-h-[52px] rounded-xl border bg-white p-2',
          'transition-all duration-200',
          'cursor-text',
          isFocused
            ? 'border-slate-400 ring-2 ring-slate-200'
            : 'border-slate-200 hover:border-slate-300',
          error && 'border-red-300'
        )}
        onClick={() => inputRef.current?.focus()}
      >
        <div className="flex flex-wrap gap-2">
          <AnimatePresence mode="popLayout">
            {value.map((tag) => (
              <motion.span
                key={tag}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.15 }}
                className={cn(
                  'inline-flex items-center gap-1.5 px-3 py-1.5',
                  'bg-slate-100 text-slate-700 rounded-lg',
                  'text-sm font-medium',
                  'border border-slate-200'
                )}
              >
                {tag}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeTag(tag);
                  }}
                  className={cn(
                    'p-0.5 rounded-md',
                    'hover:bg-slate-200 transition-colors',
                    'focus:outline-none focus:ring-1 focus:ring-slate-400'
                  )}
                >
                  <X className="w-3 h-3" />
                </button>
              </motion.span>
            ))}
          </AnimatePresence>
          <div className="flex items-center gap-1 flex-1 min-w-[140px]">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={value.length === 0 ? placeholder : 'Add more...'}
              className={cn(
                'flex-1 min-w-0 bg-transparent outline-none',
                'text-sm text-slate-900 placeholder:text-slate-400',
                'py-1.5'
              )}
            />
            {inputValue && (
              <motion.button
                type="button"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={addTag}
                className={cn(
                  'p-1 rounded-md',
                  'bg-slate-900 text-white',
                  'hover:bg-slate-700 transition-colors'
                )}
              >
                <Plus className="w-3.5 h-3.5" />
              </motion.button>
            )}
          </div>
        </div>
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
      {hint && !error && (
        <p className="mt-2 text-xs text-slate-500">{hint}</p>
      )}
      {value.length >= maxTags && (
        <p className="mt-2 text-xs text-amber-600">Maximum {maxTags} tags allowed</p>
      )}
    </div>
  );
}
