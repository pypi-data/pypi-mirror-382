"""기술지표 계산 모듈 (TA-Lib 기반)"""

from .manager import (
    calculate_indicators,
    get_market_sentiment,
    calculate_support_resistance,
    calculate_trend_indicators,
    IndicatorManager
)

# TA-Lib 기반 고급 지표 계산 (추가 기능)
try:
    from .talib_manager import (
        calculate_advanced_indicators_talib,
        get_market_sentiment_talib,
        calculate_trend_indicators_talib,
        get_talib_version,
        TALibIndicatorManager
    )
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

__all__ = [
    "calculate_indicators",
    "get_market_sentiment", 
    "calculate_support_resistance",
    "calculate_trend_indicators",
    "IndicatorManager"
]

# TA-Lib이 사용 가능한 경우 추가 export
if TALIB_AVAILABLE:
    __all__.extend([
        "calculate_advanced_indicators_talib", 
        "get_market_sentiment_talib",
        "calculate_trend_indicators_talib",
        "get_talib_version",
        "TALibIndicatorManager",
        "TALIB_AVAILABLE"
    ])
