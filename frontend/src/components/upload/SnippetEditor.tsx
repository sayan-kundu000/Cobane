import React, { useState } from 'react';
import toast from 'react-hot-toast';
import MonacoWrapper from '../monaco/MonacoWrapper.tsx';
import { Button } from '../common/Button.tsx';
import { Input } from '../common/Input.tsx';
import { uploadProjectFile } from '../../services/projects.ts';

interface SnippetEditorProps {
  projectId: number;
  onUploadSuccess: (source: any) => void;
}

export const SnippetEditor: React.FC<SnippetEditorProps> = ({ projectId, onUploadSuccess }) => {
  const [filename, setFilename] = useState('snippet.py');
  const [code, setCode] = useState('def calculate_sum(a, b):\n    # TODO: Add safety validations\n    assert a is not None\n    return a + b\n');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!filename.trim()) {
      toast.error('File name is required.');
      return;
    }
    if (!code.trim()) {
      toast.error('Code body cannot be blank.');
      return;
    }

    try {
      setSaving(true);

      // Create a virtual file using Blob
      const blob = new Blob([code], { type: 'text/plain' });
      const file = new File([blob], filename, { type: 'text/plain' });

      const res = await uploadProjectFile(projectId, file);

      if (res.success && res.data) {
        toast.success(`Successfully saved snippet as: ${filename}`);
        onUploadSuccess(res.data);
      } else {
        throw new Error(res.message || 'Snippet creation failed');
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.message || err.message || 'Failed to save code snippet.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-end space-y-3 sm:space-y-0 sm:space-x-4">
        <div className="flex-1">
          <Input
            label="Snippet Name"
            type="text"
            value={filename}
            onChange={(e: any) => setFilename(e.target.value)}
            placeholder="snippet.py"
          />
        </div>
        <Button
          onClick={handleSave}
          disabled={saving}
          className="w-full sm:w-auto h-10 px-6 font-semibold"
        >
          {saving ? 'Saving...' : 'Review Snippet'}
        </Button>
      </div>

      <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden shadow-sm">
        <MonacoWrapper
          code={code}
          language={filename.endsWith('.js') ? 'javascript' : filename.endsWith('.ts') ? 'typescript' : 'python'}
          onChange={(val) => setCode(val || '')}
        />
      </div>
    </div>
  );
};

export default SnippetEditor;
