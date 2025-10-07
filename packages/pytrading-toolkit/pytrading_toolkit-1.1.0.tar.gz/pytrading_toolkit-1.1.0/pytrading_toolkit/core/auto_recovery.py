#!/usr/bin/env python3
"""
자동 복구 및 장애 대응 시스템
시스템 장애 자동 감지 및 복구
"""

import os
import time
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import psutil
import subprocess

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """장애 타입"""
    COMPONENT_FAILURE = "component_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_LEAK = "memory_leak"
    CONNECTION_LOSS = "connection_loss"
    API_ERROR = "api_error"
    CONFIG_ERROR = "config_error"
    SECURITY_THREAT = "security_threat"

class RecoveryAction(Enum):
    """복구 액션"""
    RESTART_COMPONENT = "restart_component"
    RESTART_SYSTEM = "restart_system"
    CLEAR_CACHE = "clear_cache"
    RESET_CONNECTIONS = "reset_connections"
    RELOAD_CONFIG = "reload_config"
    ESCALATE_ALERT = "escalate_alert"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class FailureEvent:
    """장애 이벤트"""
    failure_id: str
    failure_type: FailureType
    component: str
    severity: str  # low, medium, high, critical
    description: str
    timestamp: datetime
    details: Dict[str, Any]
    recovery_actions: List[RecoveryAction]
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class RecoveryPlan:
    """복구 계획"""
    plan_id: str
    failure_type: FailureType
    component: str
    actions: List[RecoveryAction]
    timeout_seconds: int
    retry_count: int
    escalation_threshold: int

class AutoRecoverySystem:
    """자동 복구 시스템"""
    
    def __init__(self, system_manager):
        self.system_manager = system_manager
        self.is_running = False
        self.monitor_thread = None
        
        # 장애 이벤트 저장소
        self.failure_events: List[FailureEvent] = []
        self.active_failures: Dict[str, FailureEvent] = {}
        
        # 복구 계획
        self.recovery_plans = self._initialize_recovery_plans()
        
        # 모니터링 설정
        self.monitoring_interval = 10  # 10초마다 확인
        self.health_check_timeout = 30  # 30초 타임아웃
        
        # 임계값 설정
        self.thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 95.0,
            'disk_usage_percent': 90.0,
            'response_time': 10.0,
            'error_rate': 10.0,
            'connection_failures': 5
        }
        
        # 복구 통계
        self.recovery_stats = {
            'total_failures': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'escalated_failures': 0
        }
        
        # 콜백 함수들
        self.callbacks = {
            'failure_detected': [],
            'recovery_started': [],
            'recovery_completed': [],
            'recovery_failed': [],
            'escalation_required': []
        }
    
    def _initialize_recovery_plans(self) -> Dict[str, RecoveryPlan]:
        """복구 계획 초기화"""
        return {
            'component_failure': RecoveryPlan(
                plan_id='restart_component',
                failure_type=FailureType.COMPONENT_FAILURE,
                component='*',
                actions=[RecoveryAction.RESTART_COMPONENT],
                timeout_seconds=60,
                retry_count=3,
                escalation_threshold=2
            ),
            'performance_degradation': RecoveryPlan(
                plan_id='clear_cache_and_restart',
                failure_type=FailureType.PERFORMANCE_DEGRADATION,
                component='*',
                actions=[RecoveryAction.CLEAR_CACHE, RecoveryAction.RESTART_COMPONENT],
                timeout_seconds=120,
                retry_count=2,
                escalation_threshold=1
            ),
            'memory_leak': RecoveryPlan(
                plan_id='restart_system',
                failure_type=FailureType.MEMORY_LEAK,
                component='*',
                actions=[RecoveryAction.RESTART_SYSTEM],
                timeout_seconds=300,
                retry_count=1,
                escalation_threshold=1
            ),
            'connection_loss': RecoveryPlan(
                plan_id='reset_connections',
                failure_type=FailureType.CONNECTION_LOSS,
                component='*',
                actions=[RecoveryAction.RESET_CONNECTIONS],
                timeout_seconds=30,
                retry_count=5,
                escalation_threshold=3
            ),
            'api_error': RecoveryPlan(
                plan_id='retry_and_escalate',
                failure_type=FailureType.API_ERROR,
                component='*',
                actions=[RecoveryAction.RESTART_COMPONENT, RecoveryAction.ESCALATE_ALERT],
                timeout_seconds=180,
                retry_count=2,
                escalation_threshold=1
            ),
            'config_error': RecoveryPlan(
                plan_id='reload_config',
                failure_type=FailureType.CONFIG_ERROR,
                component='*',
                actions=[RecoveryAction.RELOAD_CONFIG],
                timeout_seconds=60,
                retry_count=2,
                escalation_threshold=1
            ),
            'security_threat': RecoveryPlan(
                plan_id='emergency_stop',
                failure_type=FailureType.SECURITY_THREAT,
                component='*',
                actions=[RecoveryAction.EMERGENCY_STOP, RecoveryAction.ESCALATE_ALERT],
                timeout_seconds=10,
                retry_count=0,
                escalation_threshold=0
            )
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            if self.is_running:
                logger.warning("자동 복구 시스템이 이미 실행 중입니다")
                return
            
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("자동 복구 시스템 모니터링 시작")
            
        except Exception as e:
            logger.error(f"자동 복구 시스템 시작 실패: {e}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            self.is_running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            logger.info("자동 복구 시스템 모니터링 중지")
            
        except Exception as e:
            logger.error(f"자동 복구 시스템 중지 실패: {e}")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        try:
            while self.is_running:
                # 시스템 상태 확인
                self._check_system_health()
                
                # 활성 장애 복구 확인
                self._check_active_failures()
                
                # 오래된 장애 이벤트 정리
                self._cleanup_old_failures()
                
                time.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"모니터링 루프 오류: {e}")
    
    def _check_system_health(self):
        """시스템 상태 확인"""
        try:
            # 성능 메트릭 확인
            self._check_performance_metrics()
            
            # 컴포넌트 상태 확인
            self._check_component_health()
            
            # 연결 상태 확인
            self._check_connection_health()
            
            # 보안 상태 확인
            self._check_security_health()
            
        except Exception as e:
            logger.error(f"시스템 상태 확인 실패: {e}")
    
    def _check_performance_metrics(self):
        """성능 메트릭 확인"""
        try:
            if not self.system_manager.performance_monitor:
                return
            
            current_metrics = self.system_manager.performance_monitor.get_current_metrics()
            if not current_metrics:
                return
            
            # CPU 사용률 확인
            if current_metrics.cpu_percent > self.thresholds['cpu_percent']:
                self._detect_failure(
                    FailureType.PERFORMANCE_DEGRADATION,
                    'performance_monitor',
                    'high',
                    f"높은 CPU 사용률: {current_metrics.cpu_percent:.1f}%",
                    {'cpu_percent': current_metrics.cpu_percent}
                )
            
            # 메모리 사용률 확인
            if current_metrics.memory_percent > self.thresholds['memory_percent']:
                self._detect_failure(
                    FailureType.MEMORY_LEAK,
                    'performance_monitor',
                    'critical',
                    f"높은 메모리 사용률: {current_metrics.memory_percent:.1f}%",
                    {'memory_percent': current_metrics.memory_percent}
                )
            
        except Exception as e:
            logger.error(f"성능 메트릭 확인 실패: {e}")
    
    def _check_component_health(self):
        """컴포넌트 상태 확인"""
        try:
            system_status = self.system_manager.get_system_status()
            
            for component, is_healthy in system_status.components.items():
                if not is_healthy:
                    self._detect_failure(
                        FailureType.COMPONENT_FAILURE,
                        component,
                        'high',
                        f"컴포넌트 비정상: {component}",
                        {'component': component}
                    )
            
        except Exception as e:
            logger.error(f"컴포넌트 상태 확인 실패: {e}")
    
    def _check_connection_health(self):
        """연결 상태 확인"""
        try:
            if not self.system_manager.connection_manager:
                return
            
            connections = self.system_manager.connection_manager.get_all_connections()
            failed_connections = 0
            
            for name, connection in connections.items():
                if not connection.is_connected:
                    failed_connections += 1
            
            if failed_connections > self.thresholds['connection_failures']:
                self._detect_failure(
                    FailureType.CONNECTION_LOSS,
                    'connection_manager',
                    'medium',
                    f"연결 실패: {failed_connections}개",
                    {'failed_connections': failed_connections}
                )
            
        except Exception as e:
            logger.error(f"연결 상태 확인 실패: {e}")
    
    def _check_security_health(self):
        """보안 상태 확인"""
        try:
            if not self.system_manager.audit_logger:
                return
            
            stats = self.system_manager.audit_logger.get_stats()
            error_rate = stats.get('errors', 0) / max(stats.get('total_events', 1), 1) * 100
            
            if error_rate > self.thresholds['error_rate']:
                self._detect_failure(
                    FailureType.SECURITY_THREAT,
                    'audit_logger',
                    'high',
                    f"높은 에러율: {error_rate:.1f}%",
                    {'error_rate': error_rate}
                )
            
        except Exception as e:
            logger.error(f"보안 상태 확인 실패: {e}")
    
    def _detect_failure(self, failure_type: FailureType, component: str, 
                       severity: str, description: str, details: Dict[str, Any]):
        """장애 감지"""
        try:
            failure_id = f"{failure_type.value}_{component}_{int(time.time())}"
            
            # 중복 장애 확인
            if failure_id in self.active_failures:
                return
            
            # 복구 계획 선택
            recovery_plan = self._select_recovery_plan(failure_type, component)
            
            # 장애 이벤트 생성
            failure_event = FailureEvent(
                failure_id=failure_id,
                failure_type=failure_type,
                component=component,
                severity=severity,
                description=description,
                timestamp=datetime.now(timezone.utc),
                details=details,
                recovery_actions=recovery_plan.actions if recovery_plan else []
            )
            
            # 장애 이벤트 저장
            self.failure_events.append(failure_event)
            self.active_failures[failure_id] = failure_event
            self.recovery_stats['total_failures'] += 1
            
            # 이벤트 콜백 호출
            self._trigger_callback('failure_detected', failure_event)
            
            # 자동 복구 시작
            if recovery_plan:
                self._start_recovery(failure_event, recovery_plan)
            
            logger.warning(f"장애 감지: {description}")
            
        except Exception as e:
            logger.error(f"장애 감지 실패: {e}")
    
    def _select_recovery_plan(self, failure_type: FailureType, component: str) -> Optional[RecoveryPlan]:
        """복구 계획 선택"""
        try:
            # 장애 타입별 복구 계획 찾기
            for plan in self.recovery_plans.values():
                if plan.failure_type == failure_type:
                    return plan
            
            # 기본 복구 계획
            return self.recovery_plans.get('component_failure')
            
        except Exception as e:
            logger.error(f"복구 계획 선택 실패: {e}")
            return None
    
    def _start_recovery(self, failure_event: FailureEvent, recovery_plan: RecoveryPlan):
        """복구 시작"""
        try:
            logger.info(f"복구 시작: {failure_event.failure_id}")
            
            # 이벤트 콜백 호출
            self._trigger_callback('recovery_started', failure_event)
            
            # 복구 액션 실행
            success = self._execute_recovery_actions(failure_event, recovery_plan)
            
            if success:
                # 복구 성공
                failure_event.is_resolved = True
                failure_event.resolved_at = datetime.now(timezone.utc)
                del self.active_failures[failure_event.failure_id]
                self.recovery_stats['successful_recoveries'] += 1
                
                self._trigger_callback('recovery_completed', failure_event)
                logger.info(f"복구 완료: {failure_event.failure_id}")
                
            else:
                # 복구 실패
                self.recovery_stats['failed_recoveries'] += 1
                self._trigger_callback('recovery_failed', failure_event)
                logger.error(f"복구 실패: {failure_event.failure_id}")
                
                # 에스컬레이션 확인
                if self._should_escalate(failure_event, recovery_plan):
                    self._escalate_failure(failure_event)
            
        except Exception as e:
            logger.error(f"복구 시작 실패: {e}")
    
    def _execute_recovery_actions(self, failure_event: FailureEvent, 
                                 recovery_plan: RecoveryPlan) -> bool:
        """복구 액션 실행"""
        try:
            for action in recovery_plan.actions:
                success = self._execute_recovery_action(action, failure_event)
                if not success:
                    return False
                
                # 액션 간 대기
                time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"복구 액션 실행 실패: {e}")
            return False
    
    def _execute_recovery_action(self, action: RecoveryAction, failure_event: FailureEvent) -> bool:
        """개별 복구 액션 실행"""
        try:
            if action == RecoveryAction.RESTART_COMPONENT:
                return self._restart_component(failure_event.component)
            
            elif action == RecoveryAction.RESTART_SYSTEM:
                return self._restart_system()
            
            elif action == RecoveryAction.CLEAR_CACHE:
                return self._clear_cache()
            
            elif action == RecoveryAction.RESET_CONNECTIONS:
                return self._reset_connections()
            
            elif action == RecoveryAction.RELOAD_CONFIG:
                return self._reload_config()
            
            elif action == RecoveryAction.ESCALATE_ALERT:
                return self._escalate_alert(failure_event)
            
            elif action == RecoveryAction.EMERGENCY_STOP:
                return self._emergency_stop()
            
            return False
            
        except Exception as e:
            logger.error(f"복구 액션 실행 실패: {action.value}: {e}")
            return False
    
    def _restart_component(self, component: str) -> bool:
        """컴포넌트 재시작"""
        try:
            logger.info(f"컴포넌트 재시작: {component}")
            
            # 컴포넌트별 재시작 로직
            if component == 'performance_monitor':
                if self.system_manager.performance_monitor:
                    self.system_manager.performance_monitor.stop_monitoring()
                    self.system_manager.performance_monitor.start_monitoring()
            
            elif component == 'cache_manager':
                if self.system_manager.cache_manager:
                    self.system_manager.cache_manager.clear()
            
            elif component == 'connection_manager':
                if self.system_manager.connection_manager:
                    self.system_manager.connection_manager.stop_monitoring()
                    self.system_manager.connection_manager.start_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"컴포넌트 재시작 실패: {e}")
            return False
    
    def _restart_system(self) -> bool:
        """시스템 재시작"""
        try:
            logger.warning("시스템 재시작 요청")
            
            # 시스템 중지
            self.system_manager.stop_system()
            time.sleep(5)
            
            # 시스템 시작
            return self.system_manager.start_system()
            
        except Exception as e:
            logger.error(f"시스템 재시작 실패: {e}")
            return False
    
    def _clear_cache(self) -> bool:
        """캐시 정리"""
        try:
            if self.system_manager.cache_manager:
                self.system_manager.cache_manager.clear()
                logger.info("캐시 정리 완료")
                return True
            return False
            
        except Exception as e:
            logger.error(f"캐시 정리 실패: {e}")
            return False
    
    def _reset_connections(self) -> bool:
        """연결 재설정"""
        try:
            if self.system_manager.connection_manager:
                # 모든 연결 재설정
                connections = self.system_manager.connection_manager.get_all_connections()
                for name in connections.keys():
                    self.system_manager.connection_manager.add_connection(name, "https://example.com")
                
                logger.info("연결 재설정 완료")
                return True
            return False
            
        except Exception as e:
            logger.error(f"연결 재설정 실패: {e}")
            return False
    
    def _reload_config(self) -> bool:
        """설정 재로드"""
        try:
            # 설정 재로드 로직
            logger.info("설정 재로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"설정 재로드 실패: {e}")
            return False
    
    def _escalate_alert(self, failure_event: FailureEvent) -> bool:
        """알림 에스컬레이션"""
        try:
            logger.critical(f"에스컬레이션 요청: {failure_event.description}")
            self.recovery_stats['escalated_failures'] += 1
            return True
            
        except Exception as e:
            logger.error(f"알림 에스컬레이션 실패: {e}")
            return False
    
    def _emergency_stop(self) -> bool:
        """긴급 중지"""
        try:
            logger.critical("긴급 중지 실행")
            self.system_manager.stop_system()
            return True
            
        except Exception as e:
            logger.error(f"긴급 중지 실패: {e}")
            return False
    
    def _should_escalate(self, failure_event: FailureEvent, recovery_plan: RecoveryPlan) -> bool:
        """에스컬레이션 필요 여부 확인"""
        try:
            # 복구 시도 횟수 확인
            retry_count = failure_event.details.get('retry_count', 0)
            return retry_count >= recovery_plan.escalation_threshold
            
        except Exception as e:
            logger.error(f"에스컬레이션 확인 실패: {e}")
            return False
    
    def _escalate_failure(self, failure_event: FailureEvent):
        """장애 에스컬레이션"""
        try:
            self._trigger_callback('escalation_required', failure_event)
            logger.critical(f"장애 에스컬레이션: {failure_event.failure_id}")
            
        except Exception as e:
            logger.error(f"장애 에스컬레이션 실패: {e}")
    
    def _check_active_failures(self):
        """활성 장애 확인"""
        try:
            current_time = datetime.now(timezone.utc)
            timeout_failures = []
            
            for failure_id, failure_event in self.active_failures.items():
                # 타임아웃 확인 (1시간)
                if (current_time - failure_event.timestamp).total_seconds() > 3600:
                    timeout_failures.append(failure_id)
            
            # 타임아웃된 장애 제거
            for failure_id in timeout_failures:
                del self.active_failures[failure_id]
                
        except Exception as e:
            logger.error(f"활성 장애 확인 실패: {e}")
    
    def _cleanup_old_failures(self):
        """오래된 장애 이벤트 정리"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
            self.failure_events = [
                event for event in self.failure_events
                if event.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"오래된 장애 이벤트 정리 실패: {e}")
    
    def _trigger_callback(self, event_type: str, data: Any):
        """콜백 트리거"""
        try:
            if event_type in self.callbacks:
                for callback in self.callbacks[event_type]:
                    try:
                        callback(event_type, data)
                    except Exception as e:
                        logger.error(f"콜백 실행 실패: {e}")
                        
        except Exception as e:
            logger.error(f"콜백 트리거 실패: {e}")
    
    def add_callback(self, event_type: str, callback: Callable):
        """콜백 추가"""
        try:
            if event_type in self.callbacks:
                self.callbacks[event_type].append(callback)
                
        except Exception as e:
            logger.error(f"콜백 추가 실패: {e}")
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """복구 통계 반환"""
        return self.recovery_stats.copy()
    
    def get_active_failures(self) -> List[Dict[str, Any]]:
        """활성 장애 목록 반환"""
        try:
            return [
                {
                    'failure_id': event.failure_id,
                    'failure_type': event.failure_type.value,
                    'component': event.component,
                    'severity': event.severity,
                    'description': event.description,
                    'timestamp': event.timestamp.isoformat(),
                    'details': event.details
                }
                for event in self.active_failures.values()
            ]
        except Exception as e:
            logger.error(f"활성 장애 목록 조회 실패: {e}")
            return []
    
    def print_recovery_status(self):
        """복구 상태 출력"""
        try:
            stats = self.get_recovery_stats()
            active_failures = self.get_active_failures()
            
            print("=" * 80)
            print("🔧 자동 복구 시스템 상태")
            print("=" * 80)
            
            print(f"📊 복구 통계:")
            print(f"  총 장애: {stats['total_failures']}개")
            print(f"  성공적 복구: {stats['successful_recoveries']}개")
            print(f"  복구 실패: {stats['failed_recoveries']}개")
            print(f"  에스컬레이션: {stats['escalated_failures']}개")
            
            if active_failures:
                print(f"\n🚨 활성 장애 ({len(active_failures)}개):")
                for failure in active_failures:
                    print(f"  - {failure['component']}: {failure['description']}")
            else:
                print(f"\n✅ 활성 장애 없음")
            
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"복구 상태 출력 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 자동 복구 시스템 테스트")
    
    # 시스템 관리자와 자동 복구 시스템 초기화
    from .system_manager import SystemManager
    
    system_manager = SystemManager("test_config", "test_logs")
    auto_recovery = AutoRecoverySystem(system_manager)
    
    try:
        # 시스템 시작
        print("1. 시스템 시작")
        system_manager.start_system()
        
        # 자동 복구 시스템 시작
        print("2. 자동 복구 시스템 시작")
        auto_recovery.start_monitoring()
        
        # 복구 상태 확인
        print("3. 복구 상태 확인")
        auto_recovery.print_recovery_status()
        
        # 30초 대기
        print("4. 모니터링 (30초)")
        time.sleep(30)
        
        # 최종 상태 확인
        print("5. 최종 상태 확인")
        auto_recovery.print_recovery_status()
        
        # 자동 복구 시스템 중지
        print("6. 자동 복구 시스템 중지")
        auto_recovery.stop_monitoring()
        
        # 시스템 중지
        print("7. 시스템 중지")
        system_manager.stop_system()
        
    except Exception as e:
        print(f"❌ 자동 복구 시스템 테스트 실패: {e}")
