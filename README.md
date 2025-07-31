# 🚀 Cross-Chain Arbitrage Platform

A complete cross-chain arbitrage platform that leverages your existing blockchain indexer infrastructure to detect and execute profitable opportunities across multiple chains.

## 📊 Overview

This platform provides:
- **Real-time arbitrage detection** across Ethereum, Polygon, Arbitrum, Optimism, and BSC
- **Production-ready API** with FastAPI backend
- **Modern React frontend** with real-time dashboard
- **Smart contract execution** for secure arbitrage
- **Complete monitoring** with Prometheus and Grafana
- **Docker deployment** for easy setup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  Smart Contracts│
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Ethereum)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   PostgreSQL    │    │  Your Indexer   │
│   (Port 80)     │    │   (Port 5432)   │    │  Infrastructure │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │
│   (Port 9090)   │    │   (Port 3001)   │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Your existing blockchain indexer infrastructure
- At least 8GB RAM and 4 CPU cores

### 1. Clone and Deploy
```bash
# Clone the repository
git clone <repository-url>
cd cross-chain-arbitrage

# Make deployment script executable
chmod +x deploy.sh

# Deploy the platform
./deploy.sh
```

### 2. Configure Your Indexer
Update the `INDEXER_URL` in `docker-compose.yml` to point to your existing blockchain indexer:

```yaml
environment:
  - INDEXER_URL=http://your-indexer-url
```

### 3. Access the Platform
- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Grafana Monitoring**: http://localhost:3001 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090

## 💻 API Endpoints

### Authentication
All API endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer your_api_key_here
```

### Core Endpoints

#### Get Arbitrage Opportunities
```bash
GET /api/v1/opportunities
```

Response:
```json
[
  {
    "id": "token_chain1_chain2_timestamp",
    "token_address": "0xA0b86a33E6441b8c4C8C2B8c4C8C2B8c4C8C2B8c",
    "source_chain": "ethereum",
    "target_chain": "polygon",
    "source_price": 1800.50,
    "target_price": 1820.75,
    "price_difference": 20.25,
    "profit_potential": 202.50,
    "gas_estimate": 15.00,
    "net_profit": 187.50,
    "confidence_score": 0.85,
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

#### Execute Arbitrage
```bash
POST /api/v1/execute
Content-Type: application/json

{
  "opportunity_id": "token_chain1_chain2_timestamp",
  "amount": 1000,
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
}
```

#### Create User
```bash
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "tier": "pro"
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://arbitrage_user:password@localhost:5432/arbitrage_db
REDIS_URL=redis://localhost:6379

# Your Indexer
INDEXER_URL=http://your-indexer-url

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Business Logic
MIN_PROFIT_THRESHOLD=0.5
MAX_GAS_PRICE=100
EXECUTION_TIMEOUT=30
```

### Smart Contract Configuration

Deploy the smart contract to your preferred network:

```bash
# Compile contracts
cd contracts
npm install
npx hardhat compile

# Deploy to network
npx hardhat run scripts/deploy.js --network mainnet
```

## 📈 Business Model

### Revenue Streams
1. **MEV Revenue**: 80% of arbitrage profits
2. **API Access**: $500-2000/month per enterprise client
3. **Execution Fees**: 0.1-0.5% of trade volume
4. **Data Services**: $100-500/month per trader

### Pricing Tiers
| Tier | Price | Features | Target Market |
|------|-------|----------|---------------|
| **Free** | $0 | Basic opportunities, 1 chain | Individual traders |
| **Pro** | $99/month | All chains, real-time alerts | Active traders |
| **Enterprise** | $999/month | API access, custom analytics | Hedge funds, protocols |
| **White Label** | $5000/month | Branded solution | Exchanges, platforms |

## 🔍 Monitoring

### Grafana Dashboards
- **Arbitrage Opportunities**: Real-time opportunity tracking
- **Execution Performance**: Success rates and profit metrics
- **System Health**: API response times and error rates
- **Gas Costs**: Historical gas price analysis

### Prometheus Metrics
- `arbitrage_opportunities_total`: Total opportunities detected
- `arbitrage_executions_total`: Total executions performed
- `arbitrage_profit_total`: Total profit generated
- `api_request_duration_seconds`: API performance metrics

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Smart Contract Development
```bash
cd contracts
npm install
npx hardhat test
npx hardhat compile
```

## 🔒 Security

### API Security
- Bearer token authentication
- Rate limiting (10 requests/minute)
- CORS protection
- Input validation

### Smart Contract Security
- Reentrancy protection
- Access control
- Emergency pause functionality
- Gas optimization

### Infrastructure Security
- Non-root Docker containers
- Health checks
- SSL/TLS encryption
- Regular security updates

## 📊 Performance

### Scalability
- **Horizontal scaling**: Multiple API instances
- **Database optimization**: Indexed queries
- **Caching**: Redis for frequently accessed data
- **Load balancing**: Nginx reverse proxy

### Performance Metrics
- **API Response Time**: < 100ms average
- **Opportunity Detection**: Real-time (30s intervals)
- **Execution Speed**: < 5 seconds per arbitrage
- **Uptime**: 99.9% target

## 🚨 Troubleshooting

### Common Issues

#### API Not Responding
```bash
# Check API health
curl http://localhost:8000/health

# View API logs
docker-compose logs arbitrage-api
```

#### Database Connection Issues
```bash
# Check database status
docker-compose logs postgres

# Test database connection
docker-compose exec postgres psql -U arbitrage_user -d arbitrage_db
```

#### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs arbitrage-frontend

# Rebuild frontend
docker-compose up -d --build arbitrage-frontend
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f arbitrage-api

# Access container shell
docker-compose exec arbitrage-api bash
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- **Email**: support@arbitrage-platform.com
- **Discord**: [Join our community](https://discord.gg/arbitrage)
- **Documentation**: [Full documentation](https://docs.arbitrage-platform.com)

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic arbitrage detection
- ✅ API endpoints
- ✅ Frontend dashboard
- ✅ Smart contract execution

### Phase 2 (Next 3 months)
- 🔄 Advanced analytics
- 🔄 Machine learning predictions
- 🔄 Mobile app
- 🔄 More chain support

### Phase 3 (6 months)
- 📋 White-label solutions
- 📋 Enterprise features
- 📋 Advanced risk management
- 📋 Institutional tools

---

**Built with ❤️ for the DeFi community**