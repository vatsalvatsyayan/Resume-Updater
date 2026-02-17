import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ProfileFormData } from '@/types/form.types';
import { defaultProfileFormData } from '@/types/form.types';

interface FormStore {
  draft: ProfileFormData | null;
  lastSaved: Date | null;
  saveDraft: (data: ProfileFormData) => void;
  loadDraft: () => ProfileFormData | null;
  clearDraft: () => void;
  hasDraft: () => boolean;
}

export const useFormStore = create<FormStore>()(
  persist(
    (set, get) => ({
      draft: null,
      lastSaved: null,

      saveDraft: (data: ProfileFormData) => {
        set({ draft: data, lastSaved: new Date() });
      },

      loadDraft: () => {
        const { draft } = get();
        return draft || defaultProfileFormData;
      },

      clearDraft: () => {
        set({ draft: null, lastSaved: null });
      },

      hasDraft: () => {
        return get().draft !== null;
      },
    }),
    {
      name: 'resume-form-draft',
      partialize: (state) => ({ draft: state.draft, lastSaved: state.lastSaved }),
    }
  )
);
