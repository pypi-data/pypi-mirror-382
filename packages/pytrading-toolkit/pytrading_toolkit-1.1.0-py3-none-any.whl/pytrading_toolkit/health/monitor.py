#!/usr/bin/env python3
"""
공통 헬스 모니터링 시스템
업비트와 바이비트 시스템에서 공통으로 사용
"""

import threading
import time
import psutil
import os
import subprocess
from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any, Optional

from ..notifications.telegram import TelegramNotifier

logger = logging.getLogger(__name__)

class HealthMonitor:
    """공통 헬스 모니터링 시스템"""
    
    def __init__(self, system_name: str, telegram_notifier: Optional[TelegramNotifier] = None):
        self.system_name = system_name
        self.telegram_notifier = telegram_notifier
        self.telegram_enabled = telegram_notifier is not None
        
        self.last_heartbeat = datetime.now(timezone.utc)
        self.error_count = 0
        self.max_errors = 5
        self.monitoring = True
        
        # 알림 간격 제어 (스팸 방지)
        self.last_notification = {}
        self.notification_cooldown = 300  # 5분
        
        # 모니터링 설정
        self.config = {
            'heartbeat_interval': 300,  # 5분
            'memory_threshold': 80,     # 80% 이상 시 경고
            'disk_threshold': 85,       # 85% 이상 시 경고
            'cpu_threshold': 90,        # 90% 이상 시 경고
            'network_timeout': 10,      # 네트워크 타임아웃
            'process_check_interval': 60,  # 프로세스 체크 간격
        }
        
        logger.info(f"{system_name} 헬스 모니터링 시스템 초기화 완료")
    
    def start_monitoring(self):
        """헬스 모니터링 시작"""
        logger.info(f"{self.system_name} 헬스 모니터링 시작")
        
        # 각종 모니터링 스레드 시작
        threading.Thread(target=self._monitor_process, daemon=True).start()
        threading.Thread(target=self._monitor_memory, daemon=True).start()
        threading.Thread(target=self._monitor_disk, daemon=True).start()
        threading.Thread(target=self._monitor_network, daemon=True).start()
        threading.Thread(target=self._monitor_trading_activity, daemon=True).start()
        threading.Thread(target=self._send_heartbeat, daemon=True).start()
        
        logger.info(f"{self.system_name} 모든 모니터링 스레드 시작됨")
    
    def stop_monitoring(self):
        """헬스 모니터링 중단"""
        self.monitoring = False
        logger.info(f"{self.system_name} 헬스 모니터링 중단됨")
    
    def _monitor_process(self):
        """프로세스 상태 모니터링"""
        while self.monitoring:
            try:
                # 메인 프로세스 확인
                main_process = None
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python3' and proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            # main.py가 포함되고, 시스템 이름이 명령행에 있거나 업비트/바이비트 관련 디렉토리에 있는 경우
                            if 'main.py' in cmdline and (
                                self.system_name in cmdline or 
                                'upbit' in cmdline.lower() or 
                                'bybit' in cmdline.lower() or
                                'app/upbit' in cmdline or
                                'app/bybit' in cmdline
                            ):
                                main_process = proc
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if main_process is None:
                    self._send_alert("프로세스 경고", f"{self.system_name} 메인 프로세스를 찾을 수 없습니다")
                else:
                    # 프로세스 상태 확인
                    try:
                        cpu_percent = main_process.cpu_percent()
                        memory_percent = main_process.memory_percent()
                        
                        if cpu_percent > self.config['cpu_threshold']:
                            self._send_alert("CPU 경고", f"CPU 사용률이 높습니다: {cpu_percent:.1f}%")
                        
                        if memory_percent > self.config['memory_threshold']:
                            self._send_alert("메모리 경고", f"메모리 사용률이 높습니다: {memory_percent:.1f}%")
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                time.sleep(self.config['process_check_interval'])
                
            except Exception as e:
                logger.error(f"프로세스 모니터링 오류: {e}")
                time.sleep(self.config['process_check_interval'])
    
    def _monitor_memory(self):
        """메모리 사용량 모니터링"""
        while self.monitoring:
            try:
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                if memory_percent > self.config['memory_threshold']:
                    self._send_alert("메모리 경고", 
                                   f"시스템 메모리 사용률: {memory_percent:.1f}% "
                                   f"(사용: {memory.used // (1024**3):.1f}GB, "
                                   f"가용: {memory.available // (1024**3):.1f}GB)")
                
                time.sleep(300)  # 5분마다 체크
                
            except Exception as e:
                logger.error(f"메모리 모니터링 오류: {e}")
                time.sleep(300)
    
    def _monitor_disk(self):
        """디스크 사용량 모니터링"""
        while self.monitoring:
            try:
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                
                if disk_percent > self.config['disk_threshold']:
                    self._send_alert("디스크 경고",
                                   f"디스크 사용률: {disk_percent:.1f}% "
                                   f"(사용: {disk.used // (1024**3):.1f}GB, "
                                   f"가용: {disk.free // (1024**3):.1f}GB)")
                
                time.sleep(600)  # 10분마다 체크
                
            except Exception as e:
                logger.error(f"디스크 모니터링 오류: {e}")
                time.sleep(600)
    
    def _monitor_network(self):
        """네트워크 상태 모니터링"""
        while self.monitoring:
            try:
                # 네트워크 인터페이스 상태 확인
                net_io = psutil.net_io_counters()
                
                # 네트워크 활동이 있는지 확인
                if net_io.bytes_sent == 0 and net_io.bytes_recv == 0:
                    self._send_alert("네트워크 경고", "네트워크 활동이 감지되지 않습니다")
                
                time.sleep(300)  # 5분마다 체크
                
            except Exception as e:
                logger.error(f"네트워크 모니터링 오류: {e}")
                time.sleep(300)
    
    def _monitor_trading_activity(self):
        """트레이딩 활동 모니터링"""
        while self.monitoring:
            try:
                # 트레이딩 활동 체크 (로그 파일 기반)
                current_time = datetime.now(timezone.utc)
                
                # 마지막 하트비트와 비교
                time_since_heartbeat = (current_time - self.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.config['heartbeat_interval'] * 2:
                    self._send_alert("활동 경고", 
                                   f"트레이딩 활동이 {int(time_since_heartbeat/60)}분 동안 감지되지 않았습니다")
                
                time.sleep(300)  # 5분마다 체크
                
            except Exception as e:
                logger.error(f"트레이딩 활동 모니터링 오류: {e}")
                time.sleep(300)
    
    def _send_heartbeat(self):
        """하트비트 전송"""
        while self.monitoring:
            try:
                current_time = datetime.now(timezone.utc)
                self.last_heartbeat = current_time
                
                # 정상 상태 로깅
                logger.info(f"{self.system_name} 하트비트 전송 - 정상 작동 중", extra={
                    'timestamp': current_time.isoformat(),
                    'system': self.system_name
                })
                
                time.sleep(self.config['heartbeat_interval'])
                
            except Exception as e:
                logger.error(f"하트비트 전송 오류: {e}")
                time.sleep(self.config['heartbeat_interval'])
    
    def _send_alert(self, alert_type: str, message: str):
        """알림 전송 (스팸 방지 포함)"""
        current_time = datetime.now(timezone.utc)
        alert_key = f"{alert_type}_{message}"
        
        # 스팸 방지 체크
        if alert_key in self.last_notification:
            time_since_last = (current_time - self.last_notification[alert_key]).total_seconds()
            if time_since_last < self.notification_cooldown:
                return
        
        # 알림 전송
        if self.telegram_enabled:
            try:
                full_message = f"🚨 {self.system_name} {alert_type}\n\n{message}\n\n⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
                self.telegram_notifier.send_message(full_message)
                logger.info(f"텔레그램 알림 전송: {alert_type}")
            except Exception as e:
                logger.error(f"텔레그램 알림 전송 실패: {e}")
        
        # 로그에 기록
        logger.warning(f"{alert_type}: {message}")
        
        # 마지막 알림 시간 업데이트
        self.last_notification[alert_key] = current_time
    
    def get_health_status(self) -> Dict[str, Any]:
        """현재 헬스 상태 반환"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'system_name': self.system_name,
                'status': 'healthy' if self.error_count < self.max_errors else 'warning',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'last_heartbeat': self.last_heartbeat.isoformat(),
                'error_count': self.error_count,
                'memory': {
                    'percent': memory.percent,
                    'used_gb': memory.used // (1024**3),
                    'available_gb': memory.available // (1024**3)
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': disk.used // (1024**3),
                    'free_gb': disk.free // (1024**3)
                },
                'monitoring_active': self.monitoring
            }
        except Exception as e:
            logger.error(f"헬스 상태 조회 오류: {e}")
            return {
                'system_name': self.system_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
