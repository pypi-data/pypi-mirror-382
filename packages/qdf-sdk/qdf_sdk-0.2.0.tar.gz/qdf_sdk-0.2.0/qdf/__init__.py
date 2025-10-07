"""
QDF SDK - Python SDK for QuantDeFi Pool Rankings and Analytics

Example:
    ```python
    from qdf import QDFClient

    client = QDFClient()
    top_pools = client.get_top_pools(n=10)
    ```
"""

from .client import QDFClient
from .exceptions import (
    QDFError,
    APIError,
    NetworkError,
    ValidationError,
    NotFoundError,
    RateLimitError
)
from .models import (
    # Rankings
    RankedPool,
    RankingChange,
    RankingsResponse,
    RankingSession,
    # Pools
    PoolSummary,
    PoolDetail,
    PoolStats,
    # Macro
    MacroLiveData,
    MarketRegime,
    MarketAnalysis,
    FearGreedData
)

__version__ = "0.2.0"
__author__ = "QuantDeFi"

__all__ = [
    # Main client
    "QDFClient",

    # Exceptions
    "QDFError",
    "APIError",
    "NetworkError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",

    # Models
    "RankedPool",
    "RankingChange",
    "RankingsResponse",
    "RankingSession",
    "PoolSummary",
    "PoolDetail",
    "PoolStats",
    "MacroLiveData",
    "MarketRegime",
    "MarketAnalysis",
    "FearGreedData",
]