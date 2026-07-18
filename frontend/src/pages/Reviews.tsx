import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listReviews } from '../services/reviews.ts';
import { Badge } from '../components/ui/Badge.tsx';
import { Button } from '../components/common/Button.tsx';
import Table from '../components/ui/Table.tsx';

export const Reviews: React.FC = () => {
  const [page, setPage] = useState(1);
  const [projectIdFilter, setProjectIdFilter] = useState<number | undefined>(undefined);

  // Load reviews list
  const { data: reviewsData, isLoading } = useQuery({
    queryKey: ['reviews', { page, project_id: projectIdFilter }],
    queryFn: () =>
      listReviews({
        page,
        page_size: 10,
        project_id: projectIdFilter,
      }),
  });

  const reviews = reviewsData?.data?.items || [];
  const pagination = reviewsData?.data?.pagination;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            Code Review Audit Trail
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse and review static checks and automated LLM suggestions across code versions.
          </p>
        </div>
      </div>

      {/* Filter toolbar */}
      <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-gray-400 uppercase">Filter Project ID:</span>
          <input
            type="number"
            placeholder="e.g. 1"
            className="w-24 p-1.5 border border-gray-250 dark:border-gray-700 dark:bg-gray-900 rounded-md text-xs focus:outline-none dark:text-white font-mono"
            value={projectIdFilter || ''}
            onChange={(e) => {
              const val = parseInt(e.target.value);
              setProjectIdFilter(isNaN(val) ? undefined : val);
              setPage(1);
            }}
          />
          {projectIdFilter !== undefined && (
            <button
              onClick={() => {
                setProjectIdFilter(undefined);
                setPage(1);
              }}
              className="text-xs text-rose-500 font-semibold"
            >
              Clear
            </button>
          )}
        </div>
        <span className="text-xs font-semibold text-gray-400">
          Showing {reviews.length} of {pagination?.total_items || reviews.length} runs
        </span>
      </div>

      {/* Table grid listing */}
      <Table
        data={reviews}
        loading={isLoading}
        keyExtractor={(row) => row.id}
        emptyMessage="No review sessions found. Set project filters or trigger new checks from a project detail page."
        columns={[
          {
            header: 'Run ID',
            accessor: (row) => <span className="font-mono font-bold text-gray-650">#{row.id}</span>,
          },
          {
            header: 'Project ID',
            accessor: (row) => (
              <Link
                to={`/projects/${row.project_id}`}
                className="font-bold text-primary-600 hover:text-primary-750 font-mono"
              >
                #{row.project_id}
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
            header: 'Pylint score',
            accessor: (row) => (row.pylint_score !== null ? `${row.pylint_score.toFixed(1)} / 10` : 'N/A'),
          },
          {
            header: 'Bandit findings',
            accessor: (row) => (row.bandit_issues_count !== null ? `${row.bandit_issues_count} warnings` : 'N/A'),
          },
          {
            header: 'Radon score',
            accessor: (row) => (row.radon_mi_score !== null ? `${row.radon_mi_score.toFixed(1)}` : 'N/A'),
          },
          {
            header: 'AI Suggestions',
            accessor: (row) => (
              <Badge variant={row.ai_review_completed ? 'success' : 'secondary'}>
                {row.ai_review_completed ? 'Completed' : 'Pending'}
              </Badge>
            ),
          },
          {
            header: 'Details',
            accessor: (row) => (
              <Link
                to={`/reviews/${row.id}`}
                className="text-xs font-bold text-primary-600 hover:text-primary-750"
              >
                View Report →
              </Link>
            ),
          },
        ]}
      />

      {/* Pagination controls */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center items-center space-x-2 pt-4">
          <Button
            variant="secondary"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1 text-xs"
          >
            Previous
          </Button>
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Page {page} of {pagination.total_pages}
          </span>
          <Button
            variant="secondary"
            disabled={page === pagination.total_pages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1 text-xs"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

export default Reviews;
