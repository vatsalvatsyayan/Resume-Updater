import type { ReactNode } from 'react';

import { cn } from '@/lib/cn';

function asRecord(v: unknown): Record<string, unknown> | null {
  return v !== null && typeof v === 'object' && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : null;
}

function asStr(v: unknown): string {
  return typeof v === 'string' ? v : '';
}

function asStrOpt(v: unknown): string | undefined {
  if (typeof v !== 'string') return undefined;
  const t = v.trim();
  return t ? t : undefined;
}

function asBool(v: unknown): boolean {
  return v === true;
}

function asStrList(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.filter((x): x is string => typeof x === 'string' && x.trim().length > 0);
}

function dateRange(
  start?: string,
  end?: string,
  isPresent?: boolean
): string | null {
  const s = asStrOpt(start);
  const e = isPresent ? 'Present' : asStrOpt(end);
  if (s && e) return `${s} – ${e}`;
  if (s) return s;
  if (e) return e;
  return null;
}

function SectionTitle({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h5
      className={cn(
        'mt-5 first:mt-0 border-b border-slate-200 pb-1 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500',
        className
      )}
    >
      {children}
    </h5>
  );
}

export function FormattedTailoredResume({
  data,
  className,
}: {
  data: Record<string, unknown>;
  className?: string;
}) {
  const name = asStr(data.name).trim() || 'Your name';
  const email = asStrOpt(data.email);
  const portfolio = asStrOpt(data.portfolioWebsite);
  const github = asStrOpt(data.githubUrl);
  const linkedin = asStrOpt(data.linkedinUrl);
  const summary = asStrOpt(data.professionalSummary);

  const contactParts = [email, portfolio, github, linkedin].filter(Boolean);

  const education = Array.isArray(data.education) ? data.education : [];
  const workExperience = Array.isArray(data.workExperience)
    ? data.workExperience
    : [];
  const projects = Array.isArray(data.projects) ? data.projects : [];
  const skills = asStrList(data.skills);
  const certifications = Array.isArray(data.certifications)
    ? data.certifications
    : [];
  const volunteer = Array.isArray(data.volunteer) ? data.volunteer : [];
  const leadership = Array.isArray(data.leadership) ? data.leadership : [];
  const extraSections = Array.isArray(data.extraSections)
    ? data.extraSections
    : [];

  return (
    <article
      className={cn(
        'rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-800 shadow-sm',
        'max-h-[min(480px,70vh)] overflow-y-auto leading-relaxed',
        className
      )}
    >
      <header className="border-b border-slate-200 pb-3">
        <h3 className="text-xl font-bold tracking-tight text-slate-900">{name}</h3>
        {contactParts.length > 0 && (
          <p className="mt-1.5 text-xs text-slate-600 break-words">
            {contactParts.join('  ·  ')}
          </p>
        )}
      </header>

      {summary && (
        <section className="mt-4">
          <SectionTitle>Summary</SectionTitle>
          <p className="mt-2 whitespace-pre-wrap text-[13px] text-slate-700">{summary}</p>
        </section>
      )}

      {education.length > 0 && (
        <section>
          <SectionTitle>Education</SectionTitle>
          <ul className="mt-2 space-y-3">
            {education.map((raw, i) => {
              const e = asRecord(raw);
              if (!e) return null;
              const degree = [asStr(e.courseName), asStr(e.major)].filter(Boolean).join(', ');
              const school = asStr(e.universityName);
              const dr = dateRange(
                asStrOpt(e.startDate),
                asStrOpt(e.endDate),
                asBool(e.isPresent)
              );
              const gpa = asStrOpt(e.gpa);
              return (
                <li key={i} className="text-[13px]">
                  <p className="font-semibold text-slate-900">
                    {[degree, school].filter(Boolean).join(' — ') || '—'}
                  </p>
                  {(dr || gpa) && (
                    <p className="text-xs text-slate-500">
                      {[dr, gpa ? `GPA: ${gpa}` : null].filter(Boolean).join(' · ')}
                    </p>
                  )}
                  {asStrOpt(e.highlight) && (
                    <p className="mt-1 text-slate-600">{asStrOpt(e.highlight)}</p>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {workExperience.length > 0 && (
        <section>
          <SectionTitle>Experience</SectionTitle>
          <ul className="mt-2 space-y-4">
            {workExperience.map((raw, i) => {
              const w = asRecord(raw);
              if (!w) return null;
              const position = asStr(w.position);
              const company = asStr(w.companyName);
              const loc = asStrOpt(w.location);
              const dr = dateRange(
                asStrOpt(w.startDate),
                asStrOpt(w.endDate),
                asBool(w.isPresent)
              );
              const bullets = asStrList(w.bullets);
              return (
                <li key={i}>
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0">
                    <p className="font-semibold text-slate-900">
                      {position}
                      {company ? ` — ${company}` : ''}
                      {loc ? ` · ${loc}` : ''}
                    </p>
                    {dr && (
                      <span className="text-xs tabular-nums text-slate-500">{dr}</span>
                    )}
                  </div>
                  {bullets.length > 0 && (
                    <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[13px] text-slate-700">
                      {bullets.map((b, j) => (
                        <li key={j} className="pl-0.5">
                          {b}
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {projects.length > 0 && (
        <section>
          <SectionTitle>Projects</SectionTitle>
          <ul className="mt-2 space-y-4">
            {projects.map((raw, i) => {
              const p = asRecord(raw);
              if (!p) return null;
              const title = asStr(p.projectName);
              const link = asStrOpt(p.link);
              const tech = asStrList(p.techStack);
              const bullets = asStrList(p.bullets);
              return (
                <li key={i}>
                  <p className="font-semibold text-slate-900">
                    {title}
                    {link ? (
                      <span className="font-normal text-slate-600">
                        {' '}
                        ·{' '}
                        <span className="break-all text-slate-600">{link}</span>
                      </span>
                    ) : null}
                  </p>
                  {tech.length > 0 && (
                    <p className="mt-0.5 text-xs text-slate-500">{tech.join(', ')}</p>
                  )}
                  {bullets.length > 0 && (
                    <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[13px] text-slate-700">
                      {bullets.map((b, j) => (
                        <li key={j}>{b}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {skills.length > 0 && (
        <section>
          <SectionTitle>Skills</SectionTitle>
          <p className="mt-2 text-[13px] text-slate-700">{skills.join(', ')}</p>
        </section>
      )}

      {certifications.length > 0 && (
        <section>
          <SectionTitle>Certifications</SectionTitle>
          <ul className="mt-2 space-y-2 text-[13px]">
            {certifications.map((raw, i) => {
              const c = asRecord(raw);
              if (!c) return null;
              const nm = asStr(c.name);
              const org = asStr(c.issuingOrganization);
              const issue = asStrOpt(c.issueDate);
              const exp = asBool(c.hasNoExpiry)
                ? null
                : asStrOpt(c.expiryDate);
              const line = [nm, org].filter(Boolean).join(' — ');
              const dates = [issue, exp ? `expires ${exp}` : null].filter(Boolean).join(' · ');
              return (
                <li key={i}>
                  <span className="font-medium text-slate-900">{line}</span>
                  {dates ? (
                    <span className="text-slate-500"> · {dates}</span>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {volunteer.length > 0 && (
        <section>
          <SectionTitle>Volunteer</SectionTitle>
          <ul className="mt-2 space-y-3">
            {volunteer.map((raw, i) => {
              const v = asRecord(raw);
              if (!v) return null;
              const role = asStr(v.role);
              const org = asStr(v.organizationName);
              const dr = dateRange(
                asStrOpt(v.startDate),
                asStrOpt(v.endDate),
                asBool(v.isPresent)
              );
              const bullets = asStrList(v.bullets);
              return (
                <li key={i} className="text-[13px]">
                  <p className="font-semibold text-slate-900">
                    {role}
                    {org ? ` — ${org}` : ''}
                  </p>
                  {dr && <p className="text-xs text-slate-500">{dr}</p>}
                  {bullets.length > 0 && (
                    <ul className="mt-1 list-disc space-y-1 pl-4 text-slate-700">
                      {bullets.map((b, j) => (
                        <li key={j}>{b}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {leadership.length > 0 && (
        <section>
          <SectionTitle>Leadership</SectionTitle>
          <ul className="mt-2 space-y-3">
            {leadership.map((raw, i) => {
              const l = asRecord(raw);
              if (!l) return null;
              const title = asStr(l.title);
              const org = asStr(l.organization);
              const dr = dateRange(
                asStrOpt(l.startDate),
                asStrOpt(l.endDate),
                asBool(l.isPresent)
              );
              const bullets = asStrList(l.bullets);
              return (
                <li key={i} className="text-[13px]">
                  <p className="font-semibold text-slate-900">
                    {title}
                    {org ? ` — ${org}` : ''}
                  </p>
                  {dr && <p className="text-xs text-slate-500">{dr}</p>}
                  {bullets.length > 0 && (
                    <ul className="mt-1 list-disc space-y-1 pl-4 text-slate-700">
                      {bullets.map((b, j) => (
                        <li key={j}>{b}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {extraSections.map((raw, i) => {
        const s = asRecord(raw);
        if (!s) return null;
        const secTitle = asStr(s.title).trim();
        const items = asStrList(s.items);
        if (!secTitle && items.length === 0) return null;
        return (
          <section key={i}>
            <SectionTitle>{secTitle || 'Additional'}</SectionTitle>
            {items.length > 0 ? (
              <ul className="mt-2 list-disc space-y-1 pl-4 text-[13px] text-slate-700">
                {items.map((item, j) => (
                  <li key={j}>{item}</li>
                ))}
              </ul>
            ) : null}
          </section>
        );
      })}
    </article>
  );
}
