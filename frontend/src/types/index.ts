export interface ApiResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
  request_id: string;
  error?: string;
  message?: string;
  details?: any;
}

export interface User {
  id: number;
  email: string;
  username: string;
  is_superuser: boolean;
  is_active: boolean;
}

export interface UserProfile {
  id: number;
  user_id: number;
  full_name?: string;
  bio?: string;
  created_at?: string;
}

export interface UserPreference {
  theme: 'light' | 'dark' | 'neon';
  receiving_notifications: boolean;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
}

export interface ProjectStats {
  average_pylint_score: number;
  average_maintainability_index: number;
  total_bandit_vulnerabilities: number;
  total_reviews_conducted: number;
}

export interface UploadedSource {
  id: number;
  project_id: number;
  filename: string;
  file_path: string;
  file_size: number;
  language: string;
  sha256_hash: string;
  status: 'pending' | 'processed' | 'error';
}

export interface Review {
  id: number;
  project_id: number;
  uploaded_source_id: number;
  status: 'pending' | 'completed' | 'failed';
  pylint_score: number | null;
  radon_mi_score: number | null;
  bandit_issues_count: number | null;
  ai_review_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReviewFinding {
  id: number;
  review_id: number;
  file_path: string;
  line_number: number;
  severity: 'critical' | 'warning' | 'info' | string;
  category: string;
  message: string;
  code_snippet: string | null;
  suggestion: string | null;
  provider: 'pylint' | 'bandit' | 'ai' | string;
  created_at: string;
}

export interface ReviewMetrics {
  id: number;
  review_id: number;
  cyclomatic_complexity: number;
  maintainability_index: number;
  loc: number;
  functions_count: number;
  classes_count: number;
}

export interface Report {
  id: number;
  review_id: number;
  format: string;
  file_path: string;
  created_at: string;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: Pagination;
}
