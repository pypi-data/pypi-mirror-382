#!/usr/bin/env python3
"""
간단한 점검 감지 시스템
업비트와 바이비트 시스템에서 공통으로 사용
"""

import threading
import time
import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

from ..notifications.telegram import TelegramNotifier

logger = logging.getLogger(__name__)

@dataclass
class MaintenanceEvent:
    """점검 이벤트 정보"""
    timestamp: datetime
    event_type: str  # 'start', 'end', 'detected'
    duration_minutes: Optional[int] = None
    details: Optional[Dict] = None

class SimpleMaintenanceDetector:
    """간단한 점검 감지 시스템"""
    
    def __init__(self, system_name: str, telegram_notifier: Optional[TelegramNotifier] = None):
        self.system_name = system_name
        self.telegram_notifier = telegram_notifier
        self.telegram_enabled = telegram_notifier is not None
        
        # 점검 감지 설정
        self.config = {
            'check_interval': 30,           # 체크 간격 (초)
            'api_timeout': 10,              # API 타임아웃
            'max_retry_attempts': 3,        # 최대 재시도 횟수
            'retry_delay': 5,               # 재시도 간격
            'response_delay_threshold': 8.0, # 응답 지연 임계값
            'required_success': 3,          # 성공 필요 횟수
        }
        
        # 점검 상태
        self.maintenance_active = False
        self.maintenance_start_time = None
        self.last_check_time = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        
        # 점검 이력
        self.maintenance_history: List[MaintenanceEvent] = []
        self.max_history_size = 100
        
        # 모니터링 상태
        self.monitoring = False
        self.monitor_thread = None
        
        logger.info(f"{system_name} 간단한 점검 감지 시스템 초기화 완료")
    
    def start_monitoring(self):
        """점검 감지 모니터링 시작"""
        if self.monitoring:
            logger.warning("점검 감지 모니터링이 이미 실행 중입니다")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"{self.system_name} 점검 감지 모니터링 시작됨")
    
    def stop_monitoring(self):
        """점검 감지 모니터링 중단"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info(f"{self.system_name} 점검 감지 모니터링 중단됨")
    
    def _monitor_loop(self):
        """점검 감지 모니터링 루프"""
        while self.monitoring:
            try:
                self._check_maintenance_status()
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                logger.error(f"점검 감지 모니터링 오류: {e}")
                time.sleep(self.config['check_interval'])
    
    def _check_maintenance_status(self):
        """점검 상태 확인"""
        try:
            start_time = time.time()
            
            # API 상태 확인 (시스템별로 구현 필요)
            status = self._check_api_status()
            
            response_time = time.time() - start_time
            
            if status['healthy']:
                self._handle_success(response_time)
            else:
                self._handle_failure(status, response_time)
            
            self.last_check_time = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"점검 상태 확인 오류: {e}")
            self._handle_failure({'error': str(e)}, 0)
    
    def _check_api_status(self) -> Dict[str, Any]:
        """API 상태 확인 (하위 클래스에서 구현)"""
        # 기본 구현: 항상 정상으로 가정
        return {
            'healthy': True,
            'response_time': 0.1,
            'status_code': 200
        }
    
    def _handle_success(self, response_time: float):
        """성공 처리"""
        self.consecutive_failures = 0
        self.consecutive_successes += 1
        
        # 점검 종료 감지
        if self.maintenance_active and self.consecutive_successes >= self.config['required_success']:
            self._end_maintenance()
        
        # 응답 시간이 느린 경우 경고
        if response_time > self.config['response_delay_threshold']:
            logger.warning(f"API 응답이 느립니다: {response_time:.2f}초")
    
    def _handle_failure(self, status: Dict, response_time: float):
        """실패 처리"""
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        
        # 점검 시작 감지
        if not self.maintenance_active and self.consecutive_failures >= self.config['required_success']:
            self._start_maintenance(status, response_time)
        
        # 응답 시간이 매우 느린 경우
        if response_time > self.config['response_delay_threshold'] * 2:
            logger.warning(f"API 응답이 매우 느립니다: {response_time:.2f}초")
    
    def _start_maintenance(self, status: Dict, response_time: float):
        """점검 시작 처리"""
        self.maintenance_active = True
        self.maintenance_start_time = datetime.now(timezone.utc)
        
        # 점검 이벤트 기록
        event = MaintenanceEvent(
            timestamp=self.maintenance_start_time,
            event_type='start',
            details={
                'status': status,
                'response_time': response_time,
                'consecutive_failures': self.consecutive_failures
            }
        )
        self._add_maintenance_event(event)
        
        # 알림 전송
        message = f"🔧 {self.system_name} 점검 시작 감지\n\n"
        message += f"📊 상태: {status.get('error', 'API 응답 실패')}\n"
        message += f"⏱️ 응답시간: {response_time:.2f}초\n"
        message += f"🔄 연속 실패: {self.consecutive_failures}회"
        
        self._send_maintenance_alert(message)
        
        logger.warning(f"{self.system_name} 점검 시작 감지됨")
    
    def _end_maintenance(self):
        """점검 종료 처리"""
        if not self.maintenance_active:
            return
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.maintenance_start_time).total_seconds() / 60
        
        # 점검 이벤트 기록
        event = MaintenanceEvent(
            timestamp=end_time,
            event_type='end',
            duration_minutes=int(duration),
            details={
                'start_time': self.maintenance_start_time.isoformat(),
                'consecutive_successes': self.consecutive_successes
            }
        )
        self._add_maintenance_event(event)
        
        # 알림 전송
        message = f"✅ {self.system_name} 점검 종료 감지\n\n"
        message += f"⏱️ 점검 시간: {int(duration)}분\n"
        message += f"🔄 연속 성공: {self.consecutive_successes}회\n"
        message += f"🕐 시작: {self.maintenance_start_time.strftime('%H:%M:%S')}\n"
        message += f"🕐 종료: {end_time.strftime('%H:%M:%S')}"
        
        self._send_maintenance_alert(message)
        
        # 상태 초기화
        self.maintenance_active = False
        self.maintenance_start_time = None
        
        logger.info(f"{self.system_name} 점검 종료 감지됨 (지속시간: {int(duration)}분)")
    
    def _add_maintenance_event(self, event: MaintenanceEvent):
        """점검 이벤트 추가"""
        self.maintenance_history.append(event)
        
        # 이력 크기 제한
        if len(self.maintenance_history) > self.max_history_size:
            self.maintenance_history.pop(0)
    
    def _send_maintenance_alert(self, message: str):
        """점검 알림 전송"""
        if self.telegram_enabled:
            try:
                self.telegram_notifier.send_message(message)
                logger.info("점검 알림 텔레그램 전송 완료")
            except Exception as e:
                logger.error(f"점검 알림 텔레그램 전송 실패: {e}")
        
        # 로그에도 기록
        logger.info(f"점검 알림: {message}")
    
    def get_maintenance_status(self) -> Dict[str, Any]:
        """현재 점검 상태 반환"""
        current_time = datetime.now(timezone.utc)
        
        # 점검 통계 계산
        total_maintenance = len([e for e in self.maintenance_history if e.event_type == 'end'])
        total_duration = sum([e.duration_minutes or 0 for e in self.maintenance_history if e.event_type == 'end'])
        avg_duration = total_duration / total_maintenance if total_maintenance > 0 else 0
        
        # 최근 점검 정보
        recent_maintenance = None
        if self.maintenance_history:
            recent_maintenance = self.maintenance_history[-1]
        
        return {
            'system_name': self.system_name,
            'maintenance_active': self.maintenance_active,
            'monitoring_active': self.monitoring,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'statistics': {
                'total_count': total_maintenance,
                'avg_duration_minutes': int(avg_duration),
                'total_duration_minutes': total_duration
            },
            'recent_event': {
                'type': recent_maintenance.event_type if recent_maintenance else None,
                'timestamp': recent_maintenance.timestamp.isoformat() if recent_maintenance else None,
                'duration_minutes': recent_maintenance.duration_minutes if recent_maintenance else None
            } if recent_maintenance else None,
            'current_status': {
                'healthy': self.consecutive_failures < self.config['required_success'],
                'response_time': None,  # 실제 구현에서 설정
                'last_error': None      # 실제 구현에서 설정
            }
        }
    
    def is_maintenance_active(self) -> bool:
        """점검 중인지 확인"""
        return self.maintenance_active
    
    def get_maintenance_duration(self) -> Optional[int]:
        """현재 점검 지속 시간 (분) 반환"""
        if not self.maintenance_active or not self.maintenance_start_time:
            return None
        
        duration = (datetime.now(timezone.utc) - self.maintenance_start_time).total_seconds() / 60
        return int(duration)
