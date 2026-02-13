# Tailor Resume Modal - Implementation Plan

## Overview

This document outlines the implementation plan for the "Tailor Resume Modal" feature. When users click the **+** button on the Applications page, a beautiful modal will open allowing them to input job details to tailor their resume for a specific position.

---

## Feature Summary

**Trigger**: Click the `+` button in the Header (Applications page only)

**Purpose**: Collect job application details to generate a tailored resume

**Inputs**:
- Company Name (text input)
- Role/Position Name (text input)
- Job Description (large textarea for pasting)

---

## UI/UX Design

### Modal Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ╭─────────────────────────────────────────────────────────╮ │
│  │                                                     [X] │ │
│  │   ✨ Tailor Your Resume                                 │ │
│  │   Create a perfectly matched resume for this role       │ │
│  │                                                         │ │
│  │   ┌─────────────────────────────────────────────────┐   │ │
│  │   │ Company Name                                    │   │ │
│  │   │ ┌─────────────────────────────────────────────┐ │   │ │
│  │   │ │ e.g., Google                                │ │   │ │
│  │   │ └─────────────────────────────────────────────┘ │   │ │
│  │   └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │   ┌─────────────────────────────────────────────────┐   │ │
│  │   │ Role / Position                                 │   │ │
│  │   │ ┌─────────────────────────────────────────────┐ │   │ │
│  │   │ │ e.g., Senior Software Engineer              │ │   │ │
│  │   │ └─────────────────────────────────────────────┘ │   │ │
│  │   └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │   ┌─────────────────────────────────────────────────┐   │ │
│  │   │ Job Description                                 │   │ │
│  │   │ ┌─────────────────────────────────────────────┐ │   │ │
│  │   │ │                                             │ │   │ │
│  │   │ │ Paste the full job description here...      │ │   │ │
│  │   │ │                                             │ │   │ │
│  │   │ │                                             │ │   │ │
│  │   │ │                                             │ │   │ │
│  │   │ └─────────────────────────────────────────────┘ │   │ │
│  │   └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │                    [Cancel]  [Tailor Resume ✨]         │ │
│  │                                                         │ │
│  ╰─────────────────────────────────────────────────────────╯ │
│                        (backdrop blur)                       │
└──────────────────────────────────────────────────────────────┘
```

### Visual Design Specifications

**Backdrop/Overlay**:
- `bg-black/50` with `backdrop-blur-sm` for glassmorphism effect
- Click outside to close (optional)
- Fade-in animation

**Modal Container**:
- `bg-white rounded-2xl` for modern appearance
- `shadow-2xl` for depth
- `max-w-lg w-full mx-4` for responsive width
- `p-6` internal padding
- Scale-up entrance animation (0.95 → 1.0)

**Header Section**:
- Sparkles icon (`✨`) with gradient or amber color
- Title: "Tailor Your Resume" - `text-xl font-bold text-slate-900`
- Subtitle: "Create a perfectly matched resume..." - `text-sm text-slate-500`
- Close button (X) - top-right corner

**Form Fields**:
- Use existing `Input` component for Company Name and Role
- Use existing `Textarea` component for Job Description
- Labels: `text-sm font-medium text-slate-700`
- Placeholders: Helpful examples
- Job Description textarea: `min-h-[200px]` for comfortable pasting

**Buttons**:
- Cancel: `variant="outline"` - secondary action
- Submit: `variant="primary"` - "Tailor Resume ✨"
- Both buttons: right-aligned, `gap-3` spacing

**Animation (Framer Motion)**:
```tsx
// Backdrop
initial={{ opacity: 0 }}
animate={{ opacity: 1 }}
exit={{ opacity: 0 }}

// Modal
initial={{ opacity: 0, scale: 0.95, y: 20 }}
animate={{ opacity: 1, scale: 1, y: 0 }}
exit={{ opacity: 0, scale: 0.95, y: 20 }}
transition={{ duration: 0.2, ease: "easeOut" }}
```

---

## Component Architecture

### New Files to Create

```
frontend/src/
├── components/
│   ├── modals/
│   │   ├── index.ts                    # Barrel export
│   │   ├── Modal.tsx                   # Reusable base modal component
│   │   └── TailorResumeModal.tsx       # Specific modal for tailoring
```

### Component Hierarchy

```
ApplicationsPage
└── TailorResumeModal (conditionally rendered)
    ├── Modal (base wrapper)
    │   ├── Backdrop (overlay)
    │   └── ModalContent
    │       ├── ModalHeader
    │       │   ├── Icon + Title
    │       │   ├── Description
    │       │   └── CloseButton
    │       ├── ModalBody
    │       │   ├── Input (Company Name)
    │       │   ├── Input (Role)
    │       │   └── Textarea (Job Description)
    │       └── ModalFooter
    │           ├── Button (Cancel)
    │           └── Button (Submit)
```

---

## Component Specifications

### 1. Modal.tsx (Base Component)

A reusable modal wrapper using Radix UI Dialog primitives.

```tsx
interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}
```

**Features**:
- Uses `@radix-ui/react-dialog` (already installed)
- Handles accessibility (focus trap, aria attributes)
- Provides overlay with backdrop blur
- Supports escape key to close
- Smooth enter/exit animations via Framer Motion

### 2. TailorResumeModal.tsx

The specific implementation for the tailor resume use case.

```tsx
interface TailorResumeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TailorResumeFormData) => void;
}

interface TailorResumeFormData {
  companyName: string;
  roleName: string;
  jobDescription: string;
}
```

**Features**:
- Form validation using React Hook Form + Zod
- All fields required
- Loading state during submission
- Error handling with toast notifications
- Clears form on successful submission

### 3. Form Validation Schema

```tsx
const tailorResumeSchema = z.object({
  companyName: z.string()
    .min(1, 'Company name is required')
    .max(100, 'Company name is too long'),
  roleName: z.string()
    .min(1, 'Role name is required')
    .max(150, 'Role name is too long'),
  jobDescription: z.string()
    .min(50, 'Please provide a more detailed job description')
    .max(10000, 'Job description is too long'),
});
```

---

## Files to Modify

### 1. Header.tsx

**Changes**:
- Accept `onAddClick` prop for the + button
- Call the handler when + button is clicked

```tsx
interface HeaderProps {
  className?: string;
  onAddClick?: () => void;  // NEW
}

// In the button:
<button
  className="p-2 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors"
  onClick={onAddClick}  // CHANGED
>
  <Plus className="w-5 h-5" />
</button>
```

### 2. ApplicationsPage.tsx

**Changes**:
- Import TailorResumeModal
- Add state for modal open/close
- Pass handler to Header
- Handle form submission

```tsx
const [isModalOpen, setIsModalOpen] = useState(false);

const handleTailorSubmit = (data: TailorResumeFormData) => {
  // TODO: Send to API
  console.log('Tailoring resume for:', data);
  setIsModalOpen(false);
  toast.success('Resume tailoring started!');
};

return (
  <>
    <Header onAddClick={() => setIsModalOpen(true)} />
    {/* ... existing content ... */}
    <TailorResumeModal
      open={isModalOpen}
      onOpenChange={setIsModalOpen}
      onSubmit={handleTailorSubmit}
    />
  </>
);
```

---

## Implementation Steps

### Phase 1: Create Base Modal Component

1. Create `/components/modals/` directory
2. Implement `Modal.tsx` using Radix UI Dialog
3. Add Framer Motion animations
4. Style with existing design tokens
5. Export from `index.ts`

### Phase 2: Create TailorResumeModal

1. Create `TailorResumeModal.tsx`
2. Implement form with React Hook Form + Zod
3. Use existing Input and Textarea components
4. Add loading/disabled states
5. Connect to Button components

### Phase 3: Wire Up to ApplicationsPage

1. Update `Header.tsx` to accept `onAddClick` prop
2. Update `ApplicationsPage.tsx` with modal state
3. Pass callback to Header
4. Render modal conditionally
5. Handle form submission (placeholder for now)

### Phase 4: Polish & Testing

1. Test keyboard navigation (Tab, Escape)
2. Test screen reader accessibility
3. Test responsive behavior (mobile view)
4. Test form validation errors
5. Test animations on open/close

---

## Design Token Reference

| Element | Classes |
|---------|---------|
| Overlay | `fixed inset-0 bg-black/50 backdrop-blur-sm` |
| Modal | `bg-white rounded-2xl shadow-2xl max-w-lg w-full` |
| Header Icon | `text-amber-500` or `text-primary-500` |
| Title | `text-xl font-bold text-slate-900` |
| Subtitle | `text-sm text-slate-500` |
| Labels | `text-sm font-medium text-slate-700` |
| Inputs | Use existing Input component |
| Textarea | Use existing Textarea component |
| Cancel Button | `variant="outline"` |
| Submit Button | `variant="primary"` |
| Spacing | `space-y-4` for form fields, `p-6` for container |

---

## Future Enhancements

1. **Auto-extract from URL**: Paste job listing URL and auto-fill fields
2. **Save as Draft**: Allow saving incomplete entries
3. **Template Selection**: Choose resume template before tailoring
4. **Preview**: Show side-by-side preview of original vs tailored resume
5. **History**: Show previously used job descriptions

---

## Acceptance Criteria

- [ ] Clicking + button opens modal with smooth animation
- [ ] Modal has Company Name, Role, and Job Description fields
- [ ] All fields are required with validation messages
- [ ] Cancel button closes modal without saving
- [ ] Submit button is disabled while form is invalid
- [ ] Clicking outside modal closes it
- [ ] Escape key closes modal
- [ ] Modal is fully accessible (screen reader friendly)
- [ ] Modal is responsive (works on mobile)
- [ ] Design matches existing theme (colors, fonts, spacing)
