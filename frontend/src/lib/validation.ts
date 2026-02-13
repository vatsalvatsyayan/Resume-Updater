import { z } from 'zod';

const urlSchema = z.string().url('Please enter a valid URL').optional().or(z.literal('')).nullable();
const dateSchema = z.string().optional().or(z.literal('')).nullable();

export const personalInfoSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name is too long'),
  email: z.string().email('Please enter a valid email address'),
  portfolioWebsite: urlSchema,
  githubUrl: urlSchema,
  linkedinUrl: urlSchema,
});

export const educationEntrySchema = z.object({
  id: z.string().optional(),
  universityName: z.string().min(1, 'University name is required'),
  courseName: z.string().min(1, 'Course name is required'),
  courseType: z.enum(["Bachelor's", "Master's", 'PhD', 'Diploma', 'Certificate', 'Associate', '']),
  major: z.string().min(1, 'Major is required'),
  gpa: z.string().optional().nullable(),
  location: z.string().optional().nullable(),
  startDate: dateSchema,
  endDate: dateSchema,
  isPresent: z.boolean(),
}).refine(
  (data) => {
    if (!data.isPresent && data.startDate && data.endDate) {
      return new Date(data.startDate) <= new Date(data.endDate);
    }
    return true;
  },
  { message: 'End date must be after start date', path: ['endDate'] }
);

export const workExperienceEntrySchema = z.object({
  id: z.string().optional(),
  companyName: z.string().min(1, 'Company name is required'),
  position: z.string().min(1, 'Position is required'),
  location: z.string().optional().nullable(),
  startDate: dateSchema,
  endDate: dateSchema,
  isPresent: z.boolean(),
  summary: z.string().max(500, 'Summary is too long').optional().nullable(),
  description: z.string().max(2000, 'Description is too long').optional().nullable(),
}).refine(
  (data) => {
    if (!data.isPresent && data.startDate && data.endDate) {
      return new Date(data.startDate) <= new Date(data.endDate);
    }
    return true;
  },
  { message: 'End date must be after start date', path: ['endDate'] }
);

export const projectEntrySchema = z.object({
  id: z.string().optional(),
  projectName: z.string().min(1, 'Project name is required'),
  link: urlSchema,
  techStack: z.array(z.string()),
  summary: z.string().max(300, 'Summary is too long').optional().nullable(),
  description: z.string().max(2000, 'Description is too long').optional().nullable(),
});

export const skillsSchema = z.object({
  programmingLanguages: z.array(z.string()),
  frameworks: z.array(z.string()),
  databases: z.array(z.string()),
  toolsAndTechnologies: z.array(z.string()),
  cloud: z.array(z.string()),
  ai: z.array(z.string()),
  other: z.array(z.string()),
});

export const certificationEntrySchema = z.object({
  id: z.string().optional(),
  name: z.string().min(1, 'Certification name is required'),
  issuingOrganization: z.string().min(1, 'Issuing organization is required'),
  issueDate: dateSchema,
  expiryDate: dateSchema,
  hasNoExpiry: z.boolean(),
  credentialId: z.string().optional().nullable(),
  credentialUrl: urlSchema,
});

export const volunteerEntrySchema = z.object({
  id: z.string().optional(),
  organizationName: z.string().min(1, 'Organization name is required'),
  role: z.string().min(1, 'Role is required'),
  cause: z.string().optional().nullable(),
  location: z.string().optional().nullable(),
  startDate: dateSchema,
  endDate: dateSchema,
  isPresent: z.boolean(),
  description: z.string().max(2000, 'Description is too long').optional().nullable(),
});

export const leadershipEntrySchema = z.object({
  id: z.string().optional(),
  title: z.string().min(1, 'Title is required'),
  organization: z.string().min(1, 'Organization is required'),
  startDate: dateSchema,
  endDate: dateSchema,
  isPresent: z.boolean(),
  description: z.string().max(2000, 'Description is too long').optional().nullable(),
});

export const profileFormSchema = z.object({
  personalInfo: personalInfoSchema,
  education: z.array(educationEntrySchema),
  workExperience: z.array(workExperienceEntrySchema),
  projects: z.array(projectEntrySchema),
  skills: skillsSchema,
  certifications: z.array(certificationEntrySchema),
  volunteer: z.array(volunteerEntrySchema),
  leadership: z.array(leadershipEntrySchema),
});

export type ProfileFormSchema = z.infer<typeof profileFormSchema>;
