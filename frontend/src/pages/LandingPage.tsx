import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Sparkles,
  Target,
  Zap,
  CheckCircle2,
  Star,
  LogIn,
  UserPlus,
} from "lucide-react";
import { Button } from "@/components/ui";
import { Header } from "@/components/layout";

import { useClerk } from "@clerk/clerk-react"; // <-- added

const features = [
  {
    icon: Target,
    title: "Tailored to Each Role",
    description: "AI optimizes your resume for specific job descriptions",
  },
  {
    icon: Zap,
    title: "Instant Generation",
    description: "Create professional resumes in seconds, not hours",
  },
  {
    icon: CheckCircle2,
    title: "ATS-Optimized",
    description: "Pass through applicant tracking systems with ease",
  },
];

export function LandingPage() {
  const clerk = useClerk();

  const handleOpenSignIn = (e?: React.MouseEvent) => {
    e?.preventDefault();
    // opens modal or redirects depending on your Clerk setup; returns to /profile after auth
    clerk.openSignIn({ redirectUrl: "/profile" });
  };

  const handleOpenSignUp = (e?: React.MouseEvent) => {
    e?.preventDefault();
    clerk.openSignUp({ redirectUrl: "/profile" });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      {/* Hero Section */}
      <main className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-amber-200/30 via-transparent to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-gradient-to-tr from-slate-200/50 via-transparent to-transparent rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-slate-200 shadow-sm mb-6"
              >
                <div className="flex -space-x-1">
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={i}
                      className="w-6 h-6 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 border-2 border-white flex items-center justify-center"
                    >
                      <Star className="w-3 h-3 text-amber-500" fill="currentColor" />
                    </div>
                  ))}
                </div>
                <span className="text-sm font-medium text-slate-600">
                  Trusted by 10,000+ job seekers
                </span>
              </motion.div>

              {/* Headline */}
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-slate-900 leading-[1.1] tracking-tight mb-6">
                Your Resume,{" "}
                <span className="relative">
                  <span className="relative z-10 text-transparent bg-clip-text bg-gradient-to-r from-slate-700 to-slate-900">
                    Perfected
                  </span>
                  <motion.span
                    className="absolute bottom-2 left-0 w-full h-3 bg-amber-300/50 -z-10 rounded"
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ delay: 0.5, duration: 0.4 }}
                  />
                </span>
              </h1>

              <p className="text-xl text-slate-600 mb-8 max-w-lg leading-relaxed">
                Build a profile once, generate unlimited tailored resumes for every job application.
                Let AI handle the heavy lifting.
              </p>

              {/* CTA Buttons (wired to Clerk) */}
              <div className="flex flex-wrap gap-4">
                {/* Use your Button but call Clerk programmatically */}
                <Button size="lg" leftIcon={<LogIn className="w-5 h-5" />} onClick={handleOpenSignIn}>
                  Log In
                </Button>

                <Button variant="outline" size="lg" leftIcon={<UserPlus className="w-5 h-5" />} onClick={handleOpenSignUp}>
                  Sign Up
                </Button>
              </div>

              {/* Features */}
              <div className="mt-12 grid sm:grid-cols-3 gap-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="flex flex-col"
                  >
                    <div className="p-2 bg-slate-900 rounded-xl w-fit mb-3">
                      <feature.icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-sm font-semibold text-slate-900 mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-slate-500">{feature.description}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Right Column - Visual */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative lg:pl-12 hidden lg:block"
            >
              {/* ... right column unchanged ... */}
              <div className="relative">
                <div className="absolute -inset-4 bg-gradient-to-r from-amber-200/50 via-slate-200/50 to-slate-300/50 rounded-3xl blur-2xl" />
                <div className="relative bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 overflow-hidden">
                  {/* resume preview content ... */}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-8 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-slate-500">
            Built for students by students.
          </p>
        </div>
      </footer>
    </div>
  );
}
