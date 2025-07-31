from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token_address = Column(String(42), nullable=False)
    source_chain = Column(String(20), nullable=False)
    target_chain = Column(String(20), nullable=False)
    source_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    price_difference = Column(Float, nullable=False)
    profit_potential = Column(Float, nullable=False)
    gas_estimate = Column(Float, nullable=False)
    net_profit = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default='active')

class ArbitrageExecution(Base):
    __tablename__ = "arbitrage_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(String, nullable=False)
    executor_address = Column(String(42), nullable=False)
    transaction_hash = Column(String(66))
    amount_executed = Column(Float, nullable=False)
    actual_profit = Column(Float, nullable=False)
    gas_used = Column(Float, nullable=False)
    execution_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default='pending')

class TokenPrice(Base):
    __tablename__ = "token_prices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token_address = Column(String(42), nullable=False)
    chain = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    volume_24h = Column(Float)
    liquidity = Column(Float)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    wallet_address = Column(String(42), unique=True, nullable=False)
    api_key = Column(String(255), unique=True)
    tier = Column(String(20), default='free')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)