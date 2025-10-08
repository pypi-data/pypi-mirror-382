"""
Macro economics data models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MacroLiveData(BaseModel):
    """Live macro economic data"""
    # Crypto prices - all Optional now
    btc_price: Optional[float] = None
    eth_price: Optional[float] = None
    btc_change_24h: Optional[float] = None
    eth_change_24h: Optional[float] = None
    btc_dominance: Optional[float] = None

    # Market metrics
    total_market_cap: Optional[float] = None
    defi_tvl: Optional[float] = None
    defi_tvl_change_24h: Optional[float] = None

    # Gas and fees
    eth_gas_price: Optional[int] = None
    eth_gas_price_gwei: Optional[float] = None

    # Market indicators
    fear_greed_index: Optional[int] = None
    fear_greed_label: Optional[str] = None
    vix_crypto: Optional[float] = None

    # Regime
    market_regime: Optional[int] = None  # Can be int (0-5) from database
    trend_direction: Optional[str] = None
    volatility_level: Optional[str] = None

    # Timestamp
    timestamp: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Additional database fields
    crypto_fear_greed: Optional[float] = None
    market_regime_name: Optional[str] = None
    vix_index: Optional[float] = None
    btc_volatility_24h_range_pct: Optional[float] = None
    eth_price_change_24h_pct: Optional[float] = None
    dex_volume_24h_usd: Optional[float] = None


class MarketRegime(BaseModel):
    """Market regime classification"""
    regime: str  # 'bull', 'bear', 'neutral', 'volatile'
    confidence: float  # 0-1 confidence score
    trend_strength: Optional[float] = None
    volatility: Optional[str] = None  # 'low', 'medium', 'high'

    # Supporting indicators
    indicators: Dict[str, Any]
    signals: List[str]

    # Time info
    regime_start_date: Optional[datetime] = None
    days_in_regime: Optional[int] = None
    previous_regime: Optional[str] = None

    timestamp: datetime


class MarketAnalysis(BaseModel):
    """Detailed market analysis"""
    # Current state
    market_regime: str
    trend_direction: str  # 'bullish', 'bearish', 'sideways'
    volatility_level: str  # 'low', 'medium', 'high', 'extreme'
    risk_level: str  # 'low', 'medium', 'high', 'extreme'

    # Key metrics
    key_indicators: Dict[str, float]
    market_signals: List[str]
    risk_factors: List[str]
    opportunities: List[str]

    # Recommendations
    recommendations: List[str]
    suggested_actions: List[str]
    pools_to_watch: Optional[List[str]] = None

    # Analysis metadata
    analysis_version: str
    confidence_score: float
    timestamp: datetime


class FearGreedData(BaseModel):
    """Fear and Greed Index data"""
    value: int  # 0-100
    label: str  # 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
    timestamp: datetime

    # Historical data
    change_24h: Optional[int] = None
    change_7d: Optional[int] = None

    # Components (if available)
    components: Optional[Dict[str, float]] = None


class MacroIndicator(BaseModel):
    """Generic macro indicator"""
    indicator: str
    value: float
    change_pct: Optional[float] = None
    change_value: Optional[float] = None
    timestamp: datetime
    source: Optional[str] = None