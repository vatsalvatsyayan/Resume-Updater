import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export type GenerationPhase = 'resume' | 'cover' | 'saving';

/** Rotate while generation runs — mix of light research-backed tips and affirmations */
const TIPS_AND_AFFIRMATIONS: string[] = [
  'Did you know? Research on tailored résumés often finds stronger interview outcomes than generic applications—some studies associate customization with dramatically higher callback or interview rates (roughly 30% to over 100% in certain samples).',
  "You're doing great. Each tailored application sharpens how you tell your story.",
  'Job searching can be exhausting—be easy on yourself. Small steps still move you forward.',
  "You're investing in clarity: hiring teams often skim résumés quickly, and alignment with the role helps you stand out.",
  'Tailoring keywords and proof of impact to the posting is not fluff—it respects the reader’s time.',
  'Take breaks and hydrate. The right opportunity is often a marathon, not a sprint.',
  'Rejections reroute you; they do not define your worth or your ceiling.',
  'Progress beats perfection. Showing up consistently is already a skill.',
];

const TIP_ROTATION_MS = 8000;

function phaseHeading(phase: GenerationPhase | null): string {
  switch (phase) {
    case 'resume':
      return 'Tailoring your résumé';
    case 'cover':
      return 'Writing your cover letter';
    case 'saving':
      return 'Saving your application';
    default:
      return 'Working on it…';
  }
}

function phaseDescription(phase: GenerationPhase | null): string | null {
  switch (phase) {
    case 'resume':
      return 'Analyzing the job description and aligning your experience.';
    case 'cover':
      return 'Drafting your letter—this may take a few minutes when research runs in the background.';
    case 'saving':
      return 'Almost there—storing your tailored materials.';
    default:
      return null;
  }
}

export function GenerationProgressOverlay({
  open,
  phase,
}: {
  open: boolean;
  phase: GenerationPhase | null;
}) {
  const [tipIndex, setTipIndex] = useState(0);

  useEffect(() => {
    if (!open) return;
    setTipIndex(0);
    const id = window.setInterval(() => {
      setTipIndex((i) => (i + 1) % TIPS_AND_AFFIRMATIONS.length);
    }, TIP_ROTATION_MS);
    return () => clearInterval(id);
  }, [open]);

  const sub = useMemo(() => phaseDescription(phase), [phase]);

  if (!open || typeof document === 'undefined') {
    return null;
  }

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4 backdrop-blur-[2px]"
      role="alertdialog"
      aria-busy="true"
      aria-live="polite"
      aria-label="Resume and cover letter generation in progress"
    >
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="w-full max-w-md rounded-2xl border border-slate-100 bg-white p-8 shadow-2xl"
      >
        <div className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900">
          <Sparkles className="h-5 w-5 shrink-0 text-amber-500" aria-hidden />
          {phaseHeading(phase)}
        </div>
        {sub ? (
          <p className="mb-5 text-sm text-slate-500">{sub}</p>
        ) : (
          <div className="mb-5" />
        )}

        <div className="relative mb-6 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
          <div
            className="animate-progress-indeterminate absolute inset-y-0 w-[42%] rounded-full bg-gradient-to-r from-slate-500 via-slate-800 to-slate-500"
            aria-hidden
          />
        </div>

        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          While you wait
        </p>
        <div className="min-h-[5.5rem]">
          <AnimatePresence mode="wait">
            <motion.p
              key={tipIndex}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.35 }}
              className="text-sm leading-relaxed text-slate-600"
            >
              {TIPS_AND_AFFIRMATIONS[tipIndex]}
            </motion.p>
          </AnimatePresence>
        </div>
      </motion.div>
    </div>,
    document.body
  );
}
