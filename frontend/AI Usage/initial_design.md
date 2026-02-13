# ResuYOU - Initial Design Document

Author: Vatsal Vatsyayan

## Overview

This document outlines the redesign plan for transforming the current "ResumeFlow" application into "ResuYOU" based on the provided wireframe diagram. The redesign introduces a tabbed navigation system, an applications management feature, and resume preview/PDF generation capabilities.

---

## Diagram Analysis

### What the Wireframe Shows

**1. Branding Change**
- App name: "ResuYOU" with emoji (🥳)
- Replace current "ResumeFlow" branding throughout

**2. Main Navigation Structure**
```
┌─────────────────────────────────────────────────┐
│ ResuYOU 🥳  │ User Profile │ Applications │     │
└─────────────────────────────────────────────────┘
```
- Two primary tabs: "User Profile" and "Applications"
- Tab-based navigation replaces current routing

**3. Applications List View**
```
┌─────────────────────────────────────────────────┐
│ [User Profile] [Applications]        [+]        │
├─────────────────────────────────────────────────┤
│ Application 1.  Google.   Job Name.      0%     │
├─────────────────────────────────────────────────┤
│ Application 2.  Apple.    Genius Bar.    42%    │
├─────────────────────────────────────────────────┤
│ Application 3.  Netflix.  SWE LOL.       69%    │
└─────────────────────────────────────────────────┘
```
- List of all user applications
- Each row displays: Company, Job Title, Match Score (%)
- "+" button to create new applications
- Rows are clickable to open application detail

**4. Application Detail View**
```
┌────────────────────────────────────────────────────────────────┐
│ Application 1                                   Download as PDF │
├─────────────────────┬──────────────────────────────────────────┤
│ Score: 0% 😡        │        ┌──────────────────┐              │
│                     │        │ John Doe Resume  │              │
│ Additional Info:    │        │                  │              │
│ • Stuff             │        │ Reasons U Should │              │
│ • Stuff             │        │ Hire Me:         │              │
│ • Stuff             │        │                  │              │
│                     │        │ • I'm smart.     │              │
│                     │        │ • I'm capable.   │              │
│                     │        └──────────────────┘              │
└─────────────────────┴──────────────────────────────────────────┘
```
- Score display with emoji indicator based on percentage
- Additional metadata/info section
- PDF download functionality
- Live resume preview panel

---

## Current State Analysis

### Existing Components to Modify
- `Header.tsx` - Rebrand to "ResuYOU", add tab navigation
- `App.tsx` - Update routing structure
- `LandingPage.tsx` - May become obsolete or simplified
- `ProfileFormPage.tsx` - Becomes content under "User Profile" tab

### Existing Components to Keep
- All form section components (PersonalInfo, Education, Work, etc.)
- UI components (Button, Input, Card, etc.)
- Form validation and state management
- API integration layer

### New Components Required
- `TabNavigation.tsx` - Main tab switcher
- `ApplicationsPage.tsx` - Applications list view
- `ApplicationDetailPage.tsx` - Single application view
- `ApplicationCard.tsx` - Row item in applications list
- `ScoreIndicator.tsx` - Score with emoji display
- `ResumePreview.tsx` - Live resume preview panel
- `CreateApplicationModal.tsx` - Modal for new applications

---

## Implementation Plan

### Phase 1: Database & Backend Setup
**Goal**: Enable application storage and retrieval

**Tasks**:
1. Create `Application` model/schema in backend
   - Fields: id, user_id, company_name, job_title, job_description, score, created_at, updated_at
2. Create API endpoints:
   - `GET /applications` - List all applications for user
   - `POST /applications` - Create new application
   - `GET /applications/{id}` - Get single application
   - `PUT /applications/{id}` - Update application
   - `DELETE /applications/{id}` - Delete application
3. Add score calculation logic (compare user profile to job requirements)

### Phase 2: Navigation & Layout Restructure
**Goal**: Implement tabbed navigation system

**Tasks**:
1. Update `Header.tsx`:
   - Change branding from "ResumeFlow" to "ResuYOU 🥳"
   - Integrate tab navigation into header
2. Create `TabNavigation.tsx` component:
   - Two tabs: "User Profile", "Applications"
   - Visual indicator for active tab
   - Click handlers for tab switching
3. Update `App.tsx` routing:
   - `/` - Redirect to `/profile` or show tabs
   - `/profile` - User Profile tab content
   - `/applications` - Applications list
   - `/applications/:id` - Application detail
4. Remove or repurpose `LandingPage.tsx`

### Phase 3: Applications List Feature
**Goal**: Display and manage list of applications

**Tasks**:
1. Create `ApplicationsPage.tsx`:
   - Fetch and display list of applications
   - Empty state when no applications exist
   - Loading and error states
2. Create `ApplicationCard.tsx`:
   - Display company, job title, score
   - Color-coded based on score (red/yellow/green)
   - Click handler to navigate to detail
3. Create `CreateApplicationModal.tsx`:
   - Form fields: Company Name, Job Title, Job Description (optional)
   - Submit creates new application via API
4. Add "+" button in header/tab area for creating applications
5. Integrate with API layer (`frontend/src/lib/api.ts`)

### Phase 4: Application Detail View
**Goal**: Show detailed view of single application

**Tasks**:
1. Create `ApplicationDetailPage.tsx`:
   - Header with application title
   - Score display with emoji indicator
   - Additional metadata section
   - Resume preview panel
   - PDF download button
2. Create `ScoreIndicator.tsx`:
   - Display percentage with appropriate emoji:
     - 0-30%: 😡 (angry/red)
     - 31-60%: 😐 (neutral/yellow)
     - 61-80%: 🙂 (happy/green)
     - 81-100%: 🤩 (excited/gold)
   - Visual progress bar or ring
3. Implement navigation back to applications list

### Phase 5: Resume Preview & PDF Generation
**Goal**: Show live resume preview and enable PDF download

**Tasks**:
1. Create `ResumePreview.tsx`:
   - Render user profile data in resume format
   - Styled to look like actual resume document
   - Responsive within detail view
2. Implement PDF generation:
   - Option A: Client-side with html2canvas + jsPDF
   - Option B: Backend endpoint that generates PDF
3. Add "Download as PDF" button functionality
4. Style resume template (clean, professional look)

### Phase 6: Score Calculation Integration
**Goal**: Calculate and display match scores

**Tasks**:
1. Implement scoring algorithm (backend):
   - Compare user skills to job requirements
   - Weight different factors (skills, experience, education)
   - Return percentage score
2. Store score on application record
3. Update score when user profile changes
4. Display score changes in real-time

---

## File Structure After Implementation

```
frontend/src/
├── components/
│   ├── applications/
│   │   ├── ApplicationCard.tsx       # NEW
│   │   ├── ApplicationsList.tsx      # NEW
│   │   ├── CreateApplicationModal.tsx # NEW
│   │   └── ScoreIndicator.tsx        # NEW
│   ├── layout/
│   │   ├── Header.tsx                # MODIFIED (rebrand + tabs)
│   │   ├── TabNavigation.tsx         # NEW
│   │   └── SectionNav.tsx            # KEEP
│   ├── resume/
│   │   ├── ResumePreview.tsx         # NEW
│   │   └── ResumeTemplate.tsx        # NEW
│   ├── sections/                     # KEEP ALL
│   ├── form/                         # KEEP ALL
│   └── ui/                           # KEEP ALL
├── pages/
│   ├── ProfilePage.tsx               # RENAMED from ProfileFormPage
│   ├── ApplicationsPage.tsx          # NEW
│   ├── ApplicationDetailPage.tsx     # NEW
│   └── SuccessPage.tsx               # KEEP (may repurpose)
├── stores/
│   ├── formStore.ts                  # KEEP
│   ├── uiStore.ts                    # MODIFY (add tab state)
│   └── applicationsStore.ts          # NEW
├── types/
│   ├── form.types.ts                 # KEEP
│   └── application.types.ts          # NEW
└── lib/
    ├── api.ts                        # MODIFY (add application endpoints)
    └── pdfGenerator.ts               # NEW
```

---

## New Type Definitions

```typescript
// application.types.ts

export interface Application {
  id: string;
  userId: string;
  companyName: string;
  jobTitle: string;
  jobDescription?: string;
  jobUrl?: string;
  score: number;
  status: 'draft' | 'applied' | 'interviewing' | 'offered' | 'rejected';
  createdAt: string;
  updatedAt: string;
}

export interface CreateApplicationInput {
  companyName: string;
  jobTitle: string;
  jobDescription?: string;
  jobUrl?: string;
}

export interface ApplicationsState {
  applications: Application[];
  selectedApplication: Application | null;
  isLoading: boolean;
  error: string | null;
}
```

---

## API Endpoints Required

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications` | List all user applications |
| POST | `/applications` | Create new application |
| GET | `/applications/{id}` | Get single application |
| PUT | `/applications/{id}` | Update application |
| DELETE | `/applications/{id}` | Delete application |
| POST | `/applications/{id}/calculate-score` | Recalculate score |
| GET | `/applications/{id}/resume-pdf` | Generate PDF |

---

## UI/UX Considerations

### Color Scheme for Scores
- **0-30%**: Red background (#FEE2E2), red text (#DC2626)
- **31-60%**: Yellow background (#FEF3C7), amber text (#D97706)
- **61-80%**: Green background (#D1FAE5), green text (#059669)
- **81-100%**: Gold background (#FEF3C7), gold text (#B45309)

### Responsive Design
- Mobile: Tabs stack vertically, list view uses cards
- Tablet: Side-by-side preview on detail page
- Desktop: Full layout as shown in wireframe

### Animations
- Tab switching: Fade transition
- Application list: Stagger fade-in on load
- Score indicator: Count-up animation
- Resume preview: Subtle shadow on hover

---

## Implementation Order & Dependencies

```
Phase 1 (Backend) ──┐
                    ├──> Phase 2 (Navigation) ──> Phase 3 (List)
                    │                                    │
                    │                                    v
                    └──────────────────────────> Phase 4 (Detail)
                                                         │
                                                         v
                                                 Phase 5 (PDF)
                                                         │
                                                         v
                                                 Phase 6 (Scoring)
```

---

## Success Criteria

1. User can switch between "User Profile" and "Applications" tabs
2. User can view list of all their applications with scores
3. User can create new applications with company/job info
4. User can click an application to see detailed view
5. Score displays with appropriate emoji indicator
6. User can preview their tailored resume
7. User can download resume as PDF
8. All existing profile form functionality remains intact

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| PDF generation complexity | Start with simple HTML template, enhance later |
| Score calculation accuracy | Begin with keyword matching, refine algorithm |
| Database schema changes | Plan migrations carefully, backup data |
| Breaking existing functionality | Keep ProfileFormPage intact, wrap in new layout |

---

## Next Steps

1. Review and approve this design document
2. Set up database tables for applications (Phase 1)
3. Begin frontend navigation restructure (Phase 2)
4. Iterate on remaining phases

---

## REVISED SCOPE (Feb 12, 2026)

After clarification, the scope has been **significantly reduced to UI-only**:

### What We ARE Building:
1. **Rebrand** from "ResumeFlow" to "ResuYOU 🥳"
2. **Tabbed navigation** (User Profile | Applications) in header
3. **Static Applications list page** with hardcoded mock data
4. **Landing page updates** - add Login/Sign Up buttons
5. **Remove auto-save** - delete Zustand persistence functionality

### What We Are NOT Building:
- ❌ No backend changes (someone else handles auth)
- ❌ No authentication implementation
- ❌ No score calculation
- ❌ No PDF generation
- ❌ No application detail view (list items not clickable)
- ❌ No data persistence (remove localStorage auto-save)
- ❌ "+" button is static (no modal, no functionality)

### Simplified File Changes:
```
MODIFY:
- frontend/src/components/layout/Header.tsx  (rebrand + tabs)
- frontend/src/pages/LandingPage.tsx         (add auth buttons)
- frontend/src/pages/ProfileFormPage.tsx     (remove auto-save)
- frontend/src/App.tsx                       (add /applications route)

CREATE:
- frontend/src/pages/ApplicationsPage.tsx    (static list with mock data)

POTENTIALLY DELETE:
- frontend/src/stores/formStore.ts           (auto-save store)
```

### Implementation Order:
1. Remove Zustand auto-save from ProfileFormPage
2. Update Header.tsx with "ResuYOU" branding + tab navigation
3. Update LandingPage with Login/Sign Up buttons
4. Create static ApplicationsPage component
5. Update App.tsx routing

---

*Document created: February 12, 2026*
*Last updated: February 12, 2026 - Scope revised to UI-only*
