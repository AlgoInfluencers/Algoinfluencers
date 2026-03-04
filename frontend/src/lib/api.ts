import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper functions for common API calls
export const api = {
    network: {
        getGraph: () => apiClient.get('/api/network/'),
        getInfluencers: (limit?: number) => apiClient.get('/api/network/influencers', { params: { limit } }),
        getStats: () => apiClient.get('/api/network/stats'),
    },
    simulation: {
        run: (payload: any) => apiClient.post('/api/simulation/run', payload),
    },
    predict: {
        viralProbability: (payload: any) => apiClient.post('/api/predict/', payload),
    },
};

export default apiClient;
