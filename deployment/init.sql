-- Database initialization script for arbitrage platform

-- Create tables
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    id VARCHAR(255) PRIMARY KEY,
    token_address VARCHAR(42) NOT NULL,
    source_chain VARCHAR(20) NOT NULL,
    target_chain VARCHAR(20) NOT NULL,
    source_price DECIMAL(20, 8) NOT NULL,
    target_price DECIMAL(20, 8) NOT NULL,
    price_difference DECIMAL(20, 8) NOT NULL,
    profit_potential DECIMAL(20, 8) NOT NULL,
    gas_estimate DECIMAL(20, 8) NOT NULL,
    net_profit DECIMAL(20, 8) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS arbitrage_executions (
    id VARCHAR(255) PRIMARY KEY,
    opportunity_id VARCHAR(255) NOT NULL,
    executor_address VARCHAR(42) NOT NULL,
    transaction_hash VARCHAR(66),
    amount_executed DECIMAL(20, 8) NOT NULL,
    actual_profit DECIMAL(20, 8) NOT NULL,
    gas_used DECIMAL(20, 8) NOT NULL,
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS token_prices (
    id VARCHAR(255) PRIMARY KEY,
    token_address VARCHAR(42) NOT NULL,
    chain VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume_24h DECIMAL(20, 8),
    liquidity DECIMAL(20, 8),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(token_address, chain)
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_opportunities_profit ON arbitrage_opportunities(net_profit DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON arbitrage_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_created ON arbitrage_opportunities(created_at);
CREATE INDEX IF NOT EXISTS idx_executions_time ON arbitrage_executions(execution_time);
CREATE INDEX IF NOT EXISTS idx_token_prices_updated ON token_prices(updated_at);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address);

-- Insert sample data for testing
INSERT INTO arbitrage_opportunities (
    id, token_address, source_chain, target_chain, source_price, target_price,
    price_difference, profit_potential, gas_estimate, net_profit, confidence_score, expires_at
) VALUES 
('sample_1', '0xA0b86a33E6441b8c4C8C2B8c4C8C2B8c4C8C2B8c', 'ethereum', 'polygon', 1800.50, 1820.75, 20.25, 202.50, 15.00, 187.50, 0.85, NOW() + INTERVAL '1 hour'),
('sample_2', '0xdAC17F958D2ee523a2206206994597C13D831ec7', 'arbitrum', 'optimism', 0.85, 0.87, 0.02, 20.00, 8.00, 12.00, 0.72, NOW() + INTERVAL '1 hour'),
('sample_3', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'polygon', 'bsc', 45000.00, 45100.00, 100.00, 1000.00, 25.00, 975.00, 0.95, NOW() + INTERVAL '1 hour')
ON CONFLICT (id) DO NOTHING;

-- Insert sample user
INSERT INTO users (
    id, email, wallet_address, api_key, tier
) VALUES 
('user_1', 'test@example.com', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'test_api_key_123', 'pro')
ON CONFLICT (email) DO NOTHING;