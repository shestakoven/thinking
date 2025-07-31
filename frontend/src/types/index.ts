export interface ArbitrageOpportunity {
    id: string;
    token_address: string;
    source_chain: string;
    target_chain: string;
    source_price: number;
    target_price: number;
    price_difference: number;
    profit_potential: number;
    gas_estimate: number;
    net_profit: number;
    confidence_score: number;
    timestamp: string;
}

export interface ExecuteArbitrageRequest {
    opportunity_id: string;
    amount?: number;
    wallet_address?: string;
}

export interface ExecuteArbitrageResponse {
    status: string;
    opportunity_id: string;
    estimated_profit: number;
    transaction_hash?: string;
    message: string;
}

export interface User {
    id: string;
    email: string;
    wallet_address: string;
    api_key?: string;
    tier: string;
    created_at: string;
    is_active: boolean;
}

export interface UserCreateRequest {
    email: string;
    wallet_address: string;
    tier?: string;
}

export interface ApiResponse<T> {
    data: T;
    status: string;
    message?: string;
}

export interface Stats {
    totalOpportunities: number;
    totalProfitPotential: number;
    bestOpportunity: number;
    averageConfidence: number;
}

export interface ChainInfo {
    name: string;
    symbol: string;
    gasPrice: number;
    enabled: boolean;
}