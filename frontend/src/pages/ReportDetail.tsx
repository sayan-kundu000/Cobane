import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getReportDetails, downloadReportFile } from '../services/reports.ts';
import Card from '../components/ui/Card.tsx';
import { Button } from '../components/common/Button.tsx';
import Badge from '../components/ui/Badge.tsx';

export const ReportDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const reportId = parseInt(id || '0');

  const { data: reportRes, isLoading } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => getReportDetails(reportId),
    enabled: reportId > 0,
  });

  const report = reportRes?.data;

  const handleDownload = async () => {
    try {
      const res = await downloadReportFile(reportId);
      if (res.success && res.data) {
        toast.success(res.data.message || 'Report download started.');
        window.open(res.data.download_url, '_blank');
      }
    } catch (err) {
      toast.error('Failed to trigger report file download.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <svg className="animate-spin h-10 w-10 text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  if (!report) {
    return (
      <Card className="text-center p-12 space-y-4">
        <h2 className="text-xl font-bold text-red-500">Report Reference Not Found</h2>
        <Link to="/reports" className="text-primary-600 hover:text-primary-700 font-semibold">
          Return to reports listing
        </Link>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Navigation and Actions */}
      <div className="space-y-2">
        <Link to="/reports" className="text-xs font-bold text-gray-500 hover:text-primary-600">
          ← Back to Reports Catalog
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
                Report Document Summary
              </h1>
              <Badge variant="primary">{report.format}</Badge>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              File Location: <code className="font-mono text-xs bg-gray-100 dark:bg-gray-900 px-1 py-0.5 rounded">{report.file_path}</code>
            </p>
          </div>
          <Button onClick={handleDownload} className="font-bold">
            Download Document
          </Button>
        </div>
      </div>

      {/* Preview Section */}
      <Card className="space-y-6">
        <div>
          <h3 className="text-md font-bold text-gray-900 dark:text-white uppercase tracking-wider">
            Report Outline Preview
          </h3>
          <p className="text-xs text-gray-500">HTML rendering of export metadata parameters</p>
        </div>

        <div className="border border-gray-200 dark:border-gray-700 rounded-xl p-6 bg-gray-50 dark:bg-gray-900/40 space-y-6 max-w-3xl mx-auto">
          <div className="text-center border-b border-gray-200 dark:border-gray-700 pb-6 space-y-2">
            <h2 className="text-2xl font-black text-primary-600">COBANE — AUDIT SUMMARY REPORT</h2>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              AI Code Review Assistant Documentation
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs font-medium text-gray-700 dark:text-gray-300">
            <div>
              <span className="text-gray-400 block font-bold uppercase">Report ID</span>
              <span className="font-mono text-gray-950 dark:text-white">#{report.id}</span>
            </div>
            <div>
              <span className="text-gray-400 block font-bold uppercase">Associated Review ID</span>
              <Link to={`/reviews/${report.review_id}`} className="font-mono text-primary-600 font-bold hover:underline">
                #{report.review_id}
              </Link>
            </div>
            <div>
              <span className="text-gray-400 block font-bold uppercase">Export Format</span>
              <span className="font-mono uppercase text-gray-950 dark:text-white">{report.format}</span>
            </div>
            <div>
              <span className="text-gray-400 block font-bold uppercase">Generated Timestamp</span>
              <span className="font-mono text-gray-950 dark:text-white">
                {new Date(report.created_at || Date.now()).toUTCString()}
              </span>
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-6 space-y-3">
            <h4 className="font-bold text-sm text-gray-900 dark:text-white">Report Index Findings Summary</h4>
            <p className="text-xs text-gray-550 leading-relaxed">
              This document contains the structural quality evaluation generated for project reviews. It documents code compliance ratings, cyclomatic complexity scores, bandit static threat detections, and automated AI suggestions designed to improve runtime efficiency and style conformity.
            </p>
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 p-3 rounded-lg text-xs text-amber-800 dark:text-amber-300 flex items-center space-x-2">
              <svg className="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span><strong>Note:</strong> Download the file to view the final compiled charts.</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ReportDetail;
