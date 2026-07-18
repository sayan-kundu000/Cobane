import React from 'react';
import Editor from '@monaco-editor/react';
import { useTheme } from '../../hooks/useTheme.ts';

interface MonacoWrapperProps {
  code: string;
  language?: string;
  onChange?: (val: string | undefined) => void;
  readOnly?: boolean;
  height?: string;
  lineDecorations?: any[]; // For potential custom decorations
}

export const MonacoWrapper: React.FC<MonacoWrapperProps> = ({
  code,
  language = 'python',
  onChange,
  readOnly = false,
  height = '500px',
}) => {
  const { theme } = useTheme();

  return (
    <div className="border rounded-xl overflow-hidden border-gray-250 dark:border-gray-700/80 h-full min-h-[300px]" style={{ height }}>
      <Editor
        height="100%"
        language={language}
        theme={theme === 'dark' ? 'vs-dark' : 'light'}
        value={code}
        onChange={readOnly ? undefined : onChange}
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
