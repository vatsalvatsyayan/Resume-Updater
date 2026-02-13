import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  GraduationCap,
  Briefcase,
  FolderKanban,
  Wrench,
  Award,
  Heart,
  Crown,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { useUIStore, type SectionId, sections } from '@/stores/uiStore';

const iconMap: Record<string, React.ElementType> = {
  User,
  GraduationCap,
  Briefcase,
  FolderKanban,
  Wrench,
  Award,
  Heart,
  Crown,
};

interface SectionNavProps {
  className?: string;
}

export function SectionNav({ className }: SectionNavProps) {
  const { currentSection, setCurrentSection, completedSections, getProgress } = useUIStore();
  const [isSticky, setIsSticky] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);
  const progress = getProgress();

  useEffect(() => {
    const handleScroll = () => {
      if (navRef.current) {
        const rect = navRef.current.getBoundingClientRect();
        setIsSticky(rect.top <= 64);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: SectionId) => {
    setCurrentSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 140;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div
      ref={navRef}
      className={cn(
        'sticky top-16 z-40 py-4',
        'transition-all duration-300',
        isSticky ? 'bg-white/95 backdrop-blur-lg shadow-sm' : 'bg-transparent',
        className
      )}
    >
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-4 flex items-center gap-3">
          <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-slate-700 to-slate-900 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <span className="text-sm font-semibold text-slate-600 min-w-[3rem] text-right">
            {progress}%
          </span>
        </div>

        {/* Section Pills */}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {sections.map((section) => {
            const Icon = iconMap[section.icon];
            const isActive = currentSection === section.id;
            const isCompleted = completedSections.has(section.id);

            return (
              <motion.button
                key={section.id}
                type="button"
                onClick={() => scrollToSection(section.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  'relative flex items-center gap-2 px-4 py-2 rounded-full',
                  'text-sm font-medium whitespace-nowrap',
                  'transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2',
                  isActive
                    ? 'bg-slate-900 text-white shadow-lg'
                    : isCompleted
                    ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
                )}
              >
                {isCompleted && !isActive ? (
                  <div className="p-0.5 bg-green-500 rounded-full">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                ) : (
                  <Icon className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">{section.label}</span>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
