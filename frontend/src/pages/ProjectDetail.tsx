import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getProject, getProjectStats } from '../services/projects.ts';
import { listReviews, createReview } from '../services/reviews.ts';
import Card from '../components/ui/Card.tsx';
import Badge from '../components/ui/Badge.tsx';
import { Button } from '../components/common/Button.tsx';
import Table from '../components/ui/Table.tsx';
import UploadZone from '../components/upload/UploadZone.tsx';
import SnippetEditor from '../components/upload/SnippetEditor.tsx';
import { Chatbot } from '../components/common/Chatbot.tsx';

type TabName = 'upload' | 'snippet' | 'history' | 'reviews' | 'chat';

export const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabName>('upload');

  // Load project metadata
  const { data: projectRes, isLoading: loadingProject } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => getProject(projectId),
    enabled: projectId > 0,
  });

  // Load project stats
  const { data: statsRes, isLoading: loadingStats } = useQuery({
    queryKey: ['project-stats', projectId],
    queryFn: () => getProjectStats(projectId),
    enabled: projectId > 0,
  });

  const { data: reviewsRes } = useQuery({
    queryKey: ['project-reviews', projectId],
    queryFn: () => listReviews({ project_id: projectId }),
    enabled: projectId > 0,
  });

  const project = projectRes?.data;
  const stats = statsRes?.data;
  const reviews = reviewsRes?.data?.items || [];

  // Temporary local state for uploaded files history (simulating server response or linking through lists)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>(() => {
    // Bootstrap from seed structure or local array
    if (projectId === 1) {
      return [
        {
          id: 1,
          filename: 'utils.py',
          file_size: 1024,
          language: 'python',
          status: 'processed',
          created_at: new Date().toISOString(),
        },
      ];
    }
    return [];
  });

  // Create review mutation
  const reviewMutation = useMutation({
    mutationFn: createReview,
    onSuccess: (res) => {
      if (res.success && res.data) {
        toast.success('Static check and AI review pipeline completed!');
        queryClient.invalidateQueries({ queryKey: ['project-reviews', projectId] });
        navigate(`/reviews/${res.data.id}`);
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.message || err.message || 'Analysis processing failed.');
    },
  });

  const handleUploadSuccess = (newSource: any) => {
    setUploadedFiles((prev) => [newSource, ...prev]);
    setActiveTab('history');
  };

  const handleTriggerReview = (sourceId: number) => {
    toast.loading('Running analyzers & calling LLM review models...', { id: 'review-loader' });
    reviewMutation.mutate(
      { project_id: projectId, uploaded_source_id: sourceId },
      {
        onSettled: () => {
          toast.dismiss('review-loader');
        },
      }
    );
  };

  if (loadingProject) {
    return (
      <div className="flex justify-center items-center h-64">
        <svg className="animate-spin h-10 w-10 text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  if (!project) {
    return (
      <Card className="text-center p-12 space-y-4">
        <h2 className="text-xl font-bold text-red-500">Project Workspace Not Found</h2>
        <Link to="/projects" className="text-primary-600 hover:text-primary-700 font-semibold">
          Return to projects listing
        </Link>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Back navigation */}
      <div className="space-y-2">
        <Link to="/projects" className="text-xs font-bold text-gray-500 hover:text-primary-600">
          ← Back to Projects
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
              {project.name}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {project.description || 'No description provided.'}
            </p>
          </div>
          <Badge variant="primary">Owner ID: {project.owner_id}</Badge>
        </div>
      </div>

      {/* Aggregate metrics dashboards cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card hoverable className="space-y-1">
          <span className="text-xs font-semibold text-gray-400 uppercase">Avg Pylint Rating</span>
          <h3 className="text-2xl font-extrabold text-gray-900 dark:text-white">
            {loadingStats ? '...' : stats ? `${stats.average_pylint_score.toFixed(1)} / 10` : 'N/A'}
          </h3>
        </Card>
        <Card hoverable className="space-y-1">
          <span className="text-xs font-semibold text-gray-400 uppercase">Maintainability Index</span>
          <h3 className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
            {loadingStats ? '...' : stats ? `${stats.average_maintainability_index.toFixed(1)}` : 'N/A'}
          </h3>
        </Card>
        <Card hoverable className="space-y-1">
          <span className="text-xs font-semibold text-gray-400 uppercase">Security Findings</span>
          <h3 className="text-2xl font-extrabold text-rose-600 dark:text-rose-455">
            {loadingStats ? '...' : stats ? `${stats.total_bandit_vulnerabilities}` : '0'}
          </h3>
        </Card>
        <Card hoverable className="space-y-1">
          <span className="text-xs font-semibold text-gray-400 uppercase">Total Review Runs</span>
          <h3 className="text-2xl font-extrabold text-primary-600 dark:text-primary-400">
            {loadingStats ? '...' : stats ? `${stats.total_reviews_conducted}` : '0'}
          </h3>
        </Card>
      </div>

      {/* File management interactive panel */}
      <Card className="space-y-6">
        {/* Tabs switcher */}
        <div className="flex border-b border-gray-200 dark:border-gray-700/80">
          {(['upload', 'snippet', 'history', 'reviews', 'chat'] as TabName[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-4 text-xs font-bold uppercase tracking-wider border-b-2 transition-all outline-none ${
                activeTab === tab
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-450 hover:text-gray-600 dark:hover:text-gray-300'
              }`}
            >
              {tab === 'upload' && 'Upload Files'}
              {tab === 'snippet' && 'Snippet Editor'}
              {tab === 'history' && `Code Files (${uploadedFiles.length})`}
              {tab === 'reviews' && `Review Runs (${reviews.length})`}
              {tab === 'chat' && 'Ask AI (Chatbot)'}
            </button>
          ))}
        </div>

        {/* Tab content screens */}
        <div className="min-h-[220px]">
          {activeTab === 'upload' && (
            <UploadZone projectId={projectId} onUploadSuccess={handleUploadSuccess} />
          )}

          {activeTab === 'snippet' && (
            <SnippetEditor projectId={projectId} onUploadSuccess={handleUploadSuccess} />
          )}

          {activeTab === 'history' && (
            <Table
              data={uploadedFiles}
              keyExtractor={(row) => row.id}
              emptyMessage="No files uploaded yet. Drag and drop source files or write snippets to check."
              columns={[
                { header: 'Filename', accessor: 'filename' },
                {
                  header: 'Size',
                  accessor: (row) =>
                    row.file_size ? `${(row.file_size / 1024).toFixed(2)} KB` : '0 KB',
                },
                {
                  header: 'Language',
                  accessor: (row) => <Badge variant="secondary">{row.language}</Badge>,
                },
                {
                  header: 'Upload Date',
                  accessor: (row) => new Date(row.created_at).toLocaleString(),
                },
                {
                  header: 'Actions',
                  accessor: (row) => (
                    <Button
                      variant="primary"
                      onClick={() => handleTriggerReview(row.id)}
                      disabled={reviewMutation.isPending}
                      className="text-xs px-3 py-1 font-semibold"
                    >
                      Trigger Review
                    </Button>
                  ),
                },
              ]}
            />
          )}

          {activeTab === 'reviews' && (
            <Table
              data={reviews}
              keyExtractor={(row) => row.id}
              emptyMessage="No review metrics conducted for this workspace."
              columns={[
                {
                  header: 'Review Run',
                  accessor: (row) => (
                    <Link
                      to={`/reviews/${row.id}`}
                      className="font-bold text-primary-600 hover:text-primary-750"
                    >
                      Review #{row.id}
                    </Link>
                  ),
                },
                {
                  header: 'Status',
                  accessor: (row) => (
                    <Badge
                      variant={
                        row.status === 'completed'
                          ? 'success'
                          : row.status === 'failed'
                          ? 'danger'
                          : 'warning'
                      }
                    >
                      {row.status}
                    </Badge>
                  ),
                },
                {
                  header: 'Pylint Score',
                  accessor: (row) => (row.pylint_score !== null ? `${row.pylint_score}/10` : 'N/A'),
                },
                {
                  header: 'Bandit Issues',
                  accessor: (row) => (row.bandit_issues_count !== null ? row.bandit_issues_count : 'N/A'),
                },
                {
                  header: 'Radon Score',
                  accessor: (row) => (row.radon_mi_score !== null ? `${row.radon_mi_score.toFixed(1)}` : 'N/A'),
                },
                {
                  header: 'AI Suggestion',
                  accessor: (row) => (
                    <Badge variant={row.ai_review_completed ? 'success' : 'secondary'}>
                      {row.ai_review_completed ? 'Completed' : 'Pending'}
                    </Badge>
                  ),
                },
                {
                  header: 'Actions',
                  accessor: (row) => (
                    <Link
                      to={`/reviews/${row.id}`}
                      className="text-xs font-semibold text-primary-600 hover:text-primary-750"
                    >
                      Report Summary →
                    </Link>
                  ),
                },
              ]}
            />
          )}

          {activeTab === 'chat' && (
            <Chatbot projectId={projectId} />
          )}
        </div>
      </Card>
    </div>
  );
};

export default ProjectDetail;
