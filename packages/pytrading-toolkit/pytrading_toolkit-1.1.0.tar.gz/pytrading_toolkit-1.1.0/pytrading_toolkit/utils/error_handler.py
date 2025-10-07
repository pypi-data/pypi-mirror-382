#!/usr/bin/env python3
"""
에러 처리 유틸리티 모듈
공통 에러 처리 로직을 패키지에서 제공
"""

import time
import logging
import functools
from datetime import datetime, timezone
from typing import Callable, Any, Optional, Dict, List
from enum import Enum
import requests
import json

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """에러 타입"""
    NETWORK = "network"
    API = "api"
    DATA = "data"
    CONFIG = "config"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    """에러 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RetryConfig:
    """재시도 설정"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

class ErrorHandler:
    """에러 처리 클래스"""
    
    def __init__(self, telegram_notifier=None):
        self.telegram_notifier = telegram_notifier
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}
        
        # 에러 타입별 재시도 설정
        self.retry_configs = {
            ErrorType.NETWORK: RetryConfig(max_retries=5, base_delay=1.0),
            ErrorType.API: RetryConfig(max_retries=3, base_delay=2.0),
            ErrorType.DATA: RetryConfig(max_retries=2, base_delay=1.0),
            ErrorType.CONFIG: RetryConfig(max_retries=1, base_delay=0.0),
            ErrorType.UNKNOWN: RetryConfig(max_retries=2, base_delay=1.0)
        }
    
    def classify_error(self, error: Exception) -> tuple[ErrorType, ErrorSeverity]:
        """에러 분류"""
        try:
            error_str = str(error).lower()
            
            # 네트워크 에러
            if any(keyword in error_str for keyword in ['connection', 'timeout', 'network', 'unreachable']):
                return ErrorType.NETWORK, ErrorSeverity.MEDIUM
            
            # API 에러
            if any(keyword in error_str for keyword in ['api', 'http', 'status', 'unauthorized', 'forbidden']):
                if '401' in error_str or '403' in error_str:
                    return ErrorType.API, ErrorSeverity.HIGH
                elif '429' in error_str:  # Rate limit
                    return ErrorType.API, ErrorSeverity.MEDIUM
                else:
                    return ErrorType.API, ErrorSeverity.MEDIUM
            
            # 데이터 에러
            if any(keyword in error_str for keyword in ['json', 'decode', 'parse', 'format', 'invalid']):
                return ErrorType.DATA, ErrorSeverity.LOW
            
            # 설정 에러
            if any(keyword in error_str for keyword in ['config', 'setting', 'key', 'missing']):
                return ErrorType.CONFIG, ErrorSeverity.HIGH
            
            # 알 수 없는 에러
            return ErrorType.UNKNOWN, ErrorSeverity.MEDIUM
            
        except Exception as e:
            logger.error(f"에러 분류 실패: {e}")
            return ErrorType.UNKNOWN, ErrorSeverity.MEDIUM
    
    def should_retry(self, error: Exception, retry_count: int) -> bool:
        """재시도 여부 확인"""
        try:
            error_type, severity = self.classify_error(error)
            
            # 심각한 에러는 재시도하지 않음
            if severity == ErrorSeverity.CRITICAL:
                return False
            
            # 설정 에러는 재시도하지 않음
            if error_type == ErrorType.CONFIG:
                return False
            
            # 재시도 횟수 확인
            config = self.retry_configs.get(error_type, self.retry_configs[ErrorType.UNKNOWN])
            return retry_count < config.max_retries
            
        except Exception as e:
            logger.error(f"재시도 여부 확인 실패: {e}")
            return False
    
    def get_retry_delay(self, error: Exception, retry_count: int) -> float:
        """재시도 지연 시간 계산"""
        try:
            error_type, _ = self.classify_error(error)
            config = self.retry_configs.get(error_type, self.retry_configs[ErrorType.UNKNOWN])
            
            # 지수 백오프
            delay = min(config.base_delay * (config.backoff_factor ** retry_count), config.max_delay)
            return delay
            
        except Exception as e:
            logger.error(f"재시도 지연 시간 계산 실패: {e}")
            return 1.0
    
    def log_error(self, error: Exception, context: str = "", retry_count: int = 0):
        """에러 로깅"""
        try:
            error_type, severity = self.classify_error(error)
            error_key = f"{error_type.value}_{context}"
            
            # 에러 카운트 증가
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            self.last_error_time[error_key] = datetime.now(timezone.utc)
            
            # 로그 레벨 결정
            if severity == ErrorSeverity.CRITICAL:
                log_level = logging.CRITICAL
            elif severity == ErrorSeverity.HIGH:
                log_level = logging.ERROR
            elif severity == ErrorSeverity.MEDIUM:
                log_level = logging.WARNING
            else:
                log_level = logging.INFO
            
            # 로그 메시지
            message = f"[{error_type.value.upper()}] {context}: {str(error)}"
            if retry_count > 0:
                message += f" (재시도 {retry_count}회)"
            
            logger.log(log_level, message)
            
            # 텔레그램 알림 (심각한 에러만)
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] and self.telegram_notifier:
                try:
                    self.telegram_notifier.send_error(f"🚨 {context}: {str(error)}")
                except Exception as e:
                    logger.error(f"텔레그램 알림 전송 실패: {e}")
            
        except Exception as e:
            logger.error(f"에러 로깅 실패: {e}")
    
    def retry_with_backoff(self, func: Callable, *args, context: str = "", **kwargs) -> Any:
        """백오프를 사용한 재시도"""
        retry_count = 0
        last_error = None
        
        while retry_count <= 3:  # 최대 3회 재시도
            try:
                return func(*args, **kwargs)
            except Exception as error:
                last_error = error
                
                # 에러 로깅
                self.log_error(error, context, retry_count)
                
                # 재시도 여부 확인
                if not self.should_retry(error, retry_count):
                    break
                
                # 재시도 지연
                delay = self.get_retry_delay(error, retry_count)
                logger.info(f"{context} 재시도 {retry_count + 1}회 - {delay:.1f}초 후")
                time.sleep(delay)
                
                retry_count += 1
        
        # 모든 재시도 실패
        if last_error:
            raise last_error
    
    def handle_api_error(self, error: Exception, context: str = "") -> bool:
        """API 에러 처리"""
        try:
            error_type, severity = self.classify_error(error)
            
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(f"치명적 API 에러: {context} - {error}")
                return False
            
            elif severity == ErrorSeverity.HIGH:
                logger.error(f"심각한 API 에러: {context} - {error}")
                # API 키 문제 등은 즉시 중단
                return False
            
            else:
                logger.warning(f"API 에러 (재시도 가능): {context} - {error}")
                return True
                
        except Exception as e:
            logger.error(f"API 에러 처리 실패: {e}")
            return False
    
    def handle_network_error(self, error: Exception, context: str = "") -> bool:
        """네트워크 에러 처리"""
        try:
            error_type, severity = self.classify_error(error)
            
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(f"치명적 네트워크 에러: {context} - {error}")
                return False
            
            else:
                logger.warning(f"네트워크 에러 (재시도 가능): {context} - {error}")
                return True
                
        except Exception as e:
            logger.error(f"네트워크 에러 처리 실패: {e}")
            return False
    
    def validate_data(self, data: Any, required_fields: List[str] = None) -> bool:
        """데이터 유효성 검증"""
        try:
            if data is None:
                logger.warning("데이터가 None입니다")
                return False
            
            if isinstance(data, dict):
                if required_fields:
                    for field in required_fields:
                        if field not in data:
                            logger.warning(f"필수 필드 누락: {field}")
                            return False
                
                # 빈 딕셔너리 확인
                if not data:
                    logger.warning("빈 데이터입니다")
                    return False
            
            elif isinstance(data, list):
                if not data:
                    logger.warning("빈 리스트입니다")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"데이터 유효성 검증 실패: {e}")
            return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 반환"""
        try:
            return {
                "error_counts": self.error_counts.copy(),
                "last_error_times": {k: v.isoformat() for k, v in self.last_error_time.items()},
                "total_errors": sum(self.error_counts.values())
            }
        except Exception as e:
            logger.error(f"에러 통계 조회 실패: {e}")
            return {}

def retry_on_error(error_handler: ErrorHandler = None, context: str = ""):
    """에러 재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if error_handler:
                return error_handler.retry_with_backoff(func, *args, context=context, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return=None, context: str = "", **kwargs):
    """안전한 함수 실행"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{context} 실행 실패: {e}")
        return default_return

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 에러 처리 테스트")
    
    # 에러 핸들러 초기화
    error_handler = ErrorHandler()
    
    # 테스트 함수
    def test_function(success: bool = True):
        if success:
            return "성공"
        else:
            raise ConnectionError("연결 실패")
    
    # 재시도 테스트
    print("재시도 테스트 (실패)")
    try:
        result = error_handler.retry_with_backoff(test_function, False, context="테스트")
    except Exception as e:
        print(f"최종 실패: {e}")
    
    print("\n재시도 테스트 (성공)")
    result = error_handler.retry_with_backoff(test_function, True, context="테스트")
    print(f"결과: {result}")
    
    # 에러 통계
    print(f"\n에러 통계: {error_handler.get_error_stats()}")
