import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listReports, downloadReportFile } from '../services/reports.ts';
import Table from '../components/ui/Table.tsx';
import { Button } from '../components/common/Button.tsx';

export const Reports: React.FC = () => {
  const { data: reportsRes, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: listReports,
  });

  const reports = reportsRes?.data || [];

  const handleDownload = async (id: number) => {
    try {
      const res = await downloadReportFile(id);
      if (res.success && res.data) {
        toast.success(res.data.message || 'Report download initiated.');
        window.open(res.data.download_url, '_blank');
      }
    } catch (err) {
      toast.error('Failed to trigger report file download.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm">
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Report Export Catalog
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Access all system-generated PDF, HTML, and Markdown code audit summaries.
        </p>
      </div>

      {/* Reports Table list */}
      <Table
        data={reports}
        loading={isLoading}
        keyExtractor={(row) => row.id}
        emptyMessage="No export reports generated yet. Execute reviews on codebase archives first."
        columns={[
          {
            header: 'Report ID',
            accessor: (row) => <span className="font-mono font-bold">#{row.id}</span>,
          },
          {
            header: 'Review Run ID',
            accessor: (row) => (
              <Link
                to={`/reviews/${row.review_id}`}
                className="font-bold text-primary-600 hover:text-primary-750 font-mono"
              >
                #{row.review_id}
              </Link>
            ),
          },
          {
            header: 'Format Type',
            accessor: (row) => (
              <span className="font-bold font-mono tracking-wider text-xs uppercase px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/20 dark:text-red-300 dark:border-red-900 rounded">
                {row.format}
              </span>
            ),
          },
          {
            header: 'Disk Path Reference',
            accessor: 'file_path',
            className: 'font-mono text-xs max-w-xs truncate',
          },
          {
            header: 'Created On',
            accessor: (row) => new Date(row.created_at || Date.now()).toLocaleString(),
          },
          {
            header: 'Downloads',
            accessor: (row) => (
              <div className="flex space-x-2">
                <Button
                  variant="secondary"
                  onClick={() => handleDownload(row.id)}
                  className="text-xs px-2.5 py-1 font-semibold"
                >
                  Download File
                </Button>
                <Link
                  to={`/reports/${row.id}`}
                  className="px-3 py-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 rounded text-xs font-semibold flex items-center"
                >
                  View
                </Link>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Reports;
