import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listProjects } from '../services/projects.ts';
import { listReviews } from '../services/reviews.ts';
import StatCard from '../components/dashboard/StatCard.tsx';
import QualityChart from '../components/dashboard/QualityChart.tsx';
import SecurityChart from '../components/dashboard/SecurityChart.tsx';
import Card from '../components/ui/Card.tsx';
import Badge from '../components/ui/Badge.tsx';

export const Dashboard: React.FC = () => {
  // Query projects and reviews list
  const { data: projectsData, isLoading: loadingProjects } = useQuery({
    queryKey: ['projects', { page_size: 5 }],
    queryFn: () => listProjects({ page_size: 5 }),
  });

  const { data: reviewsData, isLoading: loadingReviews } = useQuery({
    queryKey: ['reviews', { page_size: 5 }],
    queryFn: () => listReviews({ page_size: 5 }),
  });

  const projects = projectsData?.data?.items || [];
  const reviews = reviewsData?.data?.items || [];

  // Calculate statistics summaries from lists or defaults
  const totalProjects = projectsData?.data?.pagination?.total_items || projects.length || 0;
  const totalReviews = reviewsData?.data?.pagination?.total_items || reviews.length || 0;

  // Visual chart datasets
  const qualityData = [
    { name: 'Initial Commit', pylint: 65, complexity: 72 },
    { name: 'Feature A Update', pylint: 78, complexity: 80 },
    { name: 'Refactoring Phase', pylint: 85, complexity: 88 },
    { name: 'Current Build', pylint: 92, complexity: 90 },
  ];

  const securityData = [
    { category: 'SQL Injection', count: 0 },
    { category: 'Hardcoded Secrets', count: 1 },
    { category: 'Insecure Asserts', count: 2 },
    { category: 'Others', count: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            System Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Access recent review indicators, codebase metrics, and quick diagnostics panel.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/projects"
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-xs font-bold transition flex items-center"
          >
            <svg className="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
            </svg>
            New Project
          </Link>
          <Link
            to="/backend-status"
            className="px-4 py-2 bg-indigo-650 hover:bg-indigo-700 text-white dark:bg-indigo-600 dark:hover:bg-indigo-500 rounded-lg text-xs font-bold transition"
          >
            Diagnose Health
          </Link>
        </div>
      </div>

      {/* KPI Counters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Projects"
          value={totalProjects}
          subtext="Configured workspaces"
          loading={loadingProjects}
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          }
        />
        <StatCard
          title="Total Reviews Conducted"
          value={totalReviews}
          subtext="Static & AI pipelines"
          loading={loadingReviews}
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Average Pylint Score"
          value="7.8 / 10"
          subtext="Coding style & warnings"
          trend={{ value: '1.2%', isPositive: true }}
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          }
        />
        <StatCard
          title="Maintainability Index"
          value="88.5"
          subtext="Radon Complexity Index"
          trend={{ value: 'A Grade', isPositive: true }}
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
      </div>

      {/* Visualizations charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QualityChart data={qualityData} />
        <SecurityChart data={securityData} />
      </div>

      {/* Lists split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent projects list */}
        <Card className="lg:col-span-1 space-y-4">
          <div>
            <h3 className="text-md font-bold text-gray-900 dark:text-white">Active Projects</h3>
            <p className="text-xs text-gray-500">Your workspaces</p>
          </div>
          <div className="divide-y divide-gray-150 dark:divide-gray-700/80">
            {loadingProjects ? (
              <div className="animate-pulse space-y-4 py-3">
                <div className="h-4 bg-gray-250 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-4 bg-gray-250 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            ) : projects.length === 0 ? (
              <p className="text-xs text-gray-400 italic py-4">No active projects configure a new workspace.</p>
            ) : (
              projects.map((proj) => (
                <div key={proj.id} className="py-3 flex justify-between items-center first:pt-0 last:pb-0">
                  <div className="space-y-1">
                    <Link
                      to={`/projects/${proj.id}`}
                      className="text-sm font-bold text-gray-800 dark:text-gray-100 hover:text-primary-600 dark:hover:text-primary-400"
                    >
                      {proj.name}
                    </Link>
                    <p className="text-xs text-gray-500 truncate max-w-[200px]">
                      {proj.description || 'No description provided.'}
                    </p>
                  </div>
                  <Link
                    to={`/projects/${proj.id}`}
                    className="text-xs font-semibold text-primary-600 hover:text-primary-750"
                  >
                    View
                  </Link>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Recent reviews conducted */}
        <Card className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-md font-bold text-gray-900 dark:text-white">Recent Reviews</h3>
              <p className="text-xs text-gray-550">Audit trails and checker outputs</p>
            </div>
            <Link to="/reviews" className="text-xs font-bold text-primary-600 hover:text-primary-700">
              View All
            </Link>
          </div>
          <div className="divide-y divide-gray-150 dark:divide-gray-700/80">
            {loadingReviews ? (
              <div className="animate-pulse space-y-4 py-3">
                <div className="h-4 bg-gray-250 dark:bg-gray-700 rounded w-5/6"></div>
                <div className="h-4 bg-gray-250 dark:bg-gray-700 rounded w-2/3"></div>
              </div>
            ) : reviews.length === 0 ? (
              <p className="text-xs text-gray-400 italic py-4">No reviews executed yet. Submit files to analyze.</p>
            ) : (
              reviews.map((rev) => (
                <div key={rev.id} className="py-3 flex justify-between items-center first:pt-0 last:pb-0">
                  <div className="flex items-center space-x-3">
                    <Badge
                      variant={
                        rev.status === 'completed'
                          ? 'success'
                          : rev.status === 'failed'
                          ? 'danger'
                          : 'warning'
                      }
                    >
                      {rev.status}
                    </Badge>
                    <div className="space-y-0.5">
                      <Link
                        to={`/reviews/${rev.id}`}
                        className="text-sm font-bold text-gray-800 dark:text-gray-100 hover:text-primary-600"
                      >
                        Review #{rev.id}
                      </Link>
                      <p className="text-xs text-gray-500">
                        {rev.created_at ? new Date(rev.created_at).toLocaleString() : 'Just now'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {rev.pylint_score !== null && (
                      <span className="text-xs font-bold text-gray-600 dark:text-gray-400">
                        Pylint: {rev.pylint_score}/10
                      </span>
                    )}
                    <Link
                      to={`/reviews/${rev.id}`}
                      className="text-xs font-bold text-primary-600 hover:text-primary-750"
                    >
                      Report
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
