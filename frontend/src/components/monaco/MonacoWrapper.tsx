import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { useTheme } from '../../hooks/useTheme.ts';

interface MonacoWrapperProps {
  code: string;
  language?: string;
  onChange?: (val: string | undefined) => void;
  readOnly?: boolean;
  height?: string;
  selectedLine?: number | null;
  findings?: any[];
  onSelectionChange?: (text: string, startLine: number, endLine: number) => void;
  editorRef?: React.MutableRefObject<any>;
  onEditorMount?: (editor: any, monaco: any) => void;
}

export const MonacoWrapper: React.FC<MonacoWrapperProps> = ({
  code,
  language = 'python',
  onChange,
  readOnly = false,
  height = '500px',
  selectedLine = null,
  findings = [],
  onSelectionChange,
  editorRef,
  onEditorMount,
}) => {
  const { theme } = useTheme();
  const editorInstanceRef = useRef<any>(null);
  const monacoInstanceRef = useRef<any>(null);
  const decorationsRef = useRef<string[]>([]);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorInstanceRef.current = editor;
    monacoInstanceRef.current = monaco;
    if (editorRef) {
      editorRef.current = editor;
    }
    if (onEditorMount) {
      onEditorMount(editor, monaco);
    }

    // Attach cursor selection change handler
    editor.onDidChangeCursorSelection((_e: any) => {
      const selection = editor.getSelection();
      if (selection && !selection.isEmpty()) {
        const model = editor.getModel();
        if (model) {
          const text = model.getValueInRange(selection);
          if (onSelectionChange) {
            onSelectionChange(text, selection.startLineNumber, selection.endLineNumber);
          }
        }
      } else {
        if (onSelectionChange) {
          onSelectionChange('', 0, 0);
        }
      }
    });
  };

  // Sync highlighting and decorations
  useEffect(() => {
    const editor = editorInstanceRef.current;
    if (!editor) return;

    const newDecorations: any[] = [];

    // 1. Highlight selected line
    if (selectedLine) {
      newDecorations.push({
        range: { startLineNumber: selectedLine, startColumn: 1, endLineNumber: selectedLine, endColumn: 1 },
        options: {
          isWholeLine: true,
          className: 'bg-primary-50/20 dark:bg-primary-950/25 border-y border-dashed border-primary-500/40',
          marginClassName: 'active-line-margin',
        },
      });
      editor.revealLineInCenter(selectedLine);
    }

    // 2. Add visual decorations for findings
    if (findings && findings.length > 0) {
      findings.forEach((finding) => {
        const line = finding.line_number;
        const severity = (finding.severity || '').toLowerCase();
        let className = 'border-b border-dotted border-sky-400';
        let glyphMarginClassName = 'bg-sky-500 rounded-full w-2 h-2 mx-auto my-1.5';
        let hoverMessage = `${finding.provider}: ${finding.message}`;

        if (severity === 'critical') {
          className = 'border-b-2 border-dotted border-rose-500 bg-rose-500/5';
          glyphMarginClassName = 'bg-rose-500 rounded-full w-2.5 h-2.5 mx-auto my-1 animate-pulse';
        } else if (severity === 'warning') {
          className = 'border-b-2 border-dotted border-amber-500 bg-amber-500/5';
          glyphMarginClassName = 'bg-amber-500 rounded-full w-2 h-2 mx-auto my-1.5';
        } else if (severity === 'info') {
          className = 'border-b border-dotted border-sky-400';
          glyphMarginClassName = 'bg-sky-400 rounded-full w-1.5 h-1.5 mx-auto my-1.5';
        }

        newDecorations.push({
          range: { startLineNumber: line, startColumn: 1, endLineNumber: line, endColumn: 100 },
          options: {
            isWholeLine: false,
            className: className,
            glyphMarginClassName: glyphMarginClassName,
            glyphMarginHoverMessage: { value: hoverMessage },
            hoverMessage: { value: hoverMessage },
          },
        });
      });
    }

    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);
  }, [selectedLine, findings]);

  return (
    <div className="border rounded-xl overflow-hidden border-gray-250 dark:border-gray-700/80 h-full min-h-[300px]" style={{ height }}>
      <Editor
        height="100%"
        language={language}
        theme={theme === 'dark' ? 'vs-dark' : 'light'}
        value={code}
        onChange={readOnly ? undefined : onChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          minimap: { enabled: true },
          fontSize: 14,
          fontFamily: "Fira Code, Menlo, Monaco, Consolas, 'Courier New', monospace",
          automaticLayout: true,
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          folding: true,
          renderLineHighlight: 'all',
          cursorBlinking: 'smooth',
          glyphMargin: true,
          scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            useShadows: false,
            verticalScrollbarSize: 10,
            horizontalScrollbarSize: 10,
          },
        }}
      />
    </div>
  );
};

export default MonacoWrapper;
