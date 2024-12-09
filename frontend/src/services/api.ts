// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

export interface MSA {
  msas: string[];
  count: number;
}

export interface AnalysisRequest {
  msa_name: string;
  include_llm_analysis?: boolean;
}

export interface ComparisonRequest {
  base_msa: string;
  comparison_msas: string[];
}

export interface Stats {
  total_members: number;
  total_records: number;
  total_msas: number;
  total_states: number;
}

export const healthApi = {
  getMSAs: async (): Promise<MSA> => {
    const response = await api.get('/api/msas');
    return response.data;
  },

  analyzeRegion: async (request: AnalysisRequest) => {
    const response = await api.post('/api/analyze', request);
    return response.data;
  },

  compareRegions: async (request: ComparisonRequest) => {
    const response = await api.post('/api/compare', request);
    return response.data;
  },

  checkHealth: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  getStats: async (): Promise<Stats> => {
    const response = await api.get('/api/stats');
    return response.data;
  }
};