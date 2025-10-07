"""
Rankings data models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ScoreComponents(BaseModel):
    """Individual scoring components"""
    apy_score: Optional[float] = None
    tvl_score: Optional[float] = None
    volume_score: Optional[float] = None
    fee_score: Optional[float] = None
    risk_score: Optional[float] = None
    age_score: Optional[float] = None
    concentration_score: Optional[float] = None


class RankedPool(BaseModel):
    """Ranked pool data"""
    pool_id: str
    qdf_id: Optional[str] = None
    chain: str
    project: str
    symbol: str
    pool_type: Optional[str] = None

    # Ranking data
    ranking_score: float
    rank_overall: int
    rank_in_type: Optional[int] = None
    rank_in_chain: Optional[int] = None
    percentile_overall: Optional[float] = None
    percentile_in_type: Optional[float] = None

    # Scores
    momentum_score: Optional[float] = None
    volume_score: Optional[float] = None
    fee_score: Optional[float] = None
    score_components: Optional[ScoreComponents] = None

    # Pool health
    pool_health: Optional[str] = None
    health_warnings: Optional[List[str]] = None

    # IQR statistics (Interquartile Range analysis)
    pool_label: Optional[str] = None  # e.g., "GiantTVL-HighVol-HighYield"
    tvl_iqr_level: Optional[int] = None  # TVL quartile level (1-5)
    volume_iqr_level: Optional[int] = None  # Volume quartile level
    yield_iqr_level: Optional[int] = None  # Yield quartile level
    is_statistical_outlier: Optional[bool] = None  # Statistical anomaly flag

    # Financial metrics
    apy: Optional[float] = Field(None, alias='apy_processed')
    tvl_usd: Optional[float] = None
    volume_24h: Optional[float] = None
    fee_24h: Optional[float] = None
    tvl_fee_ratio: Optional[float] = None  # TVL to fee ratio

    # Change rates
    protocol_change_1d: Optional[float] = None  # 24h change rate
    protocol_change_7d: Optional[float] = None  # 7d change rate

    # Trends
    is_trending: Optional[bool] = None
    momentum_category: Optional[str] = None

    class Config:
        populate_by_name = True


class RankingChange(BaseModel):
    """Ranking change information"""
    current_rank: int
    previous_rank: Optional[int] = None
    rank_change: Optional[int] = None
    change_percentage: Optional[float] = None
    change_direction: Optional[str] = None  # 'up', 'down', 'stable', 'new'


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int

class RankingsResponse(BaseModel):
    """Paginated rankings response"""
    success: bool = True
    data: List[RankedPool]
    pagination: PaginationInfo
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class RankingSession(BaseModel):
    """Ranking session metadata"""
    session_id: str
    created_at: datetime
    formula_version: str
    market_regime: Optional[str] = None
    total_pools_scanned: int
    pools_after_filtering: int
    execution_time_seconds: Optional[float] = None
    status: str