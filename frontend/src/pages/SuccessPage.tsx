import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle2, ArrowRight, FileText, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui';
import { Header } from '@/components/layout';

export function SuccessPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          {/* Success Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            className="relative inline-block mb-8"
          >
            <div className="absolute inset-0 bg-green-400 rounded-full blur-xl opacity-30" />
            <div className="relative w-24 h-24 bg-green-500 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-12 h-12 text-white" />
            </div>
          </motion.div>

          {/* Content */}
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold text-slate-900 mb-4"
          >
            Profile Saved Successfully!
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-xl text-slate-600 mb-8 max-w-md mx-auto"
          >
            Your professional profile is now ready. You can generate tailored resumes for any job application.
          </motion.p>

          {/* Next Steps */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-2xl border border-slate-200 p-8 mb-8"
          >
            <h2 className="text-lg font-semibold text-slate-900 mb-6">
              What's Next?
            </h2>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl">
                <div className="p-2 bg-slate-900 rounded-xl">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-slate-900">Generate Resume</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Create a tailored resume for specific jobs
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl">
                <div className="p-2 bg-amber-500 rounded-xl">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-slate-900">AI Optimization</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Let AI enhance your resume for ATS
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/profile">
              <Button variant="outline" size="lg">
                Edit Profile
              </Button>
            </Link>
            <Link to="/">
              <Button size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                Back to Home
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
}
