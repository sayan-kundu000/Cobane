import React, { useState, useRef } from 'react';
import toast from 'react-hot-toast';
import { uploadProjectFile } from '../../services/projects.ts';

interface UploadZoneProps {
  projectId: number;
  onUploadSuccess: (source: any) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ projectId, onUploadSuccess }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const validateAndUpload = async (file: File) => {
    // Basic validation
    const allowedExtensions = ['.py', '.zip', '.txt', '.js', '.ts', '.tsx', '.jsx', '.json'];
    const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedExtensions.includes(extension)) {
      toast.error(`Invalid file format: ${file.name}. Supported formats: ${allowedExtensions.join(', ')}`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('File size exceeds the 10MB threshold limit.');
      return;
    }

    try {
      setUploading(true);
      setProgress(25);
      
      // Simulate progress updates for a smoother visual experience
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 15;
        });
      }, 200);

      const res = await uploadProjectFile(projectId, file);
      
      clearInterval(interval);
      setProgress(100);

      if (res.success && res.data) {
        toast.success(`Successfully uploaded codebase resource: ${file.name}`);
        onUploadSuccess(res.data);
      } else {
        throw new Error(res.message || 'File upload failed');
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.message || err.message || 'Failed to upload project code.');
    } finally {
      setTimeout(() => {
        setUploading(false);
        setProgress(0);
      }, 500);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await validateAndUpload(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 min-h-[220px] ${
          isDragActive
            ? 'border-primary-500 bg-primary-50/40 dark:bg-primary-950/20'
            : 'border-gray-300 dark:border-gray-700 hover:border-primary-400 dark:hover:border-primary-600 bg-gray-50 dark:bg-gray-900/10'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInput}
          className="hidden"
          accept=".py,.zip,.txt,.js,.ts,.tsx,.jsx,.json"
        />

        {uploading ? (
          <div className="w-full max-w-xs space-y-4 text-center">
            <svg className="animate-spin h-10 w-10 text-primary-600 mx-auto" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div className="space-y-1">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Uploading file assets... {progress}%
              </span>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-200"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3 text-center">
            <div className="p-4 bg-primary-50 dark:bg-primary-950/20 text-primary-600 dark:text-primary-400 rounded-full inline-block">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-gray-750 dark:text-gray-300">
                Drag and drop your code files or click to browse
              </p>
              <p className="text-xs text-gray-550 dark:text-gray-400 mt-1">
                Supports single scripts (.py, .js, .ts) or compressed project archives (.zip) up to 10MB
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadZone;
