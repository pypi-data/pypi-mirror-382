"""
QDF SDK Main Client
"""

from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime

from .base import BaseClient
from .models import (
    RankedPool, RankingsResponse, RankingSession, RankingChange, PaginationInfo,
    PoolSummary, PoolDetail, PoolStats,
    MacroLiveData, MarketRegime, MarketAnalysis, FearGreedData
)
from .exceptions import ValidationError

logger = logging.getLogger(__name__)

# Parameter mapping dictionaries to handle API compatibility issues
PERIOD_MAP = {
    "24h": "1d",  # User-friendly -> API expected
    "1d": "1d",   # Already correct
    "7d": "7d",   # Already correct
}

METRIC_MAP = {
    # User-friendly shortcuts for metrics
    "ranking": "ranking_score",   # User-friendly -> API expected
    "tvl": "tvl_usd",            # User-friendly -> API expected
    "apy": "apy_processed",      # User-friendly -> API expected (works for rankings)
    # Note: "volume_24h" removed - column doesn't exist in rankings table
}


class QDFClient:
    """
    QDF SDK Client for accessing DeFi pool rankings and analytics

    Example:
        ```python
        from qdf import QDFClient

        client = QDFClient()
        top_pools = client.get_top_pools(n=10)
        ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize QDF Client

        Args:
            base_url: API base URL (default: http://localhost:8000)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.client = BaseClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        self.base_url = base_url

    # ============= Rankings API =============

    def get_top_pools(
        self,
        n: int = 10,
        chain: Optional[str] = None,
        pool_type: Optional[str] = None,
        metric: str = "ranking_score"
    ) -> List[RankedPool]:
        """
        Get top N pools by ranking or other metrics

        Args:
            n: Number of pools to return (1-500)
            chain: Filter by blockchain (e.g., 'Ethereum', 'Arbitrum')
            pool_type: Filter by pool type
            metric: Metric to sort by ('ranking_score', 'apy', 'tvl_usd', 'volume_24h', 'momentum_score')

        Returns:
            List of top ranked pools

        Example:
            ```python
            top_pools = client.get_top_pools(n=10, chain="Ethereum")
            ```
        """
        if not 1 <= n <= 500:
            raise ValidationError("n must be between 1 and 500")

        # Map user-friendly metric to API expected format
        mapped_metric = METRIC_MAP.get(metric, metric)

        params = {
            "pool_type": pool_type,
            "metric": mapped_metric
        }
        if chain:
            params["chain"] = chain

        response = self.client.get(f"/api/v2/rankings/top/{n}", params=params)
        return [RankedPool(**pool) for pool in response.get("data", [])]

    def get_rankings(
        self,
        page: int = 1,
        size: int = 100,
        chain: Optional[str] = None,
        project: Optional[str] = None,
        pool_type: Optional[str] = None,
        min_rank: Optional[int] = None,
        max_rank: Optional[int] = None,
        include_pool_data: bool = True
    ) -> RankingsResponse:
        """
        Get current pool rankings with pagination

        Args:
            page: Page number (starts from 1)
            size: Page size (max 1000)
            chain: Filter by blockchain
            project: Filter by project
            pool_type: Filter by pool type
            min_rank: Minimum rank filter
            max_rank: Maximum rank filter
            include_pool_data: Include full pool data

        Returns:
            Paginated rankings response

        Example:
            ```python
            rankings = client.get_rankings(chain="Arbitrum", page=1, size=50)
            for pool in rankings.data:
                print(f"{pool.rank_overall}. {pool.symbol}: {pool.apy:.2f}%")
            ```
        """
        params = {
            "page": page,
            "size": min(size, 1000),
            "chain": chain,
            "project": project,
            "pool_type": pool_type,
            "min_rank": min_rank,
            "max_rank": max_rank,
            "include_pool_data": include_pool_data
        }

        response = self.client.get("/api/v2/rankings/current", params=params)
        return RankingsResponse(**response)

    def get_pool_ranking(
        self,
        pool_id: str,
        include_history: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed ranking information for a specific pool

        Args:
            pool_id: Pool identifier
            include_history: Include historical ranking data

        Returns:
            Pool ranking details with optional history
        """
        params = {"include_history": include_history}
        return self.client.get(f"/api/v2/rankings/pool/{pool_id}", params=params)

    def get_ranking_movers(
        self,
        period: str = "24h",
        direction: Optional[str] = None,
        min_change: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get pools with significant ranking changes

        Args:
            period: Time period ('24h', '7d', '30d')
            direction: Filter by direction ('up', 'down')
            min_change: Minimum rank change
            limit: Maximum results

        Returns:
            List of pools with ranking changes
        """
        # Map user-friendly period to API expected format
        mapped_period = PERIOD_MAP.get(period, period)

        params = {
            "period": mapped_period,
            "direction": direction,
            "min_change": min_change,
            "limit": limit
        }
        response = self.client.get("/api/v2/rankings/changes", params=params)
        return response.get("data", [])

    def get_rankings_by_type(self, limit_per_type: int = 10) -> Dict[str, List[RankedPool]]:
        """
        Get top pools grouped by pool type

        Args:
            limit_per_type: Number of pools per type

        Returns:
            Dictionary with pool types as keys and lists of pools as values
        """
        params = {"limit_per_type": limit_per_type}
        response = self.client.get("/api/v2/rankings/by-type", params=params)

        result = {}
        for pool_type, pools in response.items():
            if isinstance(pools, list):
                result[pool_type] = [RankedPool(**p) for p in pools]
        return result

    # ============= Pools API =============

    def search_pools(
        self,
        query: str,
        search_fields: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[PoolSummary]:
        """
        Search for pools by text query

        Args:
            query: Search query
            search_fields: Fields to search in (default: ['symbol', 'project'])
            limit: Maximum results

        Returns:
            List of matching pools

        Example:
            ```python
            usdc_pools = client.search_pools("USDC", limit=5)
            ```
        """
        params = {
            "q": query,
            "limit": limit
        }
        if search_fields:
            params["search_fields"] = ",".join(search_fields)

        response = self.client.get("/api/v2/pools/search", params=params)
        return [PoolSummary(**pool) for pool in response.get("data", [])]

    def get_pool_detail(
        self,
        pool_id: str,
        include_history: bool = False
    ) -> PoolDetail:
        """
        Get detailed information about a specific pool

        Args:
            pool_id: Pool identifier
            include_history: Include historical data

        Returns:
            Detailed pool information
        """
        params = {"include_history": include_history}
        response = self.client.get(f"/api/v2/pools/{pool_id}", params=params)

        # Handle wrapped response format from backend
        if isinstance(response, dict) and "data" in response:
            return PoolDetail(**response["data"])
        return PoolDetail(**response)

    def get_pools(
        self,
        page: int = 1,
        size: int = 100,
        chain: Optional[str] = None,
        project: Optional[str] = None,
        pool_type: Optional[str] = None,
        tvl_min: Optional[float] = None,
        tvl_max: Optional[float] = None,
        apy_min: Optional[float] = None,
        apy_max: Optional[float] = None,
        is_trending: Optional[bool] = None,
        sort: str = "tvl_usd",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get pools with advanced filtering

        Args:
            page: Page number
            size: Page size
            chain: Filter by blockchain
            project: Filter by project
            pool_type: Filter by pool type
            tvl_min: Minimum TVL
            tvl_max: Maximum TVL
            apy_min: Minimum APY
            apy_max: Maximum APY
            is_trending: Filter trending pools
            sort: Sort field
            order: Sort order ('asc' or 'desc')

        Returns:
            Paginated pool data
        """
        # Backend pools endpoint uses 'apy' not 'apy_processed' for sorting
        if sort == "apy_processed":
            sort = "apy"

        params = {
            "page": page,
            "size": size,
            "chain": chain,
            "project": project,
            "pool_type": pool_type,
            "tvl_min": tvl_min,
            "tvl_max": tvl_max,
            "apy_min": apy_min,
            "apy_max": apy_max,
            "is_trending": is_trending,
            "sort": sort,
            "order": order
        }
        return self.client.get("/api/v2/pools", params=params)

    def get_pools_stats(
        self,
        chain: Optional[str] = None,
        pool_type: Optional[str] = None
    ) -> PoolStats:
        """
        Get aggregate statistics for pools

        Args:
            chain: Filter by blockchain
            pool_type: Filter by pool type

        Returns:
            Pool statistics
        """
        params = {
            "chain": chain,
            "pool_type": pool_type
        }
        response = self.client.get("/api/v2/pools/stats", params=params)

        # Handle wrapped response format
        if isinstance(response, dict) and "data" in response:
            return PoolStats(**response["data"])
        return PoolStats(**response)

    # ============= Macro API =============

    def get_market_regime(self) -> MarketRegime:
        """
        Get current market regime classification

        Returns:
            Current market regime

        Example:
            ```python
            regime = client.get_market_regime()
            print(f"Market: {regime.regime} (confidence: {regime.confidence:.1%})")
            ```
        """
        response = self.client.get("/macro/regime/current")
        return MarketRegime(**response)

    def get_macro_data(self) -> MacroLiveData:
        """
        Get live macro economic data

        Returns:
            Current macro data including prices, market cap, DeFi TVL
        """
        response = self.client.get("/macro/live")
        return MacroLiveData(**response)

    def get_fear_greed_index(self, days: int = 7) -> List[FearGreedData]:
        """
        Get Fear and Greed Index history

        Args:
            days: Number of days of history

        Returns:
            List of Fear and Greed Index data points
        """
        params = {"days": days}
        response = self.client.get("/macro/metrics/fear-greed", params=params)
        return [FearGreedData(**data) for data in response.get("data", [])]

    def get_market_analysis(self) -> MarketAnalysis:
        """
        Get latest market analysis

        Returns:
            Detailed market analysis with recommendations
        """
        response = self.client.get("/macro/analysis/latest")
        return MarketAnalysis(**response)

    def get_macro_history(self, hours: int = 24) -> List[MacroLiveData]:
        """
        Get historical macro data

        Args:
            hours: Number of hours of history (1-168)

        Returns:
            List of historical macro data points
        """
        if not 1 <= hours <= 168:
            raise ValidationError("hours must be between 1 and 168")

        params = {"hours": hours}
        response = self.client.get("/macro/live/history", params=params)
        return [MacroLiveData(**data) for data in response.get("data", [])]

    # ============= Score Methods (convenience) =============

    def get_risk_score(self, pool_id: str) -> float:
        """
        Get risk score for a pool

        Args:
            pool_id: Pool identifier

        Returns:
            Risk score (0-100, lower is better)
        """
        pool = self.get_pool_ranking(pool_id)
        return pool.get("score_components", {}).get("risk_score", 0.0)

    def get_momentum_score(self, pool_id: str) -> float:
        """
        Get momentum score for a pool

        Args:
            pool_id: Pool identifier

        Returns:
            Momentum score (0-100, higher is better)
        """
        pool = self.get_pool_ranking(pool_id)
        return pool.get("momentum_score", 0.0)

    def get_volume_score(self, pool_id: str) -> float:
        """
        Get volume score for a pool

        Args:
            pool_id: Pool identifier

        Returns:
            Volume score (0-100, higher is better)
        """
        pool = self.get_pool_ranking(pool_id)
        return pool.get("volume_score", 0.0)