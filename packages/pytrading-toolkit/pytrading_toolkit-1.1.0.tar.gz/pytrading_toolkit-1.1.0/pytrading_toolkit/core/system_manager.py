#!/usr/bin/env python3
"""
통합 시스템 관리 모듈
전체 시스템의 통합 관리 및 조정
"""

import os
import time
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import json
import yaml

# 내부 모듈들
from ..config.base import BaseConfigLoader
from ..config.exchange.upbit import UpbitConfigLoader
from ..trading.bybit_trader import BybitTrader
from ..trading.bybit_data_manager import BybitDataManager
from ..trading.position_manager import PositionManager
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.cache_manager import CacheManager
from ..utils.async_manager import AsyncManager
from ..utils.advanced_logger import get_logger
from ..utils.error_handler import ErrorHandler
from ..utils.connection_manager import ConnectionManager
from ..security.encryption import SecureStorage, APIKeyManager
from ..security.access_control import AccessControlManager
from ..security.audit_logger import SecurityAuditLogger

logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """시스템 상태"""
    is_running: bool
    start_time: datetime
    uptime_seconds: float
    components: Dict[str, bool]
    performance: Dict[str, Any]
    security: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class SystemManager:
    """통합 시스템 관리자"""
    
    def __init__(self, config_dir: str = "config", log_dir: str = "logs"):
        self.config_dir = Path(config_dir)
        self.log_dir = Path(log_dir)
        
        # 디렉토리 생성
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 시스템 상태
        self.is_running = False
        self.start_time = None
        self.components = {}
        self.errors = []
        self.warnings = []
        
        # 핵심 컴포넌트들
        self.config_loader = None
        self.secure_storage = None
        self.api_manager = None
        self.access_control = None
        self.audit_logger = None
        self.performance_monitor = None
        self.cache_manager = None
        self.async_manager = None
        self.connection_manager = None
        self.error_handler = None
        
        # 거래 시스템들
        self.traders = {}
        self.data_managers = {}
        self.position_managers = {}
        
        # 로거
        self.logger = get_logger("system_manager", str(self.log_dir))
        
        # 이벤트 콜백
        self.event_callbacks = {
            "system_start": [],
            "system_stop": [],
            "component_error": [],
            "performance_alert": [],
            "security_alert": []
        }
        
        # 모니터링 스레드
        self.monitoring = False
        self.monitor_thread = None
    
    def initialize_system(self) -> bool:
        """시스템 초기화"""
        try:
            self.logger.info("시스템 초기화 시작")
            
            # 1. 보안 시스템 초기화
            if not self._initialize_security():
                return False
            
            # 2. 설정 시스템 초기화
            if not self._initialize_config():
                return False
            
            # 3. 로깅 시스템 초기화
            if not self._initialize_logging():
                return False
            
            # 4. 성능 모니터링 초기화
            if not self._initialize_performance():
                return False
            
            # 5. 캐시 시스템 초기화
            if not self._initialize_cache():
                return False
            
            # 6. 비동기 처리 초기화
            if not self._initialize_async():
                return False
            
            # 7. 연결 관리 초기화
            if not self._initialize_connections():
                return False
            
            # 8. 에러 처리 초기화
            if not self._initialize_error_handling():
                return False
            
            # 9. 거래 시스템 초기화
            if not self._initialize_trading_systems():
                return False
            
            self.logger.info("시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"시스템 초기화 실패: {e}")
            self.errors.append(f"시스템 초기화 실패: {e}")
            return False
    
    def _initialize_security(self) -> bool:
        """보안 시스템 초기화"""
        try:
            # 보안 저장소
            self.secure_storage = SecureStorage()
            self.components["secure_storage"] = True
            
            # API 키 관리자
            self.api_manager = APIKeyManager(self.secure_storage)
            self.components["api_manager"] = True
            
            # 접근 제어
            self.access_control = AccessControlManager()
            self.components["access_control"] = True
            
            # 보안 감사 로거
            self.audit_logger = SecurityAuditLogger(str(self.log_dir / "audit"))
            self.components["audit_logger"] = True
            
            self.logger.info("보안 시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"보안 시스템 초기화 실패: {e}")
            return False
    
    def _initialize_config(self) -> bool:
        """설정 시스템 초기화"""
        try:
            # 업비트 설정 로더
            self.config_loader = UpbitConfigLoader()
            self.components["config_loader"] = True
            
            self.logger.info("설정 시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 시스템 초기화 실패: {e}")
            return False
    
    def _initialize_logging(self) -> bool:
        """로깅 시스템 초기화"""
        try:
            # 고급 로거는 이미 초기화됨
            self.components["logger"] = True
            
            self.logger.info("로깅 시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"로깅 시스템 초기화 실패: {e}")
            return False
    
    def _initialize_performance(self) -> bool:
        """성능 모니터링 초기화"""
        try:
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start_monitoring()
            self.components["performance_monitor"] = True
            
            self.logger.info("성능 모니터링 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"성능 모니터링 초기화 실패: {e}")
            return False
    
    def _initialize_cache(self) -> bool:
        """캐시 시스템 초기화"""
        try:
            self.cache_manager = CacheManager(max_size=2000, default_ttl=600)
            self.cache_manager.start_cleanup()
            self.components["cache_manager"] = True
            
            self.logger.info("캐시 시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"캐시 시스템 초기화 실패: {e}")
            return False
    
    def _initialize_async(self) -> bool:
        """비동기 처리 초기화"""
        try:
            self.async_manager = AsyncManager(max_workers=8, max_queue_size=2000)
            self.async_manager.start()
            self.components["async_manager"] = True
            
            self.logger.info("비동기 처리 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"비동기 처리 초기화 실패: {e}")
            return False
    
    def _initialize_connections(self) -> bool:
        """연결 관리 초기화"""
        try:
            self.connection_manager = ConnectionManager()
            self.connection_manager.start_monitoring()
            self.components["connection_manager"] = True
            
            self.logger.info("연결 관리 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"연결 관리 초기화 실패: {e}")
            return False
    
    def _initialize_error_handling(self) -> bool:
        """에러 처리 초기화"""
        try:
            self.error_handler = ErrorHandler()
            self.components["error_handler"] = True
            
            self.logger.info("에러 처리 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"에러 처리 초기화 실패: {e}")
            return False
    
    def _initialize_trading_systems(self) -> bool:
        """거래 시스템 초기화"""
        try:
            # 바이비트 트레이더
            self.traders["bybit"] = BybitTrader(self.config_loader, test_mode=True)
            self.components["bybit_trader"] = True
            
            # 바이비트 데이터 매니저
            self.data_managers["bybit"] = BybitDataManager(self.config_loader, test_mode=True)
            self.components["bybit_data_manager"] = True
            
            # 포지션 매니저
            self.position_managers["bybit"] = PositionManager(
                self.traders["bybit"], 
                self.config_loader
            )
            self.components["position_manager"] = True
            
            self.logger.info("거래 시스템 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"거래 시스템 초기화 실패: {e}")
            return False
    
    def start_system(self) -> bool:
        """시스템 시작"""
        try:
            if self.is_running:
                self.logger.warning("시스템이 이미 실행 중입니다")
                return True
            
            if not self.initialize_system():
                return False
            
            self.is_running = True
            self.start_time = datetime.now(timezone.utc)
            
            # 모니터링 시작
            self._start_monitoring()
            
            # 이벤트 트리거
            self._trigger_event("system_start", {
                "start_time": self.start_time.isoformat(),
                "components": list(self.components.keys())
            })
            
            self.logger.info("시스템 시작 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"시스템 시작 실패: {e}")
            return False
    
    def stop_system(self) -> bool:
        """시스템 중지"""
        try:
            if not self.is_running:
                self.logger.warning("시스템이 실행 중이 아닙니다")
                return True
            
            self.logger.info("시스템 중지 시작")
            
            # 모니터링 중지
            self._stop_monitoring()
            
            # 컴포넌트들 정리
            self._cleanup_components()
            
            self.is_running = False
            
            # 이벤트 트리거
            self._trigger_event("system_stop", {
                "stop_time": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
            })
            
            self.logger.info("시스템 중지 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"시스템 중지 실패: {e}")
            return False
    
    def _start_monitoring(self):
        """모니터링 시작"""
        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("시스템 모니터링 시작")
        except Exception as e:
            self.logger.error(f"모니터링 시작 실패: {e}")
    
    def _stop_monitoring(self):
        """모니터링 중지"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            self.logger.info("시스템 모니터링 중지")
        except Exception as e:
            self.logger.error(f"모니터링 중지 실패: {e}")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        try:
            while self.monitoring:
                # 컴포넌트 상태 확인
                self._check_component_health()
                
                # 성능 모니터링
                self._check_performance()
                
                # 보안 모니터링
                self._check_security()
                
                # 에러 정리
                self._cleanup_errors()
                
                time.sleep(30)  # 30초마다 확인
                
        except Exception as e:
            self.logger.error(f"모니터링 루프 오류: {e}")
    
    def _check_component_health(self):
        """컴포넌트 상태 확인"""
        try:
            for component_name, is_healthy in self.components.items():
                if not is_healthy:
                    self.warnings.append(f"컴포넌트 비정상: {component_name}")
                    self._trigger_event("component_error", {
                        "component": component_name,
                        "status": "unhealthy"
                    })
        except Exception as e:
            self.logger.error(f"컴포넌트 상태 확인 실패: {e}")
    
    def _check_performance(self):
        """성능 확인"""
        try:
            if self.performance_monitor:
                current_metrics = self.performance_monitor.get_current_metrics()
                if current_metrics:
                    # CPU 사용률 확인
                    if current_metrics.cpu_percent > 90:
                        self.warnings.append(f"높은 CPU 사용률: {current_metrics.cpu_percent:.1f}%")
                        self._trigger_event("performance_alert", {
                            "type": "high_cpu",
                            "value": current_metrics.cpu_percent
                        })
                    
                    # 메모리 사용률 확인
                    if current_metrics.memory_percent > 90:
                        self.warnings.append(f"높은 메모리 사용률: {current_metrics.memory_percent:.1f}%")
                        self._trigger_event("performance_alert", {
                            "type": "high_memory",
                            "value": current_metrics.memory_percent
                        })
        except Exception as e:
            self.logger.error(f"성능 확인 실패: {e}")
    
    def _check_security(self):
        """보안 확인"""
        try:
            if self.audit_logger:
                stats = self.audit_logger.get_stats()
                if stats['risk_events'] > 10:  # 위험 이벤트가 10개 이상
                    self.warnings.append(f"높은 위험 이벤트 수: {stats['risk_events']}")
                    self._trigger_event("security_alert", {
                        "type": "high_risk_events",
                        "count": stats['risk_events']
                    })
        except Exception as e:
            self.logger.error(f"보안 확인 실패: {e}")
    
    def _cleanup_errors(self):
        """에러 정리"""
        try:
            # 오래된 에러 제거 (1시간 이상)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            self.errors = [error for error in self.errors if "시간" not in error]  # 간단한 필터링
            
            # 경고도 정리
            self.warnings = self.warnings[-50:]  # 최근 50개만 유지
            
        except Exception as e:
            self.logger.error(f"에러 정리 실패: {e}")
    
    def _cleanup_components(self):
        """컴포넌트 정리"""
        try:
            # 성능 모니터링 중지
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
            
            # 캐시 정리
            if self.cache_manager:
                self.cache_manager.stop_cleanup()
            
            # 비동기 처리 중지
            if self.async_manager:
                self.async_manager.stop()
            
            # 연결 모니터링 중지
            if self.connection_manager:
                self.connection_manager.stop_monitoring()
            
            # 감사 로거 정리
            if self.audit_logger:
                self.audit_logger.cleanup()
            
            self.logger.info("컴포넌트 정리 완료")
            
        except Exception as e:
            self.logger.error(f"컴포넌트 정리 실패: {e}")
    
    def get_system_status(self) -> SystemStatus:
        """시스템 상태 반환"""
        try:
            uptime_seconds = 0
            if self.start_time:
                uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            
            # 성능 메트릭
            performance = {}
            if self.performance_monitor:
                current_metrics = self.performance_monitor.get_current_metrics()
                if current_metrics:
                    performance = {
                        "cpu_percent": current_metrics.cpu_percent,
                        "memory_percent": current_metrics.memory_percent,
                        "memory_used_mb": current_metrics.memory_used_mb,
                        "active_threads": current_metrics.active_threads
                    }
            
            # 보안 메트릭
            security = {}
            if self.audit_logger:
                stats = self.audit_logger.get_stats()
                security = {
                    "total_events": stats['total_events'],
                    "risk_events": stats['risk_events'],
                    "error_rate": stats['errors'] / stats['total_events'] * 100 if stats['total_events'] > 0 else 0
                }
            
            return SystemStatus(
                is_running=self.is_running,
                start_time=self.start_time or datetime.now(timezone.utc),
                uptime_seconds=uptime_seconds,
                components=self.components.copy(),
                performance=performance,
                security=security,
                errors=self.errors.copy(),
                warnings=self.warnings.copy()
            )
            
        except Exception as e:
            self.logger.error(f"시스템 상태 조회 실패: {e}")
            return SystemStatus(
                is_running=False,
                start_time=datetime.now(timezone.utc),
                uptime_seconds=0,
                components={},
                performance={},
                security={},
                errors=[str(e)],
                warnings=[]
            )
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """이벤트 콜백 추가"""
        try:
            if event_type in self.event_callbacks:
                self.event_callbacks[event_type].append(callback)
        except Exception as e:
            self.logger.error(f"이벤트 콜백 추가 실패: {e}")
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """이벤트 트리거"""
        try:
            if event_type in self.event_callbacks:
                for callback in self.event_callbacks[event_type]:
                    try:
                        callback(event_type, data)
                    except Exception as e:
                        self.logger.error(f"이벤트 콜백 실행 실패: {e}")
        except Exception as e:
            self.logger.error(f"이벤트 트리거 실패: {e}")
    
    def print_system_status(self):
        """시스템 상태 출력"""
        try:
            status = self.get_system_status()
            
            print("=" * 80)
            print("🖥️ 시스템 상태")
            print("=" * 80)
            
            print(f"🔄 실행 상태: {'실행 중' if status.is_running else '중지됨'}")
            print(f"⏱️ 가동 시간: {status.uptime_seconds:.0f}초")
            print(f"📅 시작 시간: {status.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n🔧 컴포넌트 상태:")
            for component, is_healthy in status.components.items():
                status_icon = "✅" if is_healthy else "❌"
                print(f"  {status_icon} {component}")
            
            if status.performance:
                print(f"\n📊 성능 메트릭:")
                print(f"  CPU 사용률: {status.performance.get('cpu_percent', 0):.1f}%")
                print(f"  메모리 사용률: {status.performance.get('memory_percent', 0):.1f}%")
                print(f"  메모리 사용량: {status.performance.get('memory_used_mb', 0):.1f} MB")
                print(f"  활성 스레드: {status.performance.get('active_threads', 0)}개")
            
            if status.security:
                print(f"\n🔒 보안 메트릭:")
                print(f"  총 이벤트: {status.security.get('total_events', 0):,}개")
                print(f"  위험 이벤트: {status.security.get('risk_events', 0):,}개")
                print(f"  에러율: {status.security.get('error_rate', 0):.2f}%")
            
            if status.errors:
                print(f"\n❌ 에러 ({len(status.errors)}개):")
                for error in status.errors[-5:]:  # 최근 5개만
                    print(f"  - {error}")
            
            if status.warnings:
                print(f"\n⚠️ 경고 ({len(status.warnings)}개):")
                for warning in status.warnings[-5:]:  # 최근 5개만
                    print(f"  - {warning}")
            
            print("=" * 80)
            
        except Exception as e:
            self.logger.error(f"시스템 상태 출력 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 통합 시스템 관리 테스트")
    
    # 시스템 관리자 초기화
    system_manager = SystemManager("test_config", "test_logs")
    
    try:
        # 시스템 시작
        print("1. 시스템 시작")
        success = system_manager.start_system()
        print(f"시스템 시작: {'성공' if success else '실패'}")
        
        if success:
            # 시스템 상태 확인
            print("\n2. 시스템 상태 확인")
            system_manager.print_system_status()
            
            # 10초 대기
            print("\n3. 시스템 실행 (10초)")
            time.sleep(10)
            
            # 최종 상태 확인
            print("\n4. 최종 상태 확인")
            system_manager.print_system_status()
            
            # 시스템 중지
            print("\n5. 시스템 중지")
            stop_success = system_manager.stop_system()
            print(f"시스템 중지: {'성공' if stop_success else '실패'}")
    
    except Exception as e:
        print(f"❌ 시스템 관리 테스트 실패: {e}")
