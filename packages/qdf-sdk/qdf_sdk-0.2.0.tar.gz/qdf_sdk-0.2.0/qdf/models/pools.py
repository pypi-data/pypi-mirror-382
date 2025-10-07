"""
Pools data models
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class PoolSummary(BaseModel):
    """Pool summary data"""
    pool_id: str
    qdf_id: Optional[str] = None
    chain: str
    project: str
    symbol: str
    pool_type: Optional[str] = None

    # Financial metrics
    tvl_usd: float
    apy: Optional[float] = Field(None, alias='apy_processed')
    apy_base: Optional[float] = None
    apy_reward: Optional[float] = None
    volume_24h: Optional[float] = None
    volume_7d: Optional[float] = None
    fee_24h_estimated: Optional[float] = None

    # Risk metrics
    pool_health: Optional[str] = None
    il_risk: Optional[Union[str, float]] = None  # Can be string label or numeric value
    concentration_risk: Optional[Union[str, float]] = None  # Can be string label or numeric value
    impermanent_loss_30d: Optional[float] = None

    # Momentum
    momentum_category: Optional[str] = None
    is_trending: bool = False
    tvl_change_7d: Optional[float] = None
    apy_change_7d: Optional[float] = None

    # Protocol info
    protocol_age_days: Optional[int] = None
    audited: Optional[bool] = None

    class Config:
        populate_by_name = True


class PoolDetail(PoolSummary):
    """Detailed pool information"""
    # Additional detailed fields
    token_count: Optional[int] = None
    underlying_tokens: Optional[List[str]] = None
    reward_tokens: Optional[List[str]] = None

    # Historical data
    tvl_history: Optional[List[Dict[str, Any]]] = None
    apy_history: Optional[List[Dict[str, Any]]] = None
    volume_history: Optional[List[Dict[str, Any]]] = None

    # Risk details
    risk_factors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scanned_at: Optional[datetime] = None


class PoolStats(BaseModel):
    """Aggregate pool statistics"""
    total_count: int
    total_tvl: float
    average_apy: float
    median_apy: Optional[float] = None
    average_tvl: Optional[float] = None
    median_tvl: Optional[float] = None

    # Distributions
    chain_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    project_distribution: Dict[str, int]
    health_distribution: Dict[str, int]

    # Top performers
    highest_apy_pools: Optional[List[PoolSummary]] = None
    highest_tvl_pools: Optional[List[PoolSummary]] = None

    # Time range
    time_range: Optional[str] = None
    last_updated: Optional[datetime] = None