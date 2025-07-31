import axios from 'axios';
import { 
    ArbitrageOpportunity, 
    ExecuteArbitrageRequest, 
    ExecuteArbitrageResponse,
    User,
    UserCreateRequest
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add API key
api.interceptors.request.use((config) => {
    const apiKey = localStorage.getItem('api_key');
    if (apiKey) {
        config.headers.Authorization = `Bearer ${apiKey}`;
    }
    return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('api_key');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const arbitrageApi = {
    // Get all arbitrage opportunities
    getOpportunities: async (): Promise<ArbitrageOpportunity[]> => {
        const response = await api.get('/api/v1/opportunities');
        return response.data;
    },

    // Get opportunities for specific token
    getTokenOpportunities: async (tokenAddress: string): Promise<ArbitrageOpportunity[]> => {
        const response = await api.get(`/api/v1/opportunities/${tokenAddress}`);
        return response.data;
    },

    // Execute arbitrage
    executeArbitrage: async (request: ExecuteArbitrageRequest): Promise<ExecuteArbitrageResponse> => {
        const response = await api.post('/api/v1/execute', request);
        return response.data;
    },
};

export const userApi = {
    // Create new user
    createUser: async (userData: UserCreateRequest): Promise<User> => {
        const response = await api.post('/api/v1/users', userData);
        return response.data;
    },

    // Get current user
    getCurrentUser: async (): Promise<User> => {
        const response = await api.get('/api/v1/users/me');
        return response.data;
    },
};

export const healthApi = {
    // Health check
    checkHealth: async () => {
        const response = await api.get('/health');
        return response.data;
    },
};

export default api;