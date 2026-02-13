export interface PersonalInfo {
  name: string;
  email: string;
  portfolioWebsite: string | null;
  githubUrl: string | null;
  linkedinUrl: string | null;
}

export interface Education {
  id?: string;
  universityName: string;
  courseName: string;
  courseType: 'Bachelor\'s' | 'Master\'s' | 'PhD' | 'Diploma' | 'Certificate' | 'Associate' | '';
  major: string;
  gpa: string | null;
  location: string | null;
  startDate: string | null;
  endDate: string | null;
  isPresent: boolean;
}

export interface WorkExperience {
  id?: string;
  companyName: string;
  position: string;
  location: string | null;
  startDate: string | null;
  endDate: string | null;
  isPresent: boolean;
  summary: string | null;
  description: string | null;
}

export interface Project {
  id?: string;
  projectName: string;
  link: string | null;
  techStack: string[];
  summary: string | null;
  description: string | null;
}

export interface Skills {
  programmingLanguages: string[];
  frameworks: string[];
  databases: string[];
  toolsAndTechnologies: string[];
  cloud: string[];
  ai: string[];
  other: string[];
}

export interface Certification {
  id?: string;
  name: string;
  issuingOrganization: string;
  issueDate: string | null;
  expiryDate: string | null;
  hasNoExpiry: boolean;
  credentialId: string | null;
  credentialUrl: string | null;
}

export interface Volunteer {
  id?: string;
  organizationName: string;
  role: string;
  cause: string | null;
  location: string | null;
  startDate: string | null;
  endDate: string | null;
  isPresent: boolean;
  description: string | null;
}

export interface Leadership {
  id?: string;
  title: string;
  organization: string;
  startDate: string | null;
  endDate: string | null;
  isPresent: boolean;
  description: string | null;
}

export interface ProfileFormData {
  personalInfo: PersonalInfo;
  education: Education[];
  workExperience: WorkExperience[];
  projects: Project[];
  skills: Skills;
  certifications: Certification[];
  volunteer: Volunteer[];
  leadership: Leadership[];
}

export const defaultPersonalInfo: PersonalInfo = {
  name: '',
  email: '',
  portfolioWebsite: null,
  githubUrl: null,
  linkedinUrl: null,
};

export const defaultEducation: Education = {
  universityName: '',
  courseName: '',
  courseType: '',
  major: '',
  gpa: null,
  location: null,
  startDate: null,
  endDate: null,
  isPresent: false,
};

export const defaultWorkExperience: WorkExperience = {
  companyName: '',
  position: '',
  location: null,
  startDate: null,
  endDate: null,
  isPresent: false,
  summary: null,
  description: null,
};

export const defaultProject: Project = {
  projectName: '',
  link: null,
  techStack: [],
  summary: null,
  description: null,
};

export const defaultSkills: Skills = {
  programmingLanguages: [],
  frameworks: [],
  databases: [],
  toolsAndTechnologies: [],
  cloud: [],
  ai: [],
  other: [],
};

export const defaultCertification: Certification = {
  name: '',
  issuingOrganization: '',
  issueDate: null,
  expiryDate: null,
  hasNoExpiry: false,
  credentialId: null,
  credentialUrl: null,
};

export const defaultVolunteer: Volunteer = {
  organizationName: '',
  role: '',
  cause: null,
  location: null,
  startDate: null,
  endDate: null,
  isPresent: false,
  description: null,
};

export const defaultLeadership: Leadership = {
  title: '',
  organization: '',
  startDate: null,
  endDate: null,
  isPresent: false,
  description: null,
};

export const defaultProfileFormData: ProfileFormData = {
  personalInfo: defaultPersonalInfo,
  education: [defaultEducation],
  workExperience: [defaultWorkExperience],
  projects: [defaultProject],
  skills: defaultSkills,
  certifications: [],
  volunteer: [],
  leadership: [],
};
