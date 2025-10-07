#!/usr/bin/env python3
"""
고급 점검 감지 시스템
업비트와 바이비트 시스템에서 공통으로 사용
"""

import threading
import time
import requests
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import queue
import weakref
import gc
import os
import signal
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib

from .simple_detector import SimpleMaintenanceDetector, MaintenanceEvent

logger = logging.getLogger(__name__)

# 전역 설정
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_BASE = 1.0
MAX_CACHE_SIZE = 1000
HEALTH_CHECK_INTERVAL = 300  # 5분

@dataclass
class APICacheEntry:
    """API 응답 캐시 엔트리"""
    timestamp: datetime
    status: Any
    response_time: float
    hash: str

class RobustMaintenanceConfig:
    """강화된 점검 설정 관리"""
    
    def __init__(self, custom_config: Dict = None):
        # 기본 설정 (안전한 값들)
        self.config = {
            # API 설정
            'api_timeout': 10,
            'website_timeout': 15,
            'max_retry_attempts': 3,
            'retry_delay_base': 1.0,
            'retry_delay_max': 60.0,
            
            # 점검 감지 설정
            'check_interval': 30,
            'response_delay_threshold': 8.0,
            'required_success': 3,
            
            # 재시작 설정
            'max_restart_attempts': 5,
            'restart_delay': 300,
            
            # 캐시 설정
            'api_cache_duration': 10,
            'max_cache_size': 1000,
            
            # 로그 설정
            'max_log_size_mb': 100,
            'log_rotation_count': 5,
            
            # 메모리 설정
            'memory_cleanup_interval': 600,
            'max_memory_usage_mb': 500
        }
        
        if custom_config:
            self._safe_update(custom_config)
    
    def _safe_update(self, custom_config: Dict):
        """안전한 설정 업데이트 (타입 검증 포함)"""
        for key, value in custom_config.items():
            if key in self.config:
                # 타입 검증 및 안전한 값 설정
                expected_type = type(self.config[key])
                try:
                    if expected_type == int:
                        self.config[key] = max(1, int(value))
                    elif expected_type == float:
                        self.config[key] = max(0.1, float(value))
                    elif expected_type == bool:
                        self.config[key] = bool(value)
                    else:
                        self.config[key] = value
                except (ValueError, TypeError):
                    logger.warning(f"설정 값 타입 오류 무시: {key}={value}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회 (기본값 포함)"""
        return self.config.get(key, default)
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        try:
            # 필수 설정 검증
            required_keys = ['api_timeout', 'check_interval', 'required_success']
            for key in required_keys:
                if key not in self.config:
                    logger.error(f"필수 설정 누락: {key}")
                    return False
            
            # 값 범위 검증
            if self.config['api_timeout'] <= 0:
                logger.error("API 타임아웃은 0보다 커야 합니다")
                return False
            
            if self.config['check_interval'] <= 0:
                logger.error("체크 간격은 0보다 커야 합니다")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"설정 유효성 검사 오류: {e}")
            return False

class AdvancedMaintenanceDetector(SimpleMaintenanceDetector):
    """고급 점검 감지 시스템"""
    
    def __init__(self, system_name: str, config: RobustMaintenanceConfig = None, 
                 telegram_notifier=None, enable_cache: bool = True):
        super().__init__(system_name, telegram_notifier)
        
        # 고급 설정
        self.robust_config = config or RobustMaintenanceConfig()
        self.enable_cache = enable_cache
        
        # 고급 기능 초기화
        self._init_advanced_features()
        
        logger.info(f"{system_name} 고급 점검 감지 시스템 초기화 완료")
    
    def _init_advanced_features(self):
        """고급 기능 초기화"""
        # API 캐시
        if self.enable_cache:
            self.api_cache = {}
            self.cache_cleanup_timer = 0
        
        # 점검 예측
        self.maintenance_patterns = []
        self.prediction_model = None
        
        # 성능 모니터링
        self.performance_metrics = {
            'response_times': [],
            'error_rates': [],
            'uptime_percentage': 100.0
        }
        
        # 메모리 관리
        self.memory_cleanup_timer = 0
    
    def _check_api_status(self) -> Dict[str, Any]:
        """고급 API 상태 확인"""
        try:
            # 캐시 확인
            if self.enable_cache:
                cached_result = self._get_cached_result()
                if cached_result:
                    return cached_result
            
            # 실제 API 체크
            start_time = time.time()
            result = self._perform_api_check()
            response_time = time.time() - start_time
            
            # 결과에 응답 시간 추가
            result['response_time'] = response_time
            result['timestamp'] = datetime.now(timezone.utc)
            
            # 캐시에 저장
            if self.enable_cache:
                self._cache_result(result)
            
            # 성능 메트릭 업데이트
            self._update_performance_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"고급 API 상태 확인 오류: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'response_time': 0,
                'timestamp': datetime.now(timezone.utc)
            }
    
    def _perform_api_check(self) -> Dict[str, Any]:
        """실제 API 체크 수행 (하위 클래스에서 구현)"""
        # 기본 구현: 간단한 HTTP 체크
        try:
            # 시스템별 API 엔드포인트 설정
            api_url = self._get_api_endpoint()
            
            response = requests.get(
                api_url, 
                timeout=self.robust_config.get('api_timeout'),
                headers={'User-Agent': f'{self.system_name}-HealthCheck/1.0'}
            )
            
            if response.status_code == 200:
                return {
                    'healthy': True,
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            else:
                return {
                    'healthy': False,
                    'status_code': response.status_code,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'healthy': False,
                'error': 'timeout',
                'status_code': None
            }
        except requests.exceptions.ConnectionError:
            return {
                'healthy': False,
                'error': 'connection_error',
                'status_code': None
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'status_code': None
            }
    
    def _get_api_endpoint(self) -> str:
        """API 엔드포인트 반환 (하위 클래스에서 구현)"""
        # 기본값: 업비트 API
        return "https://api.upbit.com/v1/market/all"
    
    def _get_cached_result(self) -> Optional[Dict[str, Any]]:
        """캐시된 결과 조회"""
        if not self.enable_cache:
            return None
        
        current_time = datetime.now(timezone.utc)
        cache_key = f"{self.system_name}_api_status"
        
        if cache_key in self.api_cache:
            entry = self.api_cache[cache_key]
            cache_age = (current_time - entry.timestamp).total_seconds()
            
            if cache_age < self.robust_config.get('api_cache_duration'):
                return {
                    'healthy': entry.status,
                    'response_time': entry.response_time,
                    'cached': True
                }
        
        return None
    
    def _cache_result(self, result: Dict[str, Any]):
        """결과를 캐시에 저장"""
        if not self.enable_cache:
            return
        
        current_time = datetime.now(timezone.utc)
        cache_key = f"{self.system_name}_api_status"
        
        # 캐시 크기 제한
        if len(self.api_cache) >= self.robust_config.get('max_cache_size'):
            self._cleanup_cache()
        
        # 새 엔트리 저장
        entry = APICacheEntry(
            timestamp=current_time,
            status=result.get('healthy', False),
            response_time=result.get('response_time', 0),
            hash=hashlib.md5(str(result).encode()).hexdigest()
        )
        
        self.api_cache[cache_key] = entry
    
    def _cleanup_cache(self):
        """캐시 정리"""
        if not self.api_cache:
            return
        
        # 가장 오래된 항목 제거
        oldest_key = min(self.api_cache.keys(), 
                        key=lambda k: self.api_cache[k].timestamp)
        del self.api_cache[oldest_key]
        
        logger.debug("API 캐시 정리 완료")
    
    def _update_performance_metrics(self, result: Dict[str, Any]):
        """성능 메트릭 업데이트"""
        response_time = result.get('response_time', 0)
        
        # 응답 시간 기록
        self.performance_metrics['response_times'].append(response_time)
        if len(self.performance_metrics['response_times']) > 100:
            self.performance_metrics['response_times'].pop(0)
        
        # 에러율 업데이트
        is_error = not result.get('healthy', True)
        self.performance_metrics['error_rates'].append(1 if is_error else 0)
        if len(self.performance_metrics['error_rates']) > 100:
            self.performance_metrics['error_rates'].pop(0)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 반환"""
        response_times = self.performance_metrics['response_times']
        error_rates = self.performance_metrics['error_rates']
        
        return {
            'response_time': {
                'current': response_times[-1] if response_times else 0,
                'average': sum(response_times) / len(response_times) if response_times else 0,
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0
            },
            'error_rate': {
                'current': error_rates[-1] if error_rates else 0,
                'average': sum(error_rates) / len(error_rates) if error_rates else 0
            },
            'uptime_percentage': self.performance_metrics['uptime_percentage']
        }
    
    def predict_maintenance(self) -> Optional[Dict[str, Any]]:
        """점검 예측 (기본 구현)"""
        # 기본적인 패턴 기반 예측
        if len(self.maintenance_history) < 3:
            return None
        
        # 최근 점검 패턴 분석
        recent_maintenance = [e for e in self.maintenance_history[-10:] 
                            if e.event_type == 'start']
        
        if len(recent_maintenance) >= 2:
            # 간격 계산
            intervals = []
            for i in range(1, len(recent_maintenance)):
                interval = (recent_maintenance[i].timestamp - 
                           recent_maintenance[i-1].timestamp).total_seconds() / 3600
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                last_maintenance = recent_maintenance[-1].timestamp
                next_predicted = last_maintenance + timedelta(hours=avg_interval)
                
                return {
                    'type': 'scheduled',
                    'next_time': next_predicted,
                    'confidence': min(0.8, len(intervals) / 10),  # 신뢰도
                    'pattern': f"평균 {avg_interval:.1f}시간 간격"
                }
        
        return None
    
    def cleanup_resources(self):
        """리소스 정리"""
        try:
            # 캐시 정리
            if self.enable_cache:
                self.api_cache.clear()
            
            # 메모리 정리
            gc.collect()
            
            logger.info("리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"리소스 정리 오류: {e}")
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """상세 상태 정보 반환"""
        base_status = super().get_maintenance_status()
        performance = self.get_performance_metrics()
        prediction = self.predict_maintenance()
        
        return {
            **base_status,
            'performance': performance,
            'prediction': prediction,
            'cache_enabled': self.enable_cache,
            'cache_size': len(self.api_cache) if self.enable_cache else 0,
            'robust_config': {
                'api_timeout': self.robust_config.get('api_timeout'),
                'check_interval': self.robust_config.get('check_interval'),
                'required_success': self.robust_config.get('required_success')
            }
        }
