import React, { useState, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  getProject,
  getProjectStats,
  listProjectSources,
  getProjectSourceContent,
  updateProjectSourceContent,
  runProjectSource,
  deleteProjectSource,
} from '../services/projects.ts';
import { listReviews, createReview, deleteReview } from '../services/reviews.ts';
import Card from '../components/ui/Card.tsx';
import Badge from '../components/ui/Badge.tsx';
import { Button } from '../components/common/Button.tsx';
import Table from '../components/ui/Table.tsx';
import UploadZone from '../components/upload/UploadZone.tsx';
import SnippetEditor from '../components/upload/SnippetEditor.tsx';
import MonacoWrapper from '../components/monaco/MonacoWrapper.tsx';
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

  // Load project uploaded sources dynamically from the database
  const { data: sourcesRes, isLoading: loadingSources } = useQuery({
    queryKey: ['project-sources', projectId],
    queryFn: () => listProjectSources(projectId),
    enabled: projectId > 0,
  });
  const uploadedFiles = sourcesRes?.data || [];

  const [selectedSourceId, setSelectedSourceId] = useState<number | null>(null);
  const [editorContent, setEditorContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectedRange, setSelectedRange] = useState<{ startLine: number; endLine: number } | null>(null);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const [runOutput, setRunOutput] = useState<{ stdout: string; stderr: string; exitCode: number | null } | null>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);

  // Fetch individual file content when a file is selected
  const { data: fileContentRes, isLoading: loadingFileContent } = useQuery({
    queryKey: ['source-content', projectId, selectedSourceId],
    queryFn: () => getProjectSourceContent(projectId, selectedSourceId!),
    enabled: projectId > 0 && selectedSourceId !== null,
  });

  // Sync content state when data is loaded
  React.useEffect(() => {
    if (fileContentRes?.data) {
      setEditorContent(fileContentRes.data.content);
      setOriginalContent(fileContentRes.data.content);
      setRunOutput(null);
      setSelectedText('');
      setSelectedRange(null);
    }
  }, [fileContentRes]);

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

  const handleUploadSuccess = (_newSource: any) => {
    queryClient.invalidateQueries({ queryKey: ['project-sources', projectId] });
    setActiveTab('history');
  };

  const handleSaveContent = async () => {
    if (!selectedSourceId) return;
    try {
      setSaving(true);
      const res = await updateProjectSourceContent(projectId, selectedSourceId, editorContent);
      if (res.success && res.data) {
        setOriginalContent(res.data.content);
        toast.success('File saved successfully!');
        queryClient.invalidateQueries({ queryKey: ['project-sources', projectId] });
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Failed to save changes.');
    } finally {
      setSaving(false);
    }
  };

  const handleRunCode = async () => {
    if (!selectedSourceId) return;
    try {
      setRunning(true);
      setRunOutput(null);
      toast.loading('Executing script...', { id: 'run-loader' });
      const res = await runProjectSource(projectId, selectedSourceId);
      if (res.success && res.data) {
        setRunOutput({
          stdout: res.data.stdout,
          stderr: res.data.stderr,
          exitCode: res.data.exit_code,
        });
        toast.success('Execution completed!', { id: 'run-loader' });
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Execution failed.', { id: 'run-loader' });
    } finally {
      setRunning(false);
    }
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

  const handleDeleteSource = async (sourceId: number, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    try {
      const res = await deleteProjectSource(projectId, sourceId);
      if (res.success) {
        toast.success('File deleted successfully.');
        if (selectedSourceId === sourceId) {
          setSelectedSourceId(null);
        }
        queryClient.invalidateQueries({ queryKey: ['project-sources', projectId] });
      } else {
        toast.error('Failed to delete file.');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Failed to delete file.');
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!window.confirm(`Are you sure you want to delete Review #${reviewId}?`)) {
      return;
    }
    try {
      const res = await deleteReview(reviewId);
      if (res.success) {
        toast.success('Review deleted successfully.');
        queryClient.invalidateQueries({ queryKey: ['project-reviews', projectId] });
        queryClient.invalidateQueries({ queryKey: ['project-stats', projectId] });
      } else {
        toast.error('Failed to delete review.');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Failed to delete review.');
    }
  };

  const handleApplyCode = (suggestedCode: string, mode: 'replace' | 'insert' | 'selection' = 'replace') => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) {
      setEditorContent(suggestedCode);
      toast.success('Code applied to editor!');
      return;
    }

    if (mode === 'selection') {
      const selection = editor.getSelection();
      if (selection && !selection.isEmpty()) {
        const range = new monaco.Range(
          selection.startLineNumber,
          selection.startColumn,
          selection.endLineNumber,
          selection.endColumn
        );
        const op = { identifier: { major: 1, minor: 1 }, range: range, text: suggestedCode, forceMoveMarkers: true };
        editor.executeEdits("chatbot-apply", [op]);
        toast.success('Replaced selection with suggestion!');
      } else {
        toast.error('No selection found in editor.');
      }
    } else if (mode === 'insert') {
      const position = editor.getPosition();
      if (position) {
        const range = new monaco.Range(
          position.lineNumber,
          position.column,
          position.lineNumber,
          position.column
        );
        const op = { identifier: { major: 1, minor: 1 }, range: range, text: suggestedCode, forceMoveMarkers: true };
        editor.executeEdits("chatbot-apply", [op]);
        toast.success('Inserted suggestion at cursor!');
      } else {
        toast.error('No cursor position found.');
      }
    } else {
      const model = editor.getModel();
      if (model) {
        model.setValue(suggestedCode);
        toast.success('File content updated with suggestion!');
      } else {
        setEditorContent(suggestedCode);
        toast.success('File content updated!');
      }
    }
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
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[500px]">
              {/* Left pane: File list sidebar */}
              <div className="lg:col-span-3 border-r border-gray-200 dark:border-gray-700/80 pr-4 space-y-3">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Workspace Files</h3>
                {loadingSources ? (
                  <div className="text-xs text-gray-450">Loading files...</div>
                ) : uploadedFiles.length === 0 ? (
                  <div className="text-xs text-gray-450 italic p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    No files uploaded yet. Go to Upload Files or Snippet Editor to add code.
                  </div>
                ) : (
                  <div className="flex flex-col space-y-1.5 animate-fadeIn">
                    {uploadedFiles.map((file: any) => (
                      <div
                        key={file.id}
                        className={`group flex items-center justify-between px-3 py-1 rounded-xl border transition-all ${
                          selectedSourceId === file.id
                            ? 'bg-primary-600 border-primary-600 text-white shadow-sm'
                            : 'bg-white dark:bg-gray-800 border-gray-250 dark:border-gray-700/80 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        <button
                          onClick={() => {
                            setSelectedSourceId(file.id);
                          }}
                          className="flex-1 text-left font-semibold font-mono text-xs truncate mr-2 flex items-center justify-between py-1.5"
                        >
                          <span className="truncate">📄 {file.filename}</span>
                          <Badge
                            variant={selectedSourceId === file.id ? 'primary' : 'secondary'}
                            className="text-[10px] ml-2 shrink-0"
                          >
                            {file.language}
                          </Badge>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteSource(file.id, file.filename);
                          }}
                          title="Delete file"
                          className={`p-1.5 rounded-lg hover:bg-rose-600 hover:text-white dark:hover:bg-rose-700 transition-colors ml-1 ${
                            selectedSourceId === file.id
                              ? 'text-white hover:bg-primary-700'
                              : 'text-rose-500 hover:text-white'
                          }`}
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right pane: Editor, Run, and Review controls */}
              <div className="lg:col-span-9 flex flex-col space-y-4">
                {selectedSourceId === null ? (
                  <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-2xl p-12 text-center">
                    <span className="text-4xl mb-4">💻</span>
                    <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200">No File Selected</h3>
                    <p className="text-xs text-gray-555 max-w-xs mt-1">
                      Choose a source file from the workspace file list on the left to view, edit, execute, or trigger static analysis.
                    </p>
                  </div>
                ) : loadingFileContent ? (
                  <div className="flex-1 flex items-center justify-center h-64">
                    <svg className="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                ) : fileContentRes?.data ? (
                  <div className="flex flex-col flex-1 space-y-4 animate-fadeIn">
                    {/* File editor control header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-3 rounded-xl gap-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-gray-700 dark:text-gray-300">
                          {fileContentRes.data.filename}
                        </span>
                        {editorContent !== originalContent && (
                          <span className="text-[10px] bg-amber-100 dark:bg-amber-955/35 text-amber-800 dark:text-amber-300 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse">
                            Unsaved Changes
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-2 self-end sm:self-auto">
                        <Button
                          variant="secondary"
                          onClick={handleSaveContent}
                          disabled={saving || editorContent === originalContent}
                          className="text-xs px-3 py-1.5 font-semibold flex items-center space-x-1"
                        >
                          {saving ? 'Saving...' : '💾 Save'}
                        </Button>

                        {fileContentRes.data.language === 'python' ? (
                          <Button
                            variant="primary"
                            onClick={handleRunCode}
                            disabled={running}
                            className="text-xs px-3 py-1.5 font-semibold flex items-center space-x-1 bg-emerald-600 hover:bg-emerald-700 border-emerald-600 hover:border-emerald-700 text-white"
                          >
                            {running ? 'Running...' : '▶ Run Code'}
                          </Button>
                        ) : (
                          <span className="text-[10px] text-gray-400 dark:text-gray-500 italic px-2">
                            Only Python files are executable
                          </span>
                        )}

                        <Button
                          variant="primary"
                          onClick={() => handleTriggerReview(fileContentRes.data.id)}
                          disabled={reviewMutation.isPending}
                          className="text-xs px-3 py-1.5 font-semibold flex items-center space-x-1"
                        >
                          🔎 Review Code
                        </Button>
                      </div>
                    </div>

                    {/* Monaco Editor Container */}
                    <div className="border border-gray-250 dark:border-gray-700/80 rounded-2xl overflow-hidden shadow-sm h-[400px]">
                      <MonacoWrapper
                        code={editorContent}
                        language={fileContentRes.data.language}
                        onChange={(val) => setEditorContent(val || '')}
                        onSelectionChange={(text, startLine, endLine) => {
                          setSelectedText(text);
                          setSelectedRange(startLine > 0 ? { startLine, endLine } : null);
                        }}
                        editorRef={editorRef}
                        onEditorMount={(_editor, monaco) => {
                          monacoRef.current = monaco;
                        }}
                      />
                    </div>

                    {/* Console Output Block */}
                    {runOutput && (
                      <div className="border border-gray-250 dark:border-gray-700/80 rounded-2xl overflow-hidden shadow-sm flex flex-col bg-gray-950">
                        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-900">
                          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">
                            Console Terminal / Execution Output
                          </span>
                          <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded ${
                            runOutput.exitCode === 0
                              ? 'bg-emerald-950/40 text-emerald-400'
                              : 'bg-rose-955/40 text-rose-455'
                          }`}>
                            Exit Code: {runOutput.exitCode}
                          </span>
                        </div>
                        <pre className="p-4 text-xs font-mono text-gray-100 overflow-auto max-h-[180px] whitespace-pre-wrap">
                          {runOutput.stdout && (
                            <span className="text-gray-200">{runOutput.stdout}</span>
                          )}
                          {runOutput.stderr && (
                            <span className="text-rose-400">{runOutput.stderr}</span>
                          )}
                          {!runOutput.stdout && !runOutput.stderr && (
                            <span className="text-gray-550 italic">[Process completed with no output]</span>
                          )}
                        </pre>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-xs text-gray-450 italic">Error loading file content.</div>
                )}
              </div>
            </div>
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
                    <div className="flex items-center space-x-3">
                      <Link
                        to={`/reviews/${row.id}`}
                        className="text-xs font-semibold text-primary-600 hover:text-primary-750"
                      >
                        Report Summary →
                      </Link>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          handleDeleteReview(row.id);
                        }}
                        title="Delete review log"
                        className="text-xs font-semibold text-rose-500 hover:text-rose-700 transition-colors p-1 rounded-md hover:bg-rose-50 dark:hover:bg-rose-955/20"
                      >
                        Delete 🗑️
                      </button>
                    </div>
                  ),
                },
              ]}
            />
          )}

          {activeTab === 'chat' && (
            selectedSourceId !== null && fileContentRes?.data ? (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start min-h-[500px]">
                {/* Left side: Monaco Editor */}
                <div className="lg:col-span-6 space-y-4">
                  <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl p-4 shadow-sm space-y-3">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-gray-700 dark:text-gray-300">
                          📄 {fileContentRes.data.filename}
                        </span>
                        {editorContent !== originalContent && (
                          <span className="text-[10px] bg-amber-100 dark:bg-amber-955/35 text-amber-800 dark:text-amber-300 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider animate-pulse font-sans">
                            Unsaved Changes
                          </span>
                        )}
                      </div>
                      <Button
                        variant="secondary"
                        onClick={handleSaveContent}
                        disabled={saving || editorContent === originalContent}
                        className="text-[10px] px-2 py-1 font-semibold"
                      >
                        {saving ? 'Saving...' : '💾 Save'}
                      </Button>
                    </div>
                    <div className="h-[480px]">
                      <MonacoWrapper
                        code={editorContent}
                        language={fileContentRes.data.language}
                        onChange={(val) => setEditorContent(val || '')}
                        onSelectionChange={(text, startLine, endLine) => {
                          setSelectedText(text);
                          setSelectedRange(startLine > 0 ? { startLine, endLine } : null);
                        }}
                        editorRef={editorRef}
                        onEditorMount={(_editor, monaco) => {
                          monacoRef.current = monaco;
                        }}
                      />
                    </div>
                  </div>
                </div>
                {/* Right side: Chatbot */}
                <div className="lg:col-span-6">
                  <Chatbot
                    projectId={projectId}
                    selectedCode={selectedText}
                    selectionStartLine={selectedRange?.startLine}
                    selectionEndLine={selectedRange?.endLine}
                    editorCode={editorContent}
                    filename={fileContentRes.data.filename}
                    onApplyCode={handleApplyCode}
                    isReadOnly={false}
                  />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[500px]">
                {/* No active file: Show workspace chatbot & help card */}
                <div className="lg:col-span-4 bg-gray-50 dark:bg-gray-900/50 p-6 rounded-2xl border border-gray-250 dark:border-gray-800 flex flex-col justify-center text-center">
                  <span className="text-3xl mb-3">💬</span>
                  <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200">Connected Code Chat</h3>
                  <p className="text-xs text-gray-500 mt-2 leading-relaxed font-medium">
                    Select a source file in the <span className="font-semibold text-primary-600 hover:underline cursor-pointer" onClick={() => setActiveTab('history')}>Code Files</span> tab to open a side-by-side split screen where you can ask context-aware questions, make selections, and directly apply suggestions!
                  </p>
                </div>
                <div className="lg:col-span-8">
                  <Chatbot projectId={projectId} />
                </div>
              </div>
            )
          )}
        </div>
      </Card>
    </div>
  );
};

export default ProjectDetail;
