import api from './api.ts';
import { ApiResponse } from '../types';

export interface CheckerConfig {
  enabled: boolean;
  [key: string]: any;
}

export interface StaticAnalysisConfig {
  checkers: {
    pylint: CheckerConfig;
    bandit: CheckerConfig;
    radon: CheckerConfig;
  };
}

export const getStaticAnalysisConfig = async (): Promise<ApiResponse<StaticAnalysisConfig>> => {
  const response = await api.get('/static-analysis/config');
  return response.data;
};
