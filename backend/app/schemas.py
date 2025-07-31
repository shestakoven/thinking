from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ArbitrageOpportunityResponse(BaseModel):
    id: str
    token_address: str
    source_chain: str
    target_chain: str
    source_price: float
    target_price: float
    price_difference: float
    profit_potential: float
    gas_estimate: float
    net_profit: float
    confidence_score: float
    timestamp: datetime

class ExecuteArbitrageRequest(BaseModel):
    opportunity_id: str
    amount: Optional[float] = Field(default=1000, description="Amount to trade in tokens")
    wallet_address: Optional[str] = Field(default=None, description="Wallet address for execution")

class ExecuteArbitrageResponse(BaseModel):
    status: str
    opportunity_id: str
    estimated_profit: float
    transaction_hash: Optional[str] = None
    message: str

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

class TokenPriceResponse(BaseModel):
    token_address: str
    chain: str
    price: float
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    updated_at: datetime

class UserCreateRequest(BaseModel):
    email: str
    wallet_address: str
    tier: str = "free"

class UserResponse(BaseModel):
    id: str
    email: str
    wallet_address: str
    api_key: Optional[str] = None
    tier: str
    created_at: datetime
    is_active: bool

class APIKeyResponse(BaseModel):
    api_key: str
    expires_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime