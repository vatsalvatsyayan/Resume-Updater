# UI Fixes Plan

Author: Vatsal Vatsyayan

## Overview

This document outlines fixes for three UI issues identified in the current ResuYOU frontend.

---

## Issue 1: Landing Page - Add Login/Sign Up to Navbar

### Current State
- Login and Sign Up buttons exist in the hero section CTA area ([LandingPage.tsx:97-108](src/pages/LandingPage.tsx#L97-L108))
- Header component on landing page only shows the logo, no auth buttons ([Header.tsx](src/components/layout/Header.tsx))

### Problem
- User expects Login/Sign Up buttons in the navbar for quick access
- Currently users must scroll to find these buttons

### Solution
Modify `Header.tsx` to show Login/Sign Up buttons when on the landing page (`/`).

### File Changes
```
MODIFY: frontend/src/components/layout/Header.tsx
```

### Implementation Details
1. Check if current route is the landing page (`location.pathname === '/'`)
2. When on landing page, render Login and Sign Up buttons in the header (right side)
3. Style to match the existing button design - Login as primary, Sign Up as outline
4. Both link to `/profile` for now (auth not implemented)

### Code Changes
```tsx
// In Header.tsx, add after the tab navigation section:
{location.pathname === '/' && (
  <div className="flex items-center gap-3">
    <Link to="/profile">
      <Button size="sm" leftIcon={<LogIn className="w-4 h-4" />}>
        Log In
      </Button>
    </Link>
    <Link to="/profile">
      <Button variant="outline" size="sm" leftIcon={<UserPlus className="w-4 h-4" />}>
        Sign Up
      </Button>
    </Link>
  </div>
)}
```

---

## Issue 2: Personal Information - Icon/Text Overlap

### Current State
- Input component uses `leftAddon` prop to display icons ([Input.tsx:30-33](src/components/ui/Input.tsx#L30-L33))
- Icon positioned at `left-4` (1rem = 16px)
- Input padding set to `pl-11` (2.75rem = 44px) when leftAddon present ([Input.tsx:46](src/components/ui/Input.tsx#L46))

### Problem
- Text overlaps with the icon for all fields except name
- The 44px left padding may not be sufficient depending on icon size and input font size

### Root Cause Analysis
The icon is 4x4 (1rem = 16px) positioned at left: 1rem. This means icon occupies space from 16px to 32px. With `pl-11` (44px), there's only 12px gap between icon and text start. This may cause visual overlap especially with placeholder text.

### Solution
Increase the left padding when `leftAddon` is present.

### File Changes
```
MODIFY: frontend/src/components/ui/Input.tsx
```

### Implementation Details
1. Change `pl-11` to `pl-12` (3rem = 48px) for more breathing room
2. Alternatively, move icon slightly left from `left-4` to `left-3`

### Recommended Fix
Change line 46 in Input.tsx:
```tsx
// Before
leftAddon && 'pl-11',

// After
leftAddon && 'pl-12',
```

---

## Issue 3: SectionNav Filters - Volunteer/Leadership Labels Cut Off

### Current State
- Section pills use `overflow-x-auto` for horizontal scrolling ([SectionNav.tsx:92](src/components/layout/SectionNav.tsx#L92))
- Labels use `hidden sm:inline` to hide text on mobile, show on sm+ ([SectionNav.tsx:124](src/components/layout/SectionNav.tsx#L124))
- Pills use `whitespace-nowrap` to prevent text wrapping ([SectionNav.tsx:107](src/components/layout/SectionNav.tsx#L107))

### Problem
- "Volunteer" is partially visible
- "Leadership" is not visible at all
- The horizontal scroll area may not extend far enough, or pills are being cut off

### Root Cause Analysis
The container has fixed max-width (`max-w-4xl`) and the pills container may not have proper scroll behavior or the rightmost pills are being clipped.

### Solution
Multiple fixes to ensure all section pills are visible and scrollable.

### File Changes
```
MODIFY: frontend/src/components/layout/SectionNav.tsx
```

### Implementation Details

1. **Ensure proper scrollable container**: Add explicit min-width to pills to prevent compression
2. **Add scroll padding**: Add padding-right to ensure last items aren't clipped
3. **Consider scroll indicators**: Optional - add fade effect to indicate more content

### Recommended Fix
```tsx
// Line 92 - Add pr-4 for scroll padding on the right
<div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1 pr-4">

// Each button - ensure minimum width doesn't get compressed
<motion.button
  ...
  className={cn(
    'relative flex items-center gap-2 px-4 py-2 rounded-full',
    'text-sm font-medium whitespace-nowrap',
    'flex-shrink-0',  // ADD THIS - prevents pills from shrinking
    ...
  )}
>
```

The key fix is adding `flex-shrink-0` to each pill button to prevent them from being compressed when space is limited.

---

## Implementation Order

1. **Issue 3 (SectionNav)** - Quick fix, high impact on usability
2. **Issue 2 (Input overlap)** - Single line change, improves form usability
3. **Issue 1 (Navbar auth)** - Requires imports and slightly more code

---

## Testing Checklist

- [ ] Landing page shows Login/Sign Up buttons in navbar
- [ ] Login/Sign Up buttons in navbar navigate to `/profile`
- [ ] Personal Info fields show no overlap between icons and placeholder/input text
- [ ] All 8 section pills are visible and scrollable in SectionNav
- [ ] "Volunteer" and "Leadership" pills fully visible when scrolled
- [ ] Horizontal scroll works smoothly on the filter bar
- [ ] Mobile responsive behavior preserved

---

*Document created: February 13, 2026*
