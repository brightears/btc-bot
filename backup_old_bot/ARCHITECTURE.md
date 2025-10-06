# AI Trading Lab - System Architecture

## Overview

The AI Trading Lab is a sophisticated automated trading system that combines traditional quantitative strategies with artificial intelligence to discover, test, and execute profitable trading opportunities. The system operates 24/7 on cloud infrastructure with comprehensive safety mechanisms and remote management capabilities.

## System Components

### 1. AI Brain Module (`ai_brain/`)

The intelligence layer that drives strategy discovery and optimization.

#### Components:
- **Learning Engine** (`learning_engine.py`)
  - Pattern recognition using similarity scoring
  - Market regime identification
  - Historical pattern database
  - Confidence calculation algorithms
  - Experience replay buffer (10,000 capacity) with prioritized sampling

- **Hypothesis Generator** (`hypothesis_generator.py`)
  - Creative strategy generation with Gemini 2.5 Flash LLM
  - Research-based hypothesis creation
  - "Crazy idea" exploration for edge discovery
  - Parameter optimization using real volatility (ATR-based)
  - Take-profit and stop-loss based on actual market data

- **Strategy Evaluator** (`strategy_evaluator.py`)
  - Performance metric calculation
  - Risk-adjusted return analysis
  - Statistical significance testing
  - Strategy ranking and selection

- **Real-time Market Data** (`realtime_market_data.py`)
  - Live Binance API integration for spot and futures
  - Real funding rates and order book data
  - NO simulated data - all prices are real
  - Automatic data quality scoring

- **Paper Trading Engine** (`paper_trading_engine.py`)
  - Realistic simulation using actual market prices
  - Real exchange fees (0.1% maker/taker)
  - Slippage modeling based on order book depth
  - P&L calculation with actual price movements

- **Data Integrity Validator** (`data_integrity_validator.py`)
  - Prevents AI hallucination by validating all data
  - Blocks trading if real data unavailable
  - Price spike detection
  - Volume and funding rate validation

- **Enhanced Intelligence** (New Components)
  - **LLM Analyzer** (`llm_analyzer.py`): Gemini 2.5 Flash integration
  - **News Fetcher** (`news_fetcher.py`): Real-time crypto news monitoring
  - **Sentiment Analyzer** (`sentiment_analyzer.py`): Market sentiment analysis
  - **On-chain Monitor** (`onchain_monitor.py`): Whale activity tracking
  - **Historical Data Fetcher** (`historical_data_fetcher.py`): Backtesting data

### 2. Trading Execution Layer (`src/`)

Core trading logic and exchange interaction.

#### Components:
- **Exchange Integration** (`exchange/binance.py`)
  - CCXT-based unified interface
  - Order management
  - Market data streaming
  - WebSocket connections for real-time data

- **Funding Carry Module** (`funding/`)
  - Delta-neutral position management
  - Funding rate calculation
  - Entry/exit logic
  - Position rebalancing

- **Risk Management** (`risk/guards.py`)
  - Position size limits
  - Drawdown protection
  - Correlation checks
  - Emergency stop mechanisms

### 3. Communication Layer

#### Telegram Integration
- **Message-Only Bot** (`ai_trading_lab.py`)
  - Hourly status reports
  - 6-hour heartbeat confirmations
  - Strategy discovery alerts
  - Action-required notifications

#### Management Scripts
- `get_status.py` - System health and position status
- `approve_strategy.py` - Manual strategy approval
- `go_live.py` - Production trading activation
- `stop_trading.py` - Emergency shutdown

### 4. Infrastructure Layer

#### VPS Deployment
- **Auto-Restart Monitoring** (`monitor_bot.sh`)
  - Process health checks every 5 minutes
  - Automatic restart on failure
  - Log rotation and management

#### Data Persistence
- **Strategy Storage** (`strategies/`)
  - JSON-based strategy definitions
  - Performance history
  - Approval status tracking

- **Logging System**
  - Structured logging to `ai_lab.log`
  - Rotating log files
  - Debug/Info/Warning/Error levels

## Data Flow

```
Market Data → AI Brain → Strategy Generation
                ↓
         Strategy Testing
                ↓
         Performance Evaluation
                ↓
         Human Approval (if promising)
                ↓
         Live Execution
                ↓
         Performance Monitoring → Feedback to AI Brain
```

## Communication Architecture

### Internal Communication
- **Async/Await Pattern**: All components use asyncio for non-blocking operations
- **Message Queue**: Internal event system for component communication
- **Shared State**: Thread-safe state management for concurrent operations

### External Communication
- **REST APIs**: Exchange interaction via CCXT
- **WebSockets**: Real-time market data streaming
- **Telegram Bot API**: One-way messaging (no polling)

## Security Architecture

### Multi-Layer Security
1. **Environment Variables**: Sensitive data never in code
2. **Double-Gate System**: Multiple confirmations for live trading
3. **Rate Limiting**: API call throttling
4. **Position Limits**: Maximum exposure constraints
5. **Emergency Stop**: Kill switch for immediate shutdown

### API Key Management
- Separate keys for testnet/mainnet
- Read-only keys for monitoring
- Trade keys with withdrawal disabled
- Encrypted storage in .env files

## Deployment Architecture

### Local Development
```
Developer Machine
    ├── Virtual Environment (.venv)
    ├── Test Configuration
    └── Git Repository
```

### Production (VPS)
```
Hetzner VPS (Singapore)
    ├── AI Trading Lab Process
    ├── Monitor Script (auto-restart)
    ├── Git Pull for Updates
    └── Telegram Notifications
```

### CI/CD Pipeline
1. Local development and testing
2. Git push to GitHub
3. SSH to VPS
4. Git pull latest changes
5. Automatic restart via monitor script

## Strategy Management

### Strategy Lifecycle
1. **Generation**: AI creates hypothesis
2. **Backtesting**: Historical performance analysis
3. **Dry-Run**: Paper trading validation
4. **Review**: Human approval required
5. **Live Testing**: Small position deployment
6. **Scaling**: Gradual position increase
7. **Retirement**: Strategy deactivation

### Strategy Storage Schema
```json
{
  "id": "unique_identifier",
  "name": "strategy_name",
  "type": "funding_carry|momentum|mean_reversion",
  "parameters": {},
  "performance": {
    "backtest": {},
    "dry_run": {},
    "live": {}
  },
  "status": "testing|approved|live|retired",
  "created_at": "timestamp",
  "approved_at": "timestamp"
}
```

## Performance Monitoring

### Metrics Collected
- **Strategy Metrics**
  - Win rate
  - Sharpe ratio
  - Maximum drawdown
  - Average return

- **System Metrics**
  - API latency
  - Order fill rates
  - Memory usage
  - CPU utilization

- **Risk Metrics**
  - Position exposure
  - Correlation matrix
  - VaR calculations
  - Stress test results

## Scalability Considerations

### Current Limitations
- Single exchange (Binance)
- Single asset focus (BTC)
- Sequential strategy evaluation

### Future Scaling
- Multi-exchange arbitrage
- Portfolio-level optimization
- Distributed backtesting
- Machine learning cluster

## Error Handling

### Error Categories
1. **Exchange Errors**: Retry with exponential backoff
2. **Network Errors**: Fallback to cached data
3. **Strategy Errors**: Isolation and logging
4. **Critical Errors**: Emergency stop and notification

### Recovery Procedures
- Automatic reconnection for WebSockets
- State recovery from persistent storage
- Position reconciliation on restart
- Manual intervention alerts

## Database Design

### Current Storage (File-based)
```
btc-bot/
├── strategies/
│   ├── active/
│   ├── testing/
│   └── retired/
├── logs/
│   ├── ai_lab.log
│   └── performance.json
└── state/
    └── current_positions.json
```

### Future Database Schema
- TimescaleDB for time-series data
- PostgreSQL for strategy metadata
- Redis for real-time state
- S3 for backup and archives

## Testing Architecture

### Test Levels
1. **Unit Tests**: Component isolation
2. **Integration Tests**: Module interaction
3. **System Tests**: End-to-end flows
4. **Dry-Run**: Production simulation

### Test Coverage
- Strategy logic validation
- Risk management verification
- Exchange interaction mocking
- Performance regression testing

## Maintenance Procedures

### Daily Operations
- Log review and rotation
- Performance metric analysis
- Strategy approval decisions
- System health verification

### Weekly Tasks
- Strategy performance review
- Risk parameter adjustment
- Code deployment if needed
- Backup verification

### Emergency Procedures
1. Execute `stop_trading.py`
2. Check position status
3. Review error logs
4. Implement fixes
5. Gradual restart with monitoring

---

**Last Updated**: v1.0-ai-lab-deployed
**Architecture Version**: 1.0
**Review Cycle**: Monthly