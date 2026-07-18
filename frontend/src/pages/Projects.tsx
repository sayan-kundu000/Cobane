import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listProjects, createProject, deleteProject } from '../services/projects.ts';
import Card from '../components/ui/Card.tsx';
import { Button } from '../components/common/Button.tsx';
import { Input } from '../components/common/Input.tsx';
import Modal from '../components/ui/Modal.tsx';
import { Badge } from '../components/ui/Badge.tsx';

export const Projects: React.FC = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Create project form states
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');

  // Fetch projects list
  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects', { page, search }],
    queryFn: () => listProjects({ page, page_size: 6, search }),
  });

  const projects = projectsData?.data?.items || [];
  const pagination = projectsData?.data?.pagination;

  // Create Project mutation
  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Project workspace created successfully!');
        queryClient.invalidateQueries({ queryKey: ['projects'] });
        setIsModalOpen(false);
        setNewName('');
        setNewDesc('');
      } else {
        toast.error(res.message || 'Failed to create project.');
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.message || err.message || 'Error occurred.');
    }
  });

  // Delete Project mutation
  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Project workspace deleted.');
        queryClient.invalidateQueries({ queryKey: ['projects'] });
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.message || err.message || 'Failed to delete workspace.');
    }
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) {
      toast.error('Project name is required.');
      return;
    }
    createMutation.mutate({ name: newName, description: newDesc });
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to permanently delete this project workspace and all reviews?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            Workspaces & Projects
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage your codebase check roots, upload history, and report templates.
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          className="font-bold flex items-center justify-center space-x-1"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Project</span>
        </Button>
      </div>

      {/* Filters toolbar */}
      <div className="bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 p-4 rounded-xl flex flex-col sm:flex-row items-center space-y-3 sm:space-y-0 sm:space-x-4">
        <div className="w-full sm:max-w-xs">
          <Input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e: any) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div className="flex-1 flex justify-end w-full">
          <span className="text-xs font-semibold text-gray-400">
            Total Workspaces: {pagination?.total_items || projects.length}
          </span>
        </div>
      </div>

      {/* Grid listing */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse h-48 space-y-3">
              <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </Card>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="p-16 border border-gray-200 dark:border-gray-750 bg-white dark:bg-gray-800 rounded-2xl text-center text-gray-500 italic">
          No project workspaces found matching search constraints.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((proj) => (
            <Card hoverable key={proj.id} className="flex flex-col justify-between h-48">
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h3 className="font-extrabold text-lg text-gray-900 dark:text-white truncate pr-2">
                    {proj.name}
                  </h3>
                  <Badge variant="secondary">ID: {proj.id}</Badge>
                </div>
                <p className="text-xs text-gray-500 line-clamp-3 leading-relaxed">
                  {proj.description || 'No description provided.'}
                </p>
              </div>
              <div className="flex justify-between items-center border-t border-gray-100 dark:border-gray-700/80 pt-4 mt-4">
                <Link
                  to={`/projects/${proj.id}`}
                  className="text-xs font-bold text-primary-600 hover:text-primary-750"
                >
                  Manage Project →
                </Link>
                <button
                  onClick={() => handleDelete(proj.id)}
                  className="text-xs text-rose-500 hover:text-rose-700 font-bold"
                >
                  Delete
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

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

      {/* Create Project Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Project Workspace"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <Input
            label="Workspace Name"
            type="text"
            placeholder="my-python-service"
            value={newName}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewName(e.target.value)}
            required
          />
          <div className="space-y-1">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-400">
              Workspace Description
            </label>
            <textarea
              className="w-full p-3 border border-gray-250 dark:border-gray-700 dark:bg-gray-900 rounded-xl text-sm focus:ring-1 focus:ring-primary-500 focus:outline-none dark:text-white"
              rows={3}
              placeholder="Provide a brief description of the code repository and its purpose."
              value={newDesc}
              onChange={(e: any) => setNewDesc(e.target.value)}
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100 dark:border-gray-700">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Workspace'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Projects;
