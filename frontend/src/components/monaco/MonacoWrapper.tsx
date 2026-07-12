import React from 'react';
import Editor from '@monaco-editor/react';

interface MonacoWrapperProps {
  code: string;
  language?: string;
  theme?: 'vs-dark' | 'light';
  onChange?: (val: string | undefined) => void;
}

export const MonacoWrapper: React.FC<MonacoWrapperProps> = ({
  code,
  language = 'python',
  theme = 'vs-dark',
  onChange
}) => {
  return (
    <div className="border rounded overflow-hidden dark:border-gray-700 h-[500px]">
      <Editor
        height="100%"
        language={language}
        theme={theme}
        value={code}
        onChange={onChange}
        options={{
          minimap: { enabled: true },
          fontSize: 14,
          automaticLayout: true,
        }}
      />
    </div>
  );
};
export default MonacoWrapper;
