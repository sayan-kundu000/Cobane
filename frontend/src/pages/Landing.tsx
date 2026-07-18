import React from 'react';
import { Link } from 'react-router-dom';

export const Landing: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center space-y-12 max-w-4xl mx-auto px-4 py-16">
      {/* Hero section */}
      <div className="space-y-6">
        <div className="inline-flex items-center space-x-2 bg-primary-50 dark:bg-primary-950/30 text-primary-600 dark:text-primary-400 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase border border-primary-200/55 dark:border-primary-900/60">
          <span>✨ Introducing Cobane 1.0</span>
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 via-primary-600 to-indigo-600 dark:from-white dark:via-primary-400 dark:to-indigo-400 bg-clip-text text-transparent leading-[1.15]">
          AI-Powered Code Review & Quality Assistant
        </h1>
        <p className="text-md sm:text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
          Automate security scans, complexity audits, formatting checks, and receive context-aware AI recommendations directly on your codebase files.
        </p>
      </div>

      {/* Call to Actions */}
      <div className="flex flex-col sm:flex-row justify-center items-center gap-4 w-full max-w-sm">
        <Link
          to="/auth?mode=register"
          className="w-full sm:w-auto px-8 py-3.5 bg-primary-600 hover:bg-primary-700 text-white rounded-full font-bold transition shadow-lg shadow-primary-500/20 text-center"
        >
          Create Account
        </Link>
        <Link
          to="/auth?mode=login"
          className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-primary-50 text-primary-600 border border-primary-600 dark:bg-gray-800 dark:hover:bg-primary-950/20 dark:text-primary-400 dark:border-primary-800 rounded-full font-bold transition text-center shadow-lg shadow-primary-500/5"
        >
          Sign In
        </Link>
      </div>

      {/* Feature cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full pt-10">
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-750 p-6 rounded-xl text-left space-y-3">
          <div className="p-3 bg-red-50 dark:bg-red-950/20 text-red-500 rounded-lg w-fit">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="font-bold text-gray-900 dark:text-white">Security Vulnerabilities</h3>
          <p className="text-sm text-gray-550 dark:text-gray-400">
            Powered by Bandit checks. Identify credentials leak, vulnerable packages, and injection loopholes inside files.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-755 p-6 rounded-xl text-left space-y-3">
          <div className="p-3 bg-green-50 dark:bg-green-950/20 text-green-500 rounded-lg w-fit">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
            </svg>
          </div>
          <h3 className="font-bold text-gray-900 dark:text-white">Complexity Auditing</h3>
          <p className="text-sm text-gray-550 dark:text-gray-400">
            Calculated with Radon. Monitor Maintainability Index, cyclomatic complexity scores, and line count of structures.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-755 p-6 rounded-xl text-left space-y-3">
          <div className="p-3 bg-purple-50 dark:bg-purple-950/20 text-purple-500 rounded-lg w-fit">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="font-bold text-gray-900 dark:text-white">AI Suggestion Engine</h3>
          <p className="text-sm text-gray-550 dark:text-gray-400">
            Intelligent review summaries detailing code quality warnings, refactoring recommendations, and inline helper comments.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Landing;
