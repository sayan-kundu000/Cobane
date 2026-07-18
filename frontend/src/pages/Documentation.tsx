import React, { useState } from 'react';
import Card from '../components/ui/Card.tsx';
import Badge from '../components/ui/Badge.tsx';

type Section = 'modules' | 'classes' | 'functions' | 'readme';

export const Documentation: React.FC = () => {
  const [activeSection, setActiveSection] = useState<Section>('readme');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm">
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Codebase & API Documentation
        </h1>
        <p className="text-sm text-gray-550 mt-1">
          Explore system module architecture, helper class references, and function specifications.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Navigation sidebar */}
        <Card className="lg:col-span-1 p-4 space-y-2">
          <span className="text-xs font-bold text-gray-450 uppercase tracking-wider block px-2 mb-2">
            Table of Contents
          </span>
          <button
            onClick={() => setActiveSection('readme')}
            className={`w-full text-left px-3 py-2 text-xs font-bold uppercase rounded-lg transition-all outline-none ${
              activeSection === 'readme'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            README Summary
          </button>
          <button
            onClick={() => setActiveSection('modules')}
            className={`w-full text-left px-3 py-2 text-xs font-bold uppercase rounded-lg transition-all outline-none ${
              activeSection === 'modules'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            System Modules
          </button>
          <button
            onClick={() => setActiveSection('classes')}
            className={`w-full text-left px-3 py-2 text-xs font-bold uppercase rounded-lg transition-all outline-none ${
              activeSection === 'classes'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Class Documentation
          </button>
          <button
            onClick={() => setActiveSection('functions')}
            className={`w-full text-left px-3 py-2 text-xs font-bold uppercase rounded-lg transition-all outline-none ${
              activeSection === 'functions'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Function Catalog
          </button>
        </Card>

        {/* Details display area - right 3 columns */}
        <Card className="lg:col-span-3 space-y-6">
          {activeSection === 'readme' && (
            <div className="space-y-4">
              <h2 className="text-xl font-extrabold text-gray-900 dark:text-white">
                Cobane AI Code Review Assistant
              </h2>
              <p className="text-sm text-gray-550 leading-relaxed">
                Cobane is a production-oriented platform designed to automate code analysis, security scanning, and qualitative audits. It couples standard static checker tools (Pylint, Bandit, Radon) with Large Language Models (LLM) to perform contextual code reviews.
              </p>
              <div className="border-t border-gray-150 dark:border-gray-700 pt-4 space-y-3">
                <h4 className="font-bold text-sm text-gray-900 dark:text-white">Key Capabilities</h4>
                <ul className="list-disc pl-5 text-xs text-gray-550 space-y-2">
                  <li><strong>Style Conformity:</strong> Evaluates PEP 8 warnings using custom Pylint configs.</li>
                  <li><strong>Security Auditing:</strong> Catches secrets leakage and packages threat vulnerabilities using Bandit.</li>
                  <li><strong>Complexity Metrics:</strong> Radon computations for Cyclomatic Complexity and Maintainability.</li>
                  <li><strong>AI Advice:</strong> Fine-tuned suggestions explaining rationale for style improvements and bug fixes.</li>
                </ul>
              </div>
            </div>
          )}

          {activeSection === 'modules' && (
            <div className="space-y-4">
              <h2 className="text-xl font-extrabold text-gray-900 dark:text-white">System Modules</h2>
              <div className="space-y-4 divide-y divide-gray-150 dark:divide-gray-700/80">
                <div className="pt-0 space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white font-mono">
                      app.services.static_analysis_engine
                    </h3>
                    <Badge variant="primary">core</Badge>
                  </div>
                  <p className="text-xs text-gray-500">
                    Orchestrates checker executions. Wraps Pylint, Bandit, and Radon adapters to aggregate and normalize metrics into standard JSON formats.
                  </p>
                </div>
                <div className="pt-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white font-mono">
                      app.services.ai_service
                    </h3>
                    <Badge variant="secondary">ai</Badge>
                  </div>
                  <p className="text-xs text-gray-500">
                    Constructs semantic prompt payloads, embeds code files with warning contexts, and routes queries to LLM engines to generate reviews.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'classes' && (
            <div className="space-y-4">
              <h2 className="text-xl font-extrabold text-gray-900 dark:text-white">Class Reference</h2>
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-900 dark:text-white font-mono">
                    class StaticAnalysisOrchestrator
                  </h3>
                  <p className="text-xs text-gray-550 leading-relaxed">
                    Orchestration class that initiates asynchronous processes to run third-party checkers. Combines outputs and returns a consolidated analysis envelope.
                  </p>
                  <pre className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs font-mono overflow-x-auto text-gray-750 dark:text-gray-300">
{`class StaticAnalysisOrchestrator:
    def __init__(self):
        self.pylint = PylintAdapter()
        self.bandit = BanditAdapter()
        self.radon = RadonAdapter()

    async def run_analysis_async(self, file_path: str) -> AnalysisReport:
        # runs Pylint, Bandit & Radon concurrently`}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'functions' && (
            <div className="space-y-4">
              <h2 className="text-xl font-extrabold text-gray-900 dark:text-white">Function Reference</h2>
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-900 dark:text-white font-mono">
                    def sanitize_path(base_dir: str, user_path: str) {"->"} str
                  </h3>
                  <p className="text-xs text-gray-550">
                    Helper function preventing directory traversal attacks. Ensures all file read/write scopes are anchored under the base folder path.
                  </p>
                  <pre className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs font-mono overflow-x-auto text-gray-750 dark:text-gray-300">
{`def sanitize_path(base_dir: str, user_path: str) -> str:
    resolved_base = os.path.abspath(base_dir)
    resolved_target = os.path.abspath(os.path.join(base_dir, user_path))
    if not resolved_target.startswith(resolved_base):
        raise ValueError("Directory traversal attempt detected.")
    return resolved_target`}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Documentation;
