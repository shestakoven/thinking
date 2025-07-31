from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime, timedelta
import secrets
from typing import List, Optional

from .database import get_db, init_db
from .models import ArbitrageOpportunity as ArbitrageOpportunityModel, User
from .schemas import (
    ArbitrageOpportunityResponse, ExecuteArbitrageRequest, ExecuteArbitrageResponse,
    HealthCheckResponse, UserCreateRequest, UserResponse, APIKeyResponse, ErrorResponse
)
from .arbitrage_detector import CrossChainArbitrageDetector, IndexerClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cross-Chain Arbitrage Platform",
    description="Real-time cross-chain arbitrage opportunity detection and execution",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize components
indexer_client = IndexerClient(os.getenv("INDEXER_URL", "http://localhost:8001"))
arbitrage_detector = CrossChainArbitrageDetector(indexer_client)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Arbitrage platform started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Arbitrage platform shutting down")

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now()
    )

# Arbitrage opportunities endpoints
@app.get("/api/v1/opportunities", response_model=List[ArbitrageOpportunityResponse])
async def get_arbitrage_opportunities(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current arbitrage opportunities"""
    try:
        # Verify API key
        user = verify_api_key(db, credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Detect opportunities
        opportunities = await arbitrage_detector.detect_opportunities()
        
        # Convert to response format
        response_opportunities = []
        for opp in opportunities:
            response_opportunities.append(ArbitrageOpportunityResponse(
                id=opp.id,
                token_address=opp.token_address,
                source_chain=opp.source_chain,
                target_chain=opp.target_chain,
                source_price=opp.source_price,
                target_price=opp.target_price,
                price_difference=opp.price_difference,
                profit_potential=opp.profit_potential,
                gas_estimate=opp.gas_estimate,
                net_profit=opp.net_profit,
                confidence_score=opp.confidence_score,
                timestamp=opp.timestamp
            ))
        
        return response_opportunities
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail="Error detecting opportunities")

@app.get("/api/v1/opportunities/{token_address}", response_model=List[ArbitrageOpportunityResponse])
async def get_token_opportunities(
    token_address: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get arbitrage opportunities for specific token"""
    try:
        # Verify API key
        user = verify_api_key(db, credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Get all opportunities and filter by token
        opportunities = await arbitrage_detector.detect_opportunities()
        token_opportunities = [opp for opp in opportunities if opp.token_address == token_address]
        
        # Convert to response format
        response_opportunities = []
        for opp in token_opportunities:
            response_opportunities.append(ArbitrageOpportunityResponse(
                id=opp.id,
                token_address=opp.token_address,
                source_chain=opp.source_chain,
                target_chain=opp.target_chain,
                source_price=opp.source_price,
                target_price=opp.target_price,
                price_difference=opp.price_difference,
                profit_potential=opp.profit_potential,
                gas_estimate=opp.gas_estimate,
                net_profit=opp.net_profit,
                confidence_score=opp.confidence_score,
                timestamp=opp.timestamp
            ))
        
        return response_opportunities
    except Exception as e:
        logger.error(f"Error getting token opportunities: {e}")
        raise HTTPException(status_code=500, detail="Error getting token opportunities")

# Execute arbitrage endpoint
@app.post("/api/v1/execute", response_model=ExecuteArbitrageResponse)
async def execute_arbitrage(
    request: ExecuteArbitrageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Execute arbitrage opportunity"""
    try:
        # Verify API key
        user = verify_api_key(db, credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Find opportunity
        opportunities = await arbitrage_detector.detect_opportunities()
        opportunity = next((opp for opp in opportunities if opp.id == request.opportunity_id), None)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        # Check if opportunity is still profitable
        if opportunity.net_profit <= 0:
            raise HTTPException(status_code=400, detail="Opportunity no longer profitable")
        
        # Execute arbitrage in background
        background_tasks.add_task(
            execute_arbitrage_task, 
            opportunity, 
            request.amount or 1000,
            request.wallet_address or user.wallet_address,
            db
        )
        
        return ExecuteArbitrageResponse(
            status="execution_started",
            opportunity_id=request.opportunity_id,
            estimated_profit=opportunity.net_profit,
            message="Arbitrage execution initiated"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing arbitrage: {e}")
        raise HTTPException(status_code=500, detail="Error executing arbitrage")

# User management endpoints
@app.post("/api/v1/users", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.wallet_address == request.wallet_address)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user = User(
            email=request.email,
            wallet_address=request.wallet_address,
            tier=request.tier,
            api_key=generate_api_key()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            wallet_address=user.wallet_address,
            api_key=user.api_key,
            tier=user.tier,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current user information"""
    try:
        user = verify_api_key(db, credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            wallet_address=user.wallet_address,
            api_key=user.api_key,
            tier=user.tier,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Error getting user")

# Helper functions
def verify_api_key(db: Session, api_key: str) -> Optional[User]:
    """Verify API key and return user"""
    user = db.query(User).filter(User.api_key == api_key, User.is_active == True).first()
    return user

def generate_api_key() -> str:
    """Generate a new API key"""
    return secrets.token_urlsafe(32)

async def execute_arbitrage_task(
    opportunity,
    amount: float,
    wallet_address: str,
    db: Session
):
    """Background task to execute arbitrage"""
    try:
        logger.info(f"Executing arbitrage: {opportunity.id}")
        
        # Here you would integrate with your existing infrastructure:
        # 1. Connect to your wallet management system
        # 2. Execute the cross-chain transaction
        # 3. Record the execution in the database
        
        # Simulate execution delay
        import asyncio
        await asyncio.sleep(5)
        
        # Record execution in database
        execution = ArbitrageOpportunityModel(
            id=opportunity.id,
            token_address=opportunity.token_address,
            source_chain=opportunity.source_chain,
            target_chain=opportunity.target_chain,
            source_price=opportunity.source_price,
            target_price=opportunity.target_price,
            price_difference=opportunity.price_difference,
            profit_potential=opportunity.profit_potential,
            gas_estimate=opportunity.gas_estimate,
            net_profit=opportunity.net_profit,
            confidence_score=opportunity.confidence_score,
            expires_at=datetime.now() + timedelta(hours=1),
            status="executed"
        )
        
        db.add(execution)
        db.commit()
        
        logger.info(f"Arbitrage executed successfully: {opportunity.id}")
    except Exception as e:
        logger.error(f"Error in arbitrage execution: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)