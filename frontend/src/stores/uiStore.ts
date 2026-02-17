import { create } from 'zustand';

export type SectionId =
  | 'personal'
  | 'education'
  | 'experience'
  | 'projects'
  | 'skills'
  | 'certifications'
  | 'volunteer'
  | 'leadership';

export interface Section {
  id: SectionId;
  label: string;
  icon: string;
}

export const sections: Section[] = [
  { id: 'personal', label: 'Personal', icon: 'User' },
  { id: 'education', label: 'Education', icon: 'GraduationCap' },
  { id: 'experience', label: 'Experience', icon: 'Briefcase' },
  { id: 'projects', label: 'Projects', icon: 'FolderKanban' },
  { id: 'skills', label: 'Skills', icon: 'Wrench' },
  { id: 'certifications', label: 'Certifications', icon: 'Award' },
  { id: 'volunteer', label: 'Volunteer', icon: 'Heart' },
  { id: 'leadership', label: 'Leadership', icon: 'Crown' },
];

interface UIStore {
  currentSection: SectionId;
  setCurrentSection: (section: SectionId) => void;
  isSubmitting: boolean;
  setIsSubmitting: (value: boolean) => void;
  submitError: string | null;
  setSubmitError: (error: string | null) => void;
  showSuccessModal: boolean;
  setShowSuccessModal: (value: boolean) => void;
  completedSections: Set<SectionId>;
  markSectionComplete: (section: SectionId) => void;
  markSectionIncomplete: (section: SectionId) => void;
  getProgress: () => number;
}

export const useUIStore = create<UIStore>((set, get) => ({
  currentSection: 'personal',
  setCurrentSection: (section) => set({ currentSection: section }),

  isSubmitting: false,
  setIsSubmitting: (value) => set({ isSubmitting: value }),

  submitError: null,
  setSubmitError: (error) => set({ submitError: error }),

  showSuccessModal: false,
  setShowSuccessModal: (value) => set({ showSuccessModal: value }),

  completedSections: new Set<SectionId>(),
  markSectionComplete: (section) => {
    const { completedSections } = get();
    const updated = new Set(completedSections);
    updated.add(section);
    set({ completedSections: updated });
  },
  markSectionIncomplete: (section) => {
    const { completedSections } = get();
    const updated = new Set(completedSections);
    updated.delete(section);
    set({ completedSections: updated });
  },

  getProgress: () => {
    const { completedSections } = get();
    return Math.round((completedSections.size / sections.length) * 100);
  },
}));
