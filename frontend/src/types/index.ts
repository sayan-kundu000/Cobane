export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
}

export interface ReviewFinding {
  type: string;
  file: string;
  line: number;
  comment: string;
  suggestion?: string;
}
