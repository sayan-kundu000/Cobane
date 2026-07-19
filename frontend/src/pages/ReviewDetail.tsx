import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getReview, getReviewFindings, getReviewMetrics, getReviewReports, getReviewCodeContent } from '../services/reviews.ts';
import { downloadReportFile } from '../services/reports.ts';
import Card from '../components/ui/Card.tsx';
import Badge from '../components/ui/Badge.tsx';
import { Button } from '../components/common/Button.tsx';
import MonacoWrapper from '../components/monaco/MonacoWrapper.tsx';
import { Chatbot } from '../components/common/Chatbot.tsx';

type FilterSeverity = 'all' | 'critical' | 'warning' | 'info';

export const ReviewDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const reviewId = parseInt(id || '0');
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectedRange, setSelectedRange] = useState<{ startLine: number; endLine: number } | null>(null);
  const [severityFilter, setSeverityFilter] = useState<FilterSeverity>('all');
  const [activePanel, setActivePanel] = useState<'findings' | 'metrics' | 'reports' | 'chat'>('findings');

  // Queries
  const { data: reviewRes, isLoading: loadingReview } = useQuery({
    queryKey: ['review', reviewId],
    queryFn: () => getReview(reviewId),
    enabled: reviewId > 0,
  });

  const { data: findingsRes, isLoading: loadingFindings } = useQuery({
    queryKey: ['review-findings', reviewId],
    queryFn: () => getReviewFindings(reviewId),
    enabled: reviewId > 0,
  });

  const { data: metricsRes, isLoading: loadingMetrics } = useQuery({
    queryKey: ['review-metrics', reviewId],
    queryFn: () => getReviewMetrics(reviewId),
    enabled: reviewId > 0,
  });

  const { data: reportsRes, isLoading: loadingReports } = useQuery({
    queryKey: ['review-reports', reviewId],
    queryFn: () => getReviewReports(reviewId),
    enabled: reviewId > 0,
  });

  const { data: codeRes } = useQuery({
    queryKey: ['review-code', reviewId],
    queryFn: () => getReviewCodeContent(reviewId),
    enabled: reviewId > 0,
  });

  const review = reviewRes?.data;
  const findings = findingsRes?.data || [];
  const metrics = metricsRes?.data;
  const reports = reportsRes?.data || [];
  const codeData = codeRes?.data;

  // Filter findings
  const filteredFindings = findings.filter((f) => {
    if (severityFilter === 'all') return true;
    return f.severity.toLowerCase() === severityFilter;
  });

  const handleDownloadReport = async (reportId: number) => {
    try {
      const res = await downloadReportFile(reportId);
      if (res.success && res.data) {
        toast.success(res.data.message || 'Report download started.');
        // Stub: trigger file save
        window.open(res.data.download_url, '_blank');
      }
    } catch (err: any) {
      toast.error('Failed to trigger report document download.');
    }
  };

  const handleFindingClick = (lineNum: number) => {
    setSelectedLine(lineNum);
    toast(`Focused line number ${lineNum} inside code editor.`, { icon: '🔍' });
  };

  if (loadingReview) {
    return (
      <div className="flex justify-center items-center h-64">
        <svg className="animate-spin h-10 w-10 text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  if (!review) {
    return (
      <Card className="text-center p-12 space-y-4">
        <h2 className="text-xl font-bold text-red-500">Review Run Session Not Found</h2>
        <Link to="/reviews" className="text-primary-600 hover:text-primary-700 font-semibold">
          Return to reviews listing
        </Link>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Navigation header */}
      <div className="space-y-2">
        <Link to={`/projects/${review.project_id}`} className="text-xs font-bold text-gray-500 hover:text-primary-600">
          ← Back to Project Details
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
                Review Run #{review.id}
              </h1>
              <Badge variant="success">Completed</Badge>
            </div>
            <p className="text-sm text-gray-500">
              Run completed at {new Date(review.created_at || Date.now()).toLocaleString()}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {review.pylint_score !== null && (
              <div className="px-3 py-1.5 bg-primary-50 dark:bg-primary-950/20 border border-primary-200 dark:border-primary-900 text-primary-600 dark:text-primary-400 rounded-lg text-xs font-bold font-mono">
                Pylint: {review.pylint_score}/10
              </div>
            )}
            {review.radon_mi_score !== null && (
              <div className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900 text-emerald-600 dark:text-emerald-400 rounded-lg text-xs font-bold font-mono">
                Maintainability: {review.radon_mi_score.toFixed(1)}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main split details view layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Editor columns - left 7 columns */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-gray-400 uppercase font-mono">
                Code View: {codeData?.filename || 'source_code'}
              </span>
              <span className="text-xs text-gray-555 dark:text-gray-400 font-medium">Read-Only review mode</span>
            </div>
            <div className="h-[550px]">
              <MonacoWrapper
                code={codeData?.content || ''}
                language={codeData?.language || 'python'}
                readOnly
                selectedLine={selectedLine}
                findings={findings}
                onSelectionChange={(text, startLine, endLine) => {
                  setSelectedText(text);
                  setSelectedRange(startLine > 0 ? { startLine, endLine } : null);
                }}
              />
            </div>
          </div>
        </div>

        {/* Audit feedback tabs panel - right 5 columns */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl p-2 shadow-sm flex space-x-1">
            <button
              onClick={() => setActivePanel('findings')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-xl transition ${
                activePanel === 'findings'
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Findings ({findings.length})
            </button>
            <button
              onClick={() => setActivePanel('metrics')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-xl transition ${
                activePanel === 'metrics'
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Radon metrics
            </button>
            <button
              onClick={() => setActivePanel('chat')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-xl transition ${
                activePanel === 'chat'
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Ask AI
            </button>
            <button
              onClick={() => setActivePanel('reports')}
              className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-xl transition ${
                activePanel === 'reports'
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Export
            </button>
          </div>

          {/* Panel content areas */}
          {activePanel === 'findings' && (
            <div className="space-y-4">
              {/* Findings filters */}
              <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 p-4 rounded-2xl flex items-center space-x-2">
                <span className="text-xs font-bold text-gray-400 uppercase">Severity:</span>
                {(['all', 'critical', 'warning', 'info'] as FilterSeverity[]).map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setSeverityFilter(sev)}
                    className={`px-2.5 py-1 text-xs rounded-md font-bold transition uppercase ${
                      severityFilter === sev
                        ? 'bg-primary-50 text-primary-700 border border-primary-200 dark:bg-primary-950 dark:text-primary-300'
                        : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-350'
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>

              {/* Scrollable list */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                {loadingFindings ? (
                  <div className="text-center py-6 text-gray-500 italic">Syncing findings...</div>
                ) : filteredFindings.length === 0 ? (
                  <Card className="text-center text-gray-500 italic text-xs py-8">
                    No code analyzer warnings reported for this severity level.
                  </Card>
                ) : (
                  filteredFindings.map((find) => (
                    <Card
                      key={find.id}
                      hoverable
                      onClick={() => handleFindingClick(find.line_number)}
                      className={`cursor-pointer border-l-4 transition-all ${
                        selectedLine === find.line_number
                          ? 'border-l-primary-500 bg-primary-50/10 dark:bg-primary-950/10 shadow-sm'
                          : find.severity.toLowerCase() === 'critical'
                          ? 'border-l-rose-500'
                          : find.severity.toLowerCase() === 'warning'
                          ? 'border-l-amber-500'
                          : 'border-l-sky-500'
                      }`}
                    >
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <Badge
                            variant={
                              find.severity.toLowerCase() === 'critical'
                                ? 'danger'
                                : find.severity.toLowerCase() === 'warning'
                                ? 'warning'
                                : 'info'
                            }
                          >
                            {find.provider}: {find.severity}
                          </Badge>
                          <span className="text-xs font-semibold font-mono text-gray-400">
                            Line {find.line_number}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-gray-900 dark:text-white leading-snug">
                          {find.message}
                        </h4>
                        {find.code_snippet && (
                          <pre className="p-2 bg-gray-50 dark:bg-gray-900 rounded text-xs font-mono overflow-x-auto text-gray-700 dark:text-gray-300">
                            {find.code_snippet}
                          </pre>
                        )}
                        {find.suggestion && (
                          <div className="text-xs text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 p-2.5 rounded border border-emerald-100 dark:border-emerald-950 font-medium">
                            <strong>Fix:</strong> {find.suggestion}
                          </div>
                        )}
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {activePanel === 'chat' && (
            <Chatbot
              reviewId={reviewId}
              selectedCode={selectedText}
              selectionStartLine={selectedRange?.startLine}
              selectionEndLine={selectedRange?.endLine}
              editorCode={codeData?.content || ''}
              filename={codeData?.filename || ''}
              isReadOnly={true}
            />
          )}

          {activePanel === 'metrics' && (
            <Card className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
                  Complexity Breakdown
                </h3>
                <p className="text-xs text-gray-500">Radon Static Metrics Summaries</p>
              </div>

              {loadingMetrics ? (
                <div className="text-gray-500 italic text-xs">Loading complexity metrics...</div>
              ) : !metrics ? (
                <p className="text-xs text-gray-500 italic">No complexity metrics records calculated.</p>
              ) : (
                <div className="grid grid-cols-2 gap-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  <div className="bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg">
                    <span className="text-xs text-gray-400 block">Lines of Code (LOC)</span>
                    <span className="text-lg font-extrabold text-gray-900 dark:text-white font-mono">
                      {metrics.loc}
                    </span>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg">
                    <span className="text-xs text-gray-400 block">Cyclomatic Complexity</span>
                    <span className="text-lg font-extrabold text-gray-900 dark:text-white font-mono">
                      {metrics.cyclomatic_complexity}
                    </span>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg">
                    <span className="text-xs text-gray-400 block">Total Functions</span>
                    <span className="text-lg font-extrabold text-gray-900 dark:text-white font-mono">
                      {metrics.functions_count}
                    </span>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg">
                    <span className="text-xs text-gray-400 block">Total Classes</span>
                    <span className="text-lg font-extrabold text-gray-900 dark:text-white font-mono">
                      {metrics.classes_count}
                    </span>
                  </div>
                </div>
              )}
            </Card>
          )}

          {activePanel === 'reports' && (
            <Card className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
                  Report Exports
                </h3>
                <p className="text-xs text-gray-500">Download static review documentation</p>
              </div>

              <div className="space-y-2">
                {loadingReports ? (
                  <div className="text-gray-500 italic text-xs">Loading report configurations...</div>
                ) : reports.length === 0 ? (
                  <p className="text-xs text-gray-500 italic">No reports registered for download.</p>
                ) : (
                  reports.map((rep) => (
                    <div
                      key={rep.id}
                      className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700/80 rounded-xl hover:border-primary-400 transition"
                    >
                      <div className="flex items-center space-x-2">
                        <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <span className="text-xs font-mono font-bold text-gray-700 dark:text-gray-300">
                          {rep.format.toUpperCase()} summary report
                        </span>
                      </div>
                      <Button
                        variant="secondary"
                        onClick={() => handleDownloadReport(rep.id)}
                        className="text-xs px-2.5 py-1 font-semibold"
                      >
                        Download
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewDetail;
