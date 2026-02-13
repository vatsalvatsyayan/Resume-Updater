import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Plus, LogIn, UserPlus } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui';

interface HeaderProps {
  className?: string;
  onAddClick?: () => void;
}

export function Header({ className, onAddClick }: HeaderProps) {
  const location = useLocation();
  const isAppPage = location.pathname === '/profile' || location.pathname === '/applications';
  const currentTab = location.pathname === '/applications' ? 'applications' : 'profile';

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'sticky top-0 z-50',
        'backdrop-blur-xl bg-white/80 border-b border-slate-200/50',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-amber-400 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative p-2 bg-slate-900 rounded-xl">
                <FileText className="w-5 h-5 text-white" />
              </div>
            </div>
            <span className="text-lg font-bold text-slate-900 tracking-tight">
              ResuYOU 🥳
            </span>
          </Link>

          {/* Tab Navigation - shown on app pages */}
          {isAppPage && (
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
              <Link
                to="/profile"
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-all',
                  currentTab === 'profile'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                )}
              >
                User Profile
              </Link>
              <Link
                to="/applications"
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-all',
                  currentTab === 'applications'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                )}
              >
                Applications
              </Link>
            </div>
          )}


          {/* Auth buttons - shown on landing page */}
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

          {/* Add button - shown on applications page */}
          {location.pathname === '/applications' && onAddClick && (
            <button
              className="p-2 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors"
              onClick={onAddClick}
            >
              <Plus className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </motion.header>
  );
}
