import asyncio
import aiohttp
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

@dataclass
class ArbitrageOpportunity:
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

class IndexerClient:
    """Client to interact with your existing blockchain indexer"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_token_price(self, token_address: str, chain: str) -> Dict[str, any]:
        """Get token price from your existing indexer"""
        session = await self.get_session()
        
        # This would connect to your existing indexer infrastructure
        # For now, we'll simulate the response
        try:
            async with session.get(f"{self.base_url}/api/v1/token/{token_address}/price?chain={chain}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    # Fallback to simulated data
                    return self._get_simulated_price(token_address, chain)
        except Exception as e:
            logging.error(f"Error getting price for {token_address} on {chain}: {e}")
            return self._get_simulated_price(token_address, chain)
    
    def _get_simulated_price(self, token_address: str, chain: str) -> Dict[str, any]:
        """Simulate price data for development"""
        base_prices = {
            '0xA0b86a33E6441b8c4C8C2B8c4C8C2B8c4C8C2B8c': 1.0,  # USDC
            '0xdAC17F958D2ee523a2206206994597C13D831ec7': 1.0,  # USDT
            '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 45000.0,  # WBTC
        }
        
        chain_multipliers = {
            'ethereum': 1.0,
            'polygon': 0.999,
            'arbitrum': 0.998,
            'optimism': 0.997,
            'bsc': 0.996,
        }
        
        base_price = base_prices.get(token_address, 1.0)
        chain_multiplier = chain_multipliers.get(chain, 1.0)
        
        # Add some randomness to simulate real market conditions
        import random
        price_variation = random.uniform(0.995, 1.005)
        
        return {
            'price': base_price * chain_multiplier * price_variation,
            'volume_24h': random.uniform(1000000, 10000000),
            'liquidity': random.uniform(5000000, 50000000)
        }

class CrossChainArbitrageDetector:
    def __init__(self, indexer_client: IndexerClient):
        self.indexer = indexer_client
        self.chains = ['ethereum', 'polygon', 'arbitrum', 'optimism', 'bsc']
        self.min_profit_threshold = 0.5  # 0.5% minimum profit
        self.tracked_tokens = [
            '0xA0b86a33E6441b8c4C8C2B8c4C8C2B8c4C8C2B8c',  # USDC
            '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
            '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',  # WBTC
        ]
        self.gas_price_cache = {}
        self.cache_duration = 300  # 5 minutes
    
    async def detect_opportunities(self) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities across all chains"""
        opportunities = []
        
        for token in self.tracked_tokens:
            try:
                prices = await self.get_cross_chain_prices(token)
                
                for i, chain1 in enumerate(self.chains):
                    for chain2 in self.chains[i+1:]:
                        if chain1 != chain2 and chain1 in prices and chain2 in prices:
                            opportunity = self.calculate_arbitrage(
                                token, chain1, chain2, prices[chain1], prices[chain2]
                            )
                            if opportunity and opportunity.net_profit > 0:
                                opportunities.append(opportunity)
            except Exception as e:
                logging.error(f"Error detecting opportunities for token {token}: {e}")
                continue
        
        return sorted(opportunities, key=lambda x: x.net_profit, reverse=True)
    
    async def get_cross_chain_prices(self, token_address: str) -> Dict[str, float]:
        """Get real-time prices across all chains"""
        prices = {}
        
        # Get prices concurrently for better performance
        tasks = []
        for chain in self.chains:
            tasks.append(self.get_chain_price(token_address, chain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, chain in enumerate(self.chains):
            if isinstance(results[i], Exception):
                logging.error(f"Error getting price for {chain}: {results[i]}")
                continue
            
            if results[i] and 'price' in results[i]:
                prices[chain] = results[i]['price']
        
        return prices
    
    async def get_chain_price(self, token_address: str, chain: str) -> Optional[Dict[str, any]]:
        """Get price for a specific chain"""
        try:
            return await self.indexer.get_token_price(token_address, chain)
        except Exception as e:
            logging.error(f"Error getting price for {token_address} on {chain}: {e}")
            return None
    
    def calculate_arbitrage(self, token: str, source_chain: str, 
                          target_chain: str, source_price: float, 
                          target_price: float) -> Optional[ArbitrageOpportunity]:
        """Calculate arbitrage opportunity with gas costs"""
        
        price_diff = abs(target_price - source_price)
        price_diff_percent = (price_diff / min(source_price, target_price)) * 100
        
        if price_diff_percent < self.min_profit_threshold:
            return None
        
        # Estimate gas costs using historical data
        gas_cost_source = self.estimate_gas_cost(source_chain)
        gas_cost_target = self.estimate_gas_cost(target_chain)
        total_gas_cost = gas_cost_source + gas_cost_target
        
        # Calculate profit
        if source_price < target_price:
            buy_chain, sell_chain = source_chain, target_chain
            buy_price, sell_price = source_price, target_price
        else:
            buy_chain, sell_chain = target_chain, source_chain
            buy_price, sell_price = target_price, source_price
        
        # Calculate profit for a 1000 token trade
        trade_amount = 1000
        profit_potential = (sell_price - buy_price) * trade_amount
        net_profit = profit_potential - total_gas_cost
        
        if net_profit <= 0:
            return None
        
        return ArbitrageOpportunity(
            id=f"{token}_{source_chain}_{target_chain}_{int(time.time())}",
            token_address=token,
            source_chain=buy_chain,
            target_chain=sell_chain,
            source_price=buy_price,
            target_price=sell_price,
            price_difference=price_diff,
            profit_potential=profit_potential,
            gas_estimate=total_gas_cost,
            net_profit=net_profit,
            confidence_score=min(price_diff_percent / 10, 1.0),
            timestamp=datetime.now()
        )
    
    def estimate_gas_cost(self, chain: str) -> float:
        """Estimate gas costs using historical data"""
        # This would use your existing historical gas data
        gas_prices = {
            'ethereum': 50,  # gwei
            'polygon': 30,
            'arbitrum': 0.1,
            'optimism': 0.001,
            'bsc': 5
        }
        
        gas_price = gas_prices.get(chain, 50)
        gas_limit = 21000  # Standard transfer gas limit
        
        # Convert to ETH equivalent
        if chain == 'ethereum':
            return gas_price * 0.000000001 * gas_limit
        elif chain == 'polygon':
            return gas_price * 0.000000001 * gas_limit * 0.0001  # MATIC to ETH
        elif chain == 'arbitrum':
            return gas_price * 0.000000001 * gas_limit * 0.0001  # ARB to ETH
        elif chain == 'optimism':
            return gas_price * 0.000000001 * gas_limit * 0.0001  # OP to ETH
        elif chain == 'bsc':
            return gas_price * 0.000000001 * gas_limit * 0.0001  # BNB to ETH
        else:
            return gas_price * 0.000000001 * gas_limit
    
    async def get_tracked_tokens(self) -> List[str]:
        """Get list of tokens to track for arbitrage"""
        return self.tracked_tokens
    
    async def update_gas_prices(self):
        """Update gas price cache from your indexer"""
        # This would fetch real-time gas prices from your indexer
        # For now, we'll use static values
        pass