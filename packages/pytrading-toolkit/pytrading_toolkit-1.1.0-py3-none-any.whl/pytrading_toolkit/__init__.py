"""
PyTrading Toolkit - Python 암호화폐 트레이딩 봇 개발을 위한 포괄적인 도구킷

이 패키지는 암호화폐 자동 거래 봇 개발을 위한 포괄적인 도구들을 제공합니다.

주요 기능:
- 거래소별 설정 관리 (Upbit, Bybit)
- 기술지표 계산 및 분석
- 실시간 알림 시스템 (Telegram)
- 고급 로깅 및 모니터링
- 보안 및 접근 제어
- 통합 시스템 관리
- 자동 복구 및 장애 대응

지원 거래소:
- Upbit (업비트)
- Bybit (바이비트)
- 향후: Binance, Coinbase, Kraken

버전: 0.1.0
라이선스: MIT
"""

__version__ = "1.1.0"
__author__ = "PyTrading Toolkit Team"
__email__ = "contact@pytrading-toolkit.com"
__description__ = "Python 암호화폐 트레이딩 봇 개발을 위한 포괄적인 도구킷"


# 주요 클래스들을 최상위에서 import 가능하게 함
from .config.base import BaseConfigLoader
from .config.exchange import UpbitConfigLoader, BybitConfigLoader
from .config.master_config_loader import MasterConfigLoader
from .notifications.telegram import TelegramNotifier
from .logging.setup import setup_logger

# 헬스체크 및 모니터링
from .health.monitor import HealthMonitor
from .health.simple_detector import SimpleMaintenanceDetector
from .health.maintenance_detector import AdvancedMaintenanceDetector, RobustMaintenanceConfig

# 거래 모듈들
from .trading.bybit_trader import BybitTrader
from .trading.bybit_data_manager import BybitDataManager
from .trading.position_manager import PositionManager, Position, PositionSide, PositionStatus

# 유틸리티 함수들
from .utils.time_utils import get_kst_now, get_utc_now
from .utils.data_utils import safe_get
from .utils.error_handler import ErrorHandler, ErrorType, ErrorSeverity, RetryConfig, retry_on_error, safe_execute
from .utils.connection_manager import ConnectionManager, ConnectionStatus
from .utils.data_validator import DataValidator, ValidationResult
from .utils.performance_monitor import PerformanceMonitor, PerformanceMetrics, APIMetrics, CacheMetrics
from .utils.cache_manager import CacheManager, CacheEntry, get_global_cache, cached
from .utils.async_manager import AsyncManager, AsyncTask, get_global_async_manager, submit_task, submit_async_task
from .utils.advanced_logger import AdvancedLogger, LogEntry, LogRotator, LogFormatter, get_logger, cleanup_all_loggers
from .utils.log_analyzer import LogAnalyzer, LogAnalysisResult
from .utils.log_monitor import LogMonitor, create_error_alert_callback, create_performance_alert_callback

# 보안 모듈들
from .security.encryption import SecureStorage, APIKeyManager, PasswordManager, DataMasker
from .security.access_control import AccessControlManager, User, Session, Permission, Role
from .security.audit_logger import SecurityAuditLogger, SecurityEvent, SecurityEventType, SecurityLevel

# 통합 시스템 모듈들
from .core.system_manager import SystemManager, SystemStatus
from .core.dashboard import SystemDashboard, DashboardData
from .core.auto_recovery import AutoRecoverySystem, FailureEvent, FailureType, RecoveryAction, RecoveryPlan

__all__ = [
    # Config
    "BaseConfigLoader",
    "UpbitConfigLoader",
    "BybitConfigLoader",
    "MasterConfigLoader",
    
    # Notifications  
    "TelegramNotifier",
    
    # Logging
    "setup_logger",
    
    # Health & Monitoring
    "HealthMonitor",
    "SimpleMaintenanceDetector", 
    "AdvancedMaintenanceDetector",
    "RobustMaintenanceConfig",
    
    # Trading
    "BybitTrader",
    "BybitDataManager",
    "PositionManager",
    "Position",
    "PositionSide", 
    "PositionStatus",
    
    # Utils
    "get_kst_now",
    "get_utc_now", 
    "safe_get",
    "ErrorHandler",
    "ErrorType",
    "ErrorSeverity",
    "RetryConfig",
    "retry_on_error",
    "safe_execute",
    "ConnectionManager",
    "ConnectionStatus",
    "DataValidator",
    "ValidationResult",
    "PerformanceMonitor",
    "PerformanceMetrics",
    "APIMetrics",
    "CacheMetrics",
    "CacheManager",
    "CacheEntry",
    "get_global_cache",
    "cached",
    "AsyncManager",
    "AsyncTask",
    "get_global_async_manager",
    "submit_task",
    "submit_async_task",
    "AdvancedLogger",
    "LogEntry",
    "LogRotator",
    "LogFormatter",
    "get_logger",
    "cleanup_all_loggers",
    "LogAnalyzer",
    "LogAnalysisResult",
    "LogMonitor",
    "create_error_alert_callback",
    "create_performance_alert_callback",
    
    # Security
    "SecureStorage",
    "APIKeyManager",
    "PasswordManager",
    "DataMasker",
    "AccessControlManager",
    "User",
    "Session",
    "Permission",
    "Role",
    "SecurityAuditLogger",
    "SecurityEvent",
    "SecurityEventType",
    "SecurityLevel",
    
    # Core System
    "SystemManager",
    "SystemStatus",
    "SystemDashboard",
    "DashboardData",
    "AutoRecoverySystem",
    "FailureEvent",
    "FailureType",
    "RecoveryAction",
    "RecoveryPlan",
    
    # Indicators (동적 import)
    "indicators",
]

# 지연 import를 위한 indicators 모듈
class _IndicatorsModule:
    """지연 import를 위한 indicators 래퍼"""
    
    def __getattr__(self, name):
        from .indicators import manager
        return getattr(manager, name)

indicators = _IndicatorsModule()

# 버전 정보
def get_version():
    """패키지 버전 반환"""
    return __version__

def get_info():
    """패키지 정보 반환"""
    return {
        "name": "pytrading-toolkit",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": "Python 암호화폐 트레이딩 봇 개발 툴킷"
    }
