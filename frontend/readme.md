# Resume Updater - Frontend

Frontend application for the Resume Updater built with React, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd Resume\ Updater/frontend

# Check Node version (must be 18+)
node --version

# Install dependencies
npm install

# Start development server
npm run dev

# Test in browser
open http://localhost:5173
```

The app will be available at http://localhost:5173

## Prerequisites

- **Node.js 18+** (recommended: use Node.js 20 LTS)
- npm (comes with Node.js)
- Git
- Backend server running at http://localhost:8000 (see backend README)

**If you don't have Node.js 18+:**
- macOS: `brew install node@20`
- Windows: Download from https://nodejs.org/
- Linux: Use nvm - `nvm install 20`

Check your versions:
```bash
node --version  # Should be 18.x or higher
npm --version   # Should be 9.x or higher
git --version   # Any recent version
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Resume\ Updater
```

### 2. Navigate to Frontend Directory

```bash
cd frontend
```

### 3. Check Node.js Version

Before installing dependencies, verify you have Node.js 18+ installed:

```bash
node --version
```

If you need to install or switch Node versions:

```bash
# Using nvm (recommended)
nvm install 20
nvm use 20

# Or using Homebrew (macOS)
brew install node@20
```

### 4. Install Dependencies

```bash
npm install
```

This will install all required packages. The installation may take 1-2 minutes.

### 5. Start the Development Server

```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 6. Verify Installation

Open your browser and navigate to:
- **App**: http://localhost:5173
- **Profile Form**: http://localhost:5173/profile

### 7. Start Backend Server (Required for Form Submission)

In a separate terminal, start the backend server:

```bash
cd ../backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

## Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Framework | React 18 | UI library |
| Language | TypeScript | Type safety |
| Build Tool | Vite | Fast dev server & bundler |
| Styling | Tailwind CSS v3.4 | Utility-first CSS |
| Form Management | React Hook Form | Performant form state |
| Validation | Zod | Schema validation |
| State Management | Zustand | Global state (drafts, UI) |
| Animations | Framer Motion | Smooth transitions |
| Icons | Lucide React | Modern icon set |
| Notifications | Sonner | Toast messages |
| Routing | React Router v6 | Client-side routing |

## Project Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── TagInput.tsx
│   │   │   ├── Card.tsx
│   │   │   └── index.ts
│   │   ├── form/            # Form-specific components
│   │   │   ├── FormField.tsx
│   │   │   ├── FormSection.tsx
│   │   │   ├── EntryCard.tsx
│   │   │   ├── DateRangeField.tsx
│   │   │   └── index.ts
│   │   ├── sections/        # Form section components
│   │   │   ├── PersonalInfoSection.tsx
│   │   │   ├── EducationSection.tsx
│   │   │   ├── WorkExperienceSection.tsx
│   │   │   ├── ProjectsSection.tsx
│   │   │   ├── SkillsSection.tsx
│   │   │   ├── CertificationsSection.tsx
│   │   │   ├── VolunteerSection.tsx
│   │   │   ├── LeadershipSection.tsx
│   │   │   └── index.ts
│   │   └── layout/          # Layout components
│   │       ├── Header.tsx
│   │       ├── SectionNav.tsx
│   │       └── index.ts
│   ├── pages/               # Page components
│   │   ├── LandingPage.tsx
│   │   ├── ProfileFormPage.tsx
│   │   ├── SuccessPage.tsx
│   │   └── index.ts
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # Zustand state stores
│   │   ├── formStore.ts     # Form draft persistence
│   │   └── uiStore.ts       # UI state management
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # Backend API client
│   │   ├── validation.ts    # Zod schemas
│   │   ├── utils.ts         # Helper functions
│   │   └── cn.ts            # Tailwind class merger
│   ├── types/               # TypeScript types
│   │   └── form.types.ts    # Form data interfaces
│   ├── config/              # Configuration
│   ├── App.tsx              # Root component with routing
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles & Tailwind
├── AI Usage/                # AI development documentation
│   └── user_profile_form_plan.md
├── tailwind.config.js       # Tailwind configuration
├── postcss.config.js        # PostCSS configuration
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Build
npm run build        # Type check + production build
npm run preview      # Preview production build locally

# Linting
npm run lint         # Run ESLint
```

## Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | LandingPage | Home page with CTA |
| `/profile` | ProfileFormPage | Main profile form (8 sections) |
| `/success` | SuccessPage | Post-submission confirmation |

## Form Sections

The profile form includes 8 sections:

1. **Personal Info** - Name, email, portfolio, GitHub, LinkedIn
2. **Education** - University, degree, major, GPA, dates (multi-entry)
3. **Work Experience** - Company, position, summary, description (multi-entry)
4. **Projects** - Name, link, tech stack, description (multi-entry)
5. **Skills** - 7 categories with tag-style inputs
6. **Certifications** - Name, organization, dates, credentials (multi-entry)
7. **Volunteer** - Organization, role, cause, description (multi-entry)
8. **Leadership** - Title, organization, description (multi-entry)

## Features

### Form Management
- **Auto-save drafts** to localStorage every 2 seconds
- **Draft restoration** on page reload with option to start fresh
- **Dynamic entries** - Add/remove items in multi-entry sections
- **Real-time validation** with clear error messages

### UI/UX
- **Sticky section navigation** with progress indicator
- **Smooth animations** using Framer Motion
- **Tag-style inputs** for skills with keyboard support
- **Toast notifications** for user feedback
- **Responsive design** - Mobile, tablet, and desktop

### Form Data Structure

The form submits data in this JSON structure:

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
    "courseType": "Bachelor's | Master's | PhD | ...",
    "major": "string",
    "gpa": "string | null",
    "location": "string | null",
    "startDate": "string | null",
    "endDate": "string | null",
    "isPresent": "boolean"
  }],
  "workExperience": [...],
  "projects": [...],
  "skills": {
    "programmingLanguages": ["string"],
    "frameworks": ["string"],
    "databases": ["string"],
    "toolsAndTechnologies": ["string"],
    "cloud": ["string"],
    "ai": ["string"],
    "other": ["string"]
  },
  "certifications": [...],
  "volunteer": [...],
  "leadership": [...]
}
```

## Backend Integration

The frontend connects to the backend API at `http://127.0.0.1:8000`.

### API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/user/registration` | Submit profile form |
| GET | `/health` | Check backend status |

### Configuring API URL

The API base URL is defined in `src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

For production, update this to your production API URL.

## Development

### Adding a New UI Component

1. Create the component in `src/components/ui/`:

```typescript
// src/components/ui/Badge.tsx
import { cn } from '@/lib/cn';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning';
}

export function Badge({ children, variant = 'default' }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
      variant === 'default' && 'bg-slate-100 text-slate-700',
      variant === 'success' && 'bg-green-100 text-green-700',
      variant === 'warning' && 'bg-amber-100 text-amber-700',
    )}>
      {children}
    </span>
  );
}
```

2. Export it from `src/components/ui/index.ts`:

```typescript
export { Badge } from './Badge';
```

### Adding a New Form Section

1. Create the section in `src/components/sections/`
2. Use `useFormContext` from React Hook Form
3. Use `useFieldArray` for multi-entry sections
4. Export from `src/components/sections/index.ts`
5. Add to `ProfileFormPage.tsx`

### Styling Guidelines

- Use Tailwind utility classes
- Custom colors: `primary-*`, `surface-*`, `accent-*`
- Use `cn()` helper for conditional classes
- Animations: Use Framer Motion for complex animations
- Keep components responsive (mobile-first)

## Common Issues

### 1. Node Version Mismatch

**Problem**: Build or install errors related to Node version.

**Solution**: Use Node.js 18+:
```bash
# Check version
node --version

# Use nvm to switch versions
nvm install 20
nvm use 20
```

### 2. Port Already in Use

**Problem**: `Error: Port 5173 is already in use`

**Solution**: Kill the process or use a different port:
```bash
# Find process using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or use a different port
npm run dev -- --port 3000
```

### 3. Backend Connection Errors

**Problem**: CORS errors or connection refused.

**Solution**:
1. Make sure backend is running at `http://localhost:8000`
2. Check backend CORS settings include `http://localhost:5173`
3. Verify with: `curl http://localhost:8000/health`

### 4. TypeScript Errors

**Problem**: TypeScript compilation errors.

**Solution**:
```bash
# Clear cache and rebuild
rm -rf node_modules/.vite
npm run build
```

### 5. Tailwind Classes Not Working

**Problem**: Custom Tailwind classes not applying.

**Solution**:
1. Make sure `tailwind.config.js` includes your files in `content`
2. Restart dev server after config changes
3. Check for typos in class names

## First Time Setup Checklist

Use this checklist when setting up the project for the first time:

- [ ] Git installed (`git --version`)
- [ ] Repository cloned (`git clone <repository-url>`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] In the `frontend` directory (`cd frontend`)
- [ ] Dependencies installed (`npm install` - no errors)
- [ ] Development server starts (`npm run dev`)
- [ ] App loads at http://localhost:5173
- [ ] Backend server running at http://localhost:8000 (see backend README)
- [ ] Form submission works (fill form and submit)
- [ ] Build succeeds (`npm run build`)

If all checkboxes are checked, you're ready to develop!

## Dependencies

### Production
- **react** - UI library
- **react-dom** - React DOM renderer
- **react-router-dom** - Client-side routing
- **react-hook-form** - Form state management
- **@hookform/resolvers** - Form validation integration
- **zod** - Schema validation
- **zustand** - State management
- **framer-motion** - Animations
- **lucide-react** - Icons
- **sonner** - Toast notifications
- **clsx** - Conditional classes
- **tailwind-merge** - Merge Tailwind classes

### Development
- **typescript** - Type checking
- **vite** - Build tool
- **tailwindcss** - CSS framework
- **postcss** - CSS processing
- **autoprefixer** - CSS vendor prefixes
- **@tailwindcss/forms** - Form element styling
- **tailwindcss-animate** - Animation utilities
- **eslint** - Code linting
- **@types/react** - React type definitions

## Team Collaboration

### First Time Setup (New Team Member)

```bash
# 1. Clone the repository
git clone <repository-url>
cd Resume\ Updater/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open in browser
open http://localhost:5173
```

### Before Starting Work (Returning Developer)

```bash
# 1. Pull latest changes
git pull

# 2. Install any new dependencies
npm install

# 3. Start backend server (in separate terminal)
cd ../backend
source venv/bin/activate
python main.py

# 4. Start frontend dev server
cd ../frontend
npm run dev

# 5. Verify app loads correctly
open http://localhost:5173
```

### After Adding New Dependencies

```bash
# Install package
npm install package-name

# Or for dev dependency
npm install -D package-name

# Commit package.json and package-lock.json
git add package.json package-lock.json
git commit -m "Add package-name dependency"
```

### Never Commit

- `node_modules/` directory
- `.env` files (if any)
- `dist/` build output
- `.vite/` cache

These are already in `.gitignore`.

### Stopping the Server

```bash
# If running in foreground
Press CTRL+C

# If running in background, find and kill the process
lsof -i :5173
kill -9 <PID>
```

## License

This project is part of the Resume Updater application.
