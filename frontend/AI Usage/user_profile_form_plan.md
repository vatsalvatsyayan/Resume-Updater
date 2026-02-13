# User Profile Form - Implementation Plan

Author: Vatsal Vatsyayan

## AI Usage Documentation

This document records the AI-assisted development plan for the User Profile Form feature in the Resume Updater application.

---

## Overview

Convert existing vanilla HTML/CSS/JS frontend to a modern React + Tailwind CSS application for the resume tailoring app. This form serves dual purposes:
1. User signup/registration
2. Profile editing for existing users

## Tech Stack Selected

| Category | Technology | Rationale |
|----------|------------|-----------|
| Framework | React 18 + TypeScript | Type safety, component reusability |
| Build Tool | Vite | Fast HMR, optimized builds |
| Styling | Tailwind CSS | Utility-first, rapid development |
| Form Management | React Hook Form + Zod | Performant forms with schema validation |
| State Management | Zustand | Lightweight, simple API |
| Animations | Framer Motion | Smooth, declarative animations |
| Icons | Lucide React | Modern, consistent icon set |
| Notifications | Sonner | Toast notifications |
| Accessibility | Radix UI | Accessible component primitives |

## Data Structure

The form collects and sends the following JSON structure to the backend:

```json
{
  "personalInfo": {
    "name": "string",
    "email": "string",
    "portfolioWebsite": "string | null",
    "githubUrl": "string | null",
    "linkedinUrl": "string | null"
  },
  "education": [{
    "universityName": "string",
    "courseName": "string",
    "courseType": "Bachelor's | Master's | PhD | Diploma | Certificate | Associate",
    "major": "string",
    "gpa": "string | null",
    "location": "string | null",
    "startDate": "string | null",
    "endDate": "string | null",
    "isPresent": "boolean"
  }],
  "workExperience": [{
    "companyName": "string",
    "position": "string",
    "location": "string | null",
    "startDate": "string | null",
    "endDate": "string | null",
    "isPresent": "boolean",
    "summary": "string | null",
    "description": "string | null"
  }],
  "projects": [{
    "projectName": "string",
    "link": "string | null",
    "techStack": "string[]",
    "summary": "string | null",
    "description": "string | null"
  }],
  "skills": {
    "programmingLanguages": "string[]",
    "frameworks": "string[]",
    "databases": "string[]",
    "toolsAndTechnologies": "string[]",
    "cloud": "string[]",
    "ai": "string[]",
    "other": "string[]"
  },
  "certifications": [{
    "name": "string",
    "issuingOrganization": "string",
    "issueDate": "string | null",
    "expiryDate": "string | null",
    "hasNoExpiry": "boolean",
    "credentialId": "string | null",
    "credentialUrl": "string | null"
  }],
  "volunteer": [{
    "organizationName": "string",
    "role": "string",
    "cause": "string | null",
    "location": "string | null",
    "startDate": "string | null",
    "endDate": "string | null",
    "isPresent": "boolean",
    "description": "string | null"
  }],
  "leadership": [{
    "title": "string",
    "organization": "string",
    "startDate": "string | null",
    "endDate": "string | null",
    "isPresent": "boolean",
    "description": "string | null"
  }]
}
```

## Project Structure

```
frontend/
├── AI Usage/
│   └── user_profile_form_plan.md    # This document
├── src/
│   ├── components/
│   │   ├── ui/                      # Reusable UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── TagInput.tsx
│   │   │   ├── Card.tsx
│   │   │   └── index.ts
│   │   ├── form/                    # Form-specific components
│   │   │   ├── FormField.tsx
│   │   │   ├── FormSection.tsx
│   │   │   ├── EntryCard.tsx
│   │   │   ├── DateRangeField.tsx
│   │   │   └── index.ts
│   │   ├── sections/                # Form section components
│   │   │   ├── PersonalInfoSection.tsx
│   │   │   ├── EducationSection.tsx
│   │   │   ├── WorkExperienceSection.tsx
│   │   │   ├── ProjectsSection.tsx
│   │   │   ├── SkillsSection.tsx
│   │   │   ├── CertificationsSection.tsx
│   │   │   ├── VolunteerSection.tsx
│   │   │   ├── LeadershipSection.tsx
│   │   │   └── index.ts
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── SectionNav.tsx
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── ProfileFormPage.tsx
│   │   └── SuccessPage.tsx
│   ├── hooks/
│   │   └── useFormPersistence.ts
│   ├── stores/
│   │   ├── formStore.ts
│   │   └── uiStore.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── validation.ts
│   │   ├── utils.ts
│   │   └── cn.ts
│   ├── types/
│   │   └── form.types.ts
│   └── config/
│       └── constants.ts
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

## Implementation Phases

### Phase 1: Project Setup ✓
- [x] Initialize Vite + React + TypeScript
- [x] Install all dependencies
- [x] Configure Tailwind CSS with custom theme
- [x] Set up path aliases
- [x] Create folder structure
- [x] Create AI Usage documentation

### Phase 2: UI Components
- [ ] Build utility function (cn.ts)
- [ ] Build Button component
- [ ] Build Input component
- [ ] Build Textarea component
- [ ] Build Select component
- [ ] Build Checkbox component
- [ ] Build TagInput component
- [ ] Build Card component

### Phase 3: Form Components & Types
- [ ] Define TypeScript interfaces
- [ ] Create Zod validation schemas
- [ ] Build FormField component
- [ ] Build FormSection component
- [ ] Build EntryCard component
- [ ] Build DateRangeField component

### Phase 4: Section Components
- [ ] PersonalInfoSection
- [ ] EducationSection
- [ ] WorkExperienceSection
- [ ] ProjectsSection
- [ ] SkillsSection
- [ ] CertificationsSection
- [ ] VolunteerSection
- [ ] LeadershipSection

### Phase 5: Pages & Integration
- [ ] Create Zustand stores
- [ ] Build LandingPage
- [ ] Build ProfileFormPage
- [ ] Build SuccessPage
- [ ] Set up React Router
- [ ] Integrate with backend API

### Phase 6: Polish
- [ ] Add loading states
- [ ] Add error handling
- [ ] Implement draft auto-save
- [ ] Add animations
- [ ] Test responsiveness
- [ ] Accessibility testing

## Design Decisions

### UI/UX Approach
- **Layout**: Single-page form with sticky section navigation
- **Navigation**: Horizontal pill buttons for quick section jumps
- **Progress**: Visual progress indicator showing completion percentage
- **Colors**: Professional indigo primary (#6366f1), slate neutrals
- **Typography**: Inter font family for clean, modern look

### Form Management
- React Hook Form for performant, uncontrolled form state
- Zod for TypeScript-first schema validation
- Field arrays for dynamic add/remove entries

### State Management
- Form state: React Hook Form (local)
- Draft persistence: Zustand + localStorage
- UI state: Zustand (modals, loading, current section)

## API Integration

Backend endpoint: `POST http://127.0.0.1:8000/user/registration`

```typescript
async function submitRegistration(data: ProfileFormData): Promise<ApiResponse> {
  const response = await fetch('http://127.0.0.1:8000/user/registration', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Registration failed');
  }

  return response.json();
}
```

## Verification Checklist

- [ ] All form fields work correctly
- [ ] Validation errors display properly
- [ ] Add/remove entries function smoothly
- [ ] Skills tag input works
- [ ] Form submission successful
- [ ] Draft save/restore works
- [ ] Responsive on all screen sizes
- [ ] Keyboard navigation functional
- [ ] Screen reader compatible

---

*Generated with AI assistance using Claude Code*
