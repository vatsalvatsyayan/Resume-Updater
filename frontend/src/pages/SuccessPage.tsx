import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle2, ArrowRight, FileText, Sparkles } from 'lucide-react';

import { Header } from '@/components/layout';

export function SuccessPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="mx-auto flex min-h-[calc(100vh-64px)] max-w-4xl items-center justify-center px-4 py-10">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm"
        >
          <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-green-100">
            <CheckCircle2 className="h-12 w-12 text-green-600" />
          </div>

          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            Profile Saved Successfully!
          </h1>

          <p className="mx-auto mt-4 max-w-xl text-lg leading-8 text-slate-600">
            Your professional profile is now ready. You can generate tailored resumes for any job
            application from the Applications page.
          </p>

          <div className="mx-auto mt-10 grid max-w-xl gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-left">
              <div className="mb-3 inline-flex rounded-xl bg-slate-900 p-3 text-white">
                <FileText className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">Generate Resume</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Go to Applications and create a tailored resume for a specific job description.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-left">
              <div className="mb-3 inline-flex rounded-xl bg-amber-100 p-3 text-amber-700">
                <Sparkles className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">AI Optimization</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Use the tailored resume flow to optimize your resume for each application.
              </p>
            </div>
          </div>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              to="/profile"
              className="inline-flex items-center justify-center rounded-xl border border-slate-300 px-6 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Edit Profile
            </Link>

            <Link
              to="/applications"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
            >
              Generate Resume
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </motion.div>
      </main>
    </div>
  );
}