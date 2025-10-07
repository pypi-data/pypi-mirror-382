# QDF SDK - Quantitative DeFi Data SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-orange)](https://github.com/qdf-sdk)

## Introduction

QDF SDK is a professional DeFi pool data access tool that provides real-time data access to over 7,000 DeFi liquidity pools. Through a clean Python interface, you can easily retrieve pool rankings, search for specific pools, and view market macro data.

### Core Features

- 🚀 **Simple to Use** - Get started with just 3 lines of code
- 📊 **Massive Dataset** - Covers 60+ blockchains, 7,000+ liquidity pools
- 🎯 **Intelligent Ranking** - Multi-dimensional scoring system based on IQR algorithm
- ⚡ **High Performance** - Built-in caching and retry mechanism for stability
- 🔍 **Flexible Queries** - Supports various filtering and sorting methods

## Quick Start

### Installation

```bash
pip install qdf-sdk
```

### Basic Usage

```python
from qdf import QDFClient

# Create client
client = QDFClient()

# Get Top 10 pools
top_pools = client.get_top_pools(n=10)
for pool in top_pools:
    print(f"{pool.symbol}: Score {pool.ranking_score:.2f}")
```

## Usage Examples

### 1. Get High-Scoring Pools

```python
# Get top 5 highest-scoring pools
top_pools = client.get_top_pools(n=5)

for pool in top_pools:
    print(f"""
    Pool: {pool.symbol}
    Chain: {pool.chain}
    Overall Score: {pool.ranking_score:.2f}
    TVL: ${pool.tvl_usd:,.0f}
    APY: {pool.apy:.2f}%
    """)
```

### 2. Sort by Different Metrics

```python
# Sort by TVL
high_tvl = client.get_top_pools(n=10, metric="tvl")

# Sort by APY
high_apy = client.get_top_pools(n=10, metric="apy")

# Sort by score (default)
top_score = client.get_top_pools(n=10, metric="ranking_score")
```

### 3. Search for Specific Pools

```python
# Search for USDC-related pools
usdc_pools = client.search_pools("USDC", limit=10)

for pool in usdc_pools:
    print(f"{pool.symbol} on {pool.chain}")
```

### 4. Get Paginated Data

```python
# Get page 1 data
rankings = client.get_rankings(page=1, size=20)

print(f"Total pools: {rankings.pagination.total}")
print(f"Total pages: {rankings.pagination.pages}")
print(f"Current page: {rankings.pagination.page}")

for pool in rankings.data:
    print(f"{pool.rank}. {pool.symbol}")
```

### 5. Filter by Chain

```python
# Get only Ethereum pools
eth_pools = client.get_rankings(chain="Ethereum", size=10)

# Get Arbitrum pools
arb_pools = client.get_rankings(chain="Arbitrum", size=10)
```

### 6. View Ranking Changes

```python
# Get pools with biggest ranking changes in 24 hours
movers = client.get_ranking_movers(period="24h", limit=10)

for mover in movers:
    print(f"{mover.symbol}: Rank change {mover.rank_change}")
```

### 7. Get Market Macro Data

```python
# Get overall market data
macro = client.get_macro_data()

print(f"BTC Price: ${macro.btc_price:,.0f}")
print(f"ETH Price: ${macro.eth_price:,.0f}")
print(f"Fear & Greed Index: {macro.crypto_fear_greed}")
print(f"Market Regime: {macro.market_regime_name}")
print(f"ETH Gas: {macro.eth_gas_price_gwei} Gwei")
```

## API Documentation

### Main Methods

| Method | Description | Parameters |
|------|------|------|
| `get_top_pools()` | Get top pools | `n`: count, `metric`: sorting metric |
| `get_rankings()` | Get paginated rankings | `page`, `size`, `chain`, `protocol` |
| `search_pools()` | Search pools | `query`: search term, `limit`: result limit |
| `get_pool_detail()` | Get pool details | `pool_id`: pool ID |
| `get_ranking_movers()` | Get ranking changes | `period`: time period, `limit`: count |
| `get_macro_data()` | Get macro data | None |

### Sorting Metrics

- `ranking_score` - Overall score (default)
- `tvl` - Total Value Locked
- `apy` - Annual Percentage Yield
- `volume_24h` - 24-hour volume
- `il_risk` - Impermanent loss risk

### Supported Blockchains

Major supported chains include:
- Ethereum
- Arbitrum
- Optimism
- Polygon
- BSC
- Avalanche
- Base
- And 50+ other chains...

## Data Models

### RankedPool

```python
class RankedPool:
    pool_id: str           # Pool unique ID
    chain: str             # Blockchain
    project: str           # Project name
    symbol: str            # Pool symbol
    tvl_usd: float        # TVL (USD)
    apy: float            # Annual Percentage Yield
    ranking_score: float   # Overall score
    rank: int             # Current rank
    # ... more fields
```

### MacroLiveData

```python
class MacroLiveData:
    btc_price: float              # BTC price
    eth_price: float              # ETH price
    crypto_fear_greed: float      # Fear & Greed Index
    market_regime_name: str       # Market regime
    eth_gas_price_gwei: float     # Gas price
    # ... more fields
```

## Advanced Usage

### Custom Configuration

```python
from qdf import QDFClient

# Custom API endpoint (for private deployment)
client = QDFClient(
    base_url="https://your-api.com",
    timeout=30,
    max_retries=5
)
```

### Error Handling

```python
from qdf import QDFClient, APIError

client = QDFClient()

try:
    pools = client.get_top_pools(n=10)
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

## Performance Optimization

The SDK has multiple built-in optimizations:

1. **Connection Pooling** - Reuses HTTP connections to reduce latency
2. **Auto Retry** - Automatically handles temporary errors
3. **Smart Caching** - Reduces duplicate requests
4. **Batch Requests** - Supports batch data fetching

## FAQ

### Q: How often is the data updated?
A: Core data is updated hourly, ranking data is updated every 4 hours.

### Q: What filtering options are supported?
A: Supports filtering by chain, protocol, TVL range, APY range, and more.

### Q: How do I get historical data?
A: Current version only provides real-time data, historical data feature is under development.

### Q: Are there API call limits?
A: Default limit is 100 requests per minute. Contact us for higher limits.

## Roadmap

- [x] Basic query functionality
- [x] Ranking system
- [x] Macro data integration
- [ ] WebSocket real-time push
- [ ] Historical data queries
- [ ] Strategy backtesting support
- [ ] More chain support

## Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact Us

- 📧 Email: contact@qdf.io
- 🌐 Website: https://qdf.io
- 📖 Documentation: https://docs.qdf.io

---

<div align="center">
<b>QDF SDK</b> - Making DeFi Data Accessible
</div>