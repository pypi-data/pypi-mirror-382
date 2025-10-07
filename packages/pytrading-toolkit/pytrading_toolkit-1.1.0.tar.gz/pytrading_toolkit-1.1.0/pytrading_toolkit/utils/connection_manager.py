#!/usr/bin/env python3
"""
연결 관리 모듈
네트워크 연결 상태 관리 및 복구
"""

import time
import logging
import requests
import socket
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

@dataclass
class ConnectionStatus:
    """연결 상태"""
    is_connected: bool
    last_check: datetime
    consecutive_failures: int
    last_success: Optional[datetime] = None
    response_time: Optional[float] = None

class ConnectionManager:
    """연결 관리 클래스"""
    
    def __init__(self, check_interval: int = 30, max_failures: int = 3):
        self.check_interval = check_interval
        self.max_failures = max_failures
        self.connections: Dict[str, ConnectionStatus] = {}
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks: Dict[str, Callable] = {}
        
    def add_connection(self, name: str, url: str, timeout: int = 5) -> bool:
        """연결 추가"""
        try:
            self.connections[name] = ConnectionStatus(
                is_connected=False,
                last_check=datetime.now(timezone.utc),
                consecutive_failures=0
            )
            
            # 초기 연결 테스트
            if self.test_connection(url, timeout):
                self.connections[name].is_connected = True
                self.connections[name].last_success = datetime.now(timezone.utc)
                logger.info(f"연결 추가 성공: {name}")
                return True
            else:
                logger.warning(f"연결 추가 실패: {name}")
                return False
                
        except Exception as e:
            logger.error(f"연결 추가 실패: {e}")
            return False
    
    def test_connection(self, url: str, timeout: int = 5) -> bool:
        """연결 테스트"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                logger.debug(f"연결 테스트 성공: {url} ({response_time:.2f}s)")
                return True
            else:
                logger.warning(f"연결 테스트 실패: {url} (상태코드: {response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"연결 타임아웃: {url}")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"연결 실패: {url}")
            return False
        except Exception as e:
            logger.error(f"연결 테스트 오류: {url} - {e}")
            return False
    
    def check_connection(self, name: str, url: str, timeout: int = 5) -> bool:
        """연결 상태 확인"""
        try:
            if name not in self.connections:
                logger.warning(f"알 수 없는 연결: {name}")
                return False
            
            connection = self.connections[name]
            connection.last_check = datetime.now(timezone.utc)
            
            # 연결 테스트
            is_connected = self.test_connection(url, timeout)
            
            if is_connected:
                connection.is_connected = True
                connection.consecutive_failures = 0
                connection.last_success = datetime.now(timezone.utc)
                
                # 연결 복구 알림
                if connection.consecutive_failures > 0:
                    logger.info(f"연결 복구: {name}")
                    self._notify_connection_restored(name)
            else:
                connection.is_connected = False
                connection.consecutive_failures += 1
                
                # 연결 실패 알림
                if connection.consecutive_failures >= self.max_failures:
                    logger.error(f"연결 실패: {name} (연속 {connection.consecutive_failures}회)")
                    self._notify_connection_failed(name)
            
            return is_connected
            
        except Exception as e:
            logger.error(f"연결 상태 확인 실패: {e}")
            return False
    
    def is_connected(self, name: str) -> bool:
        """연결 상태 반환"""
        try:
            if name not in self.connections:
                return False
            return self.connections[name].is_connected
        except Exception as e:
            logger.error(f"연결 상태 조회 실패: {e}")
            return False
    
    def get_connection_status(self, name: str) -> Optional[ConnectionStatus]:
        """연결 상태 상세 정보 반환"""
        try:
            return self.connections.get(name)
        except Exception as e:
            logger.error(f"연결 상태 상세 조회 실패: {e}")
            return None
    
    def get_all_connections(self) -> Dict[str, ConnectionStatus]:
        """모든 연결 상태 반환"""
        try:
            return self.connections.copy()
        except Exception as e:
            logger.error(f"전체 연결 상태 조회 실패: {e}")
            return {}
    
    def start_monitoring(self):
        """연결 모니터링 시작"""
        try:
            if self.monitoring:
                logger.warning("이미 모니터링 중입니다")
                return
            
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
            self.monitor_thread.start()
            logger.info("연결 모니터링 시작")
            
        except Exception as e:
            logger.error(f"모니터링 시작 실패: {e}")
    
    def stop_monitoring(self):
        """연결 모니터링 중지"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("연결 모니터링 중지")
            
        except Exception as e:
            logger.error(f"모니터링 중지 실패: {e}")
    
    def _monitor_connections(self):
        """연결 모니터링 루프"""
        try:
            while self.monitoring:
                for name, connection in self.connections.items():
                    try:
                        # 연결 테스트 (URL이 있는 경우)
                        if hasattr(connection, 'url'):
                            self.check_connection(name, connection.url)
                    except Exception as e:
                        logger.error(f"연결 모니터링 오류: {name} - {e}")
                
                time.sleep(self.check_interval)
                
        except Exception as e:
            logger.error(f"모니터링 루프 오류: {e}")
    
    def set_connection_callback(self, name: str, callback: Callable):
        """연결 상태 변경 콜백 설정"""
        try:
            self.callbacks[name] = callback
            logger.info(f"연결 콜백 설정: {name}")
        except Exception as e:
            logger.error(f"연결 콜백 설정 실패: {e}")
    
    def _notify_connection_restored(self, name: str):
        """연결 복구 알림"""
        try:
            if name in self.callbacks:
                self.callbacks[name](name, True)
        except Exception as e:
            logger.error(f"연결 복구 알림 실패: {e}")
    
    def _notify_connection_failed(self, name: str):
        """연결 실패 알림"""
        try:
            if name in self.callbacks:
                self.callbacks[name](name, False)
        except Exception as e:
            logger.error(f"연결 실패 알림 실패: {e}")
    
    def get_network_info(self) -> Dict[str, Any]:
        """네트워크 정보 반환"""
        try:
            import psutil
            
            # 네트워크 통계
            net_io = psutil.net_io_counters()
            
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "connections": len(self.connections),
                "active_connections": sum(1 for conn in self.connections.values() if conn.is_connected)
            }
        except ImportError:
            logger.warning("psutil이 설치되지 않았습니다")
            return {"error": "psutil not available"}
        except Exception as e:
            logger.error(f"네트워크 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def print_connection_status(self):
        """연결 상태 출력"""
        try:
            print("=" * 60)
            print("🌐 연결 상태")
            print("=" * 60)
            
            if not self.connections:
                print("📋 등록된 연결이 없습니다")
                return
            
            for name, connection in self.connections.items():
                status = "✅ 연결됨" if connection.is_connected else "❌ 연결 끊김"
                failures = connection.consecutive_failures
                last_check = connection.last_check.strftime("%H:%M:%S")
                
                print(f"🔹 {name}")
                print(f"   상태: {status}")
                print(f"   연속 실패: {failures}회")
                print(f"   마지막 확인: {last_check}")
                
                if connection.last_success:
                    last_success = connection.last_success.strftime("%H:%M:%S")
                    print(f"   마지막 성공: {last_success}")
                
                if connection.response_time:
                    print(f"   응답 시간: {connection.response_time:.2f}s")
                
                print()
            
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"연결 상태 출력 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 연결 관리 테스트")
    
    # 연결 관리자 초기화
    conn_manager = ConnectionManager()
    
    # 테스트 연결 추가
    test_urls = {
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "invalid": "https://invalid-url-test.com"
    }
    
    for name, url in test_urls.items():
        conn_manager.add_connection(name, url)
    
    # 연결 상태 확인
    print("연결 상태 확인:")
    for name in test_urls.keys():
        status = conn_manager.is_connected(name)
        print(f"  {name}: {'✅' if status else '❌'}")
    
    # 연결 상태 출력
    conn_manager.print_connection_status()
