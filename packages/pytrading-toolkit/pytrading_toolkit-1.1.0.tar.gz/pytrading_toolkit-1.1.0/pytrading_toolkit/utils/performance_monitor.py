#!/usr/bin/env python3
"""
성능 모니터링 모듈
시스템 성능 추적 및 최적화
"""

import time
import psutil
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import gc

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    open_files: int

@dataclass
class APIMetrics:
    """API 메트릭"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    data_size: int = 0

@dataclass
class CacheMetrics:
    """캐시 메트릭"""
    cache_name: str
    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 0
    hit_rate: float = 0.0

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, monitoring_interval: int = 30, max_history: int = 1000):
        self.monitoring_interval = monitoring_interval
        self.max_history = max_history
        self.monitoring = False
        self.monitor_thread = None
        
        # 메트릭 저장소
        self.performance_history: deque = deque(maxlen=max_history)
        self.api_history: deque = deque(maxlen=max_history)
        self.cache_metrics: Dict[str, CacheMetrics] = {}
        
        # 성능 임계값
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time': 5.0,
            'cache_hit_rate': 0.7
        }
        
        # 콜백 함수들
        self.alert_callbacks: List[Callable] = []
        
        # 네트워크 통계 초기값
        self._initial_network_stats = self._get_network_stats()
    
    def start_monitoring(self):
        """성능 모니터링 시작"""
        try:
            if self.monitoring:
                logger.warning("이미 모니터링 중입니다")
                return
            
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("성능 모니터링 시작")
            
        except Exception as e:
            logger.error(f"모니터링 시작 실패: {e}")
    
    def stop_monitoring(self):
        """성능 모니터링 중지"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("성능 모니터링 중지")
            
        except Exception as e:
            logger.error(f"모니터링 중지 실패: {e}")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        try:
            while self.monitoring:
                metrics = self._collect_metrics()
                self.performance_history.append(metrics)
                
                # 임계값 확인
                self._check_thresholds(metrics)
                
                time.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"모니터링 루프 오류: {e}")
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """성능 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # 네트워크 통계
            network_stats = self._get_network_stats()
            network_sent_mb = (network_stats['bytes_sent'] - self._initial_network_stats['bytes_sent']) / (1024 * 1024)
            network_recv_mb = (network_stats['bytes_recv'] - self._initial_network_stats['bytes_recv']) / (1024 * 1024)
            
            # 스레드 수
            active_threads = threading.active_count()
            
            # 열린 파일 수
            try:
                process = psutil.Process()
                open_files = len(process.open_files())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                open_files = 0
            
            return PerformanceMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                active_threads=active_threads,
                open_files=open_files
            )
            
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                active_threads=0,
                open_files=0
            )
    
    def _get_network_stats(self) -> Dict[str, int]:
        """네트워크 통계 조회"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            logger.error(f"네트워크 통계 조회 실패: {e}")
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """임계값 확인"""
        try:
            alerts = []
            
            if metrics.cpu_percent > self.thresholds['cpu_percent']:
                alerts.append(f"CPU 사용률 높음: {metrics.cpu_percent:.1f}%")
            
            if metrics.memory_percent > self.thresholds['memory_percent']:
                alerts.append(f"메모리 사용률 높음: {metrics.memory_percent:.1f}%")
            
            if metrics.disk_usage_percent > self.thresholds['disk_usage_percent']:
                alerts.append(f"디스크 사용률 높음: {metrics.disk_usage_percent:.1f}%")
            
            if alerts:
                self._trigger_alerts(alerts)
                
        except Exception as e:
            logger.error(f"임계값 확인 실패: {e}")
    
    def _trigger_alerts(self, alerts: List[str]):
        """알림 트리거"""
        try:
            for callback in self.alert_callbacks:
                try:
                    callback(alerts)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 실패: {e}")
        except Exception as e:
            logger.error(f"알림 트리거 실패: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """알림 콜백 추가"""
        try:
            self.alert_callbacks.append(callback)
            logger.info("알림 콜백 추가됨")
        except Exception as e:
            logger.error(f"알림 콜백 추가 실패: {e}")
    
    def record_api_call(self, endpoint: str, method: str, response_time: float, 
                       status_code: int, success: bool, data_size: int = 0):
        """API 호출 기록"""
        try:
            api_metrics = APIMetrics(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=status_code,
                success=success,
                timestamp=datetime.now(timezone.utc),
                data_size=data_size
            )
            self.api_history.append(api_metrics)
            
            # 임계값 확인
            if response_time > self.thresholds['response_time']:
                self._trigger_alerts([f"API 응답 시간 느림: {endpoint} ({response_time:.2f}s)"])
                
        except Exception as e:
            logger.error(f"API 호출 기록 실패: {e}")
    
    def update_cache_metrics(self, cache_name: str, hits: int, misses: int, 
                           size: int, max_size: int):
        """캐시 메트릭 업데이트"""
        try:
            total_requests = hits + misses
            hit_rate = hits / total_requests if total_requests > 0 else 0.0
            
            self.cache_metrics[cache_name] = CacheMetrics(
                cache_name=cache_name,
                hits=hits,
                misses=misses,
                size=size,
                max_size=max_size,
                hit_rate=hit_rate
            )
            
            # 캐시 히트율 임계값 확인
            if hit_rate < self.thresholds['cache_hit_rate']:
                self._trigger_alerts([f"캐시 히트율 낮음: {cache_name} ({hit_rate:.2%})"])
                
        except Exception as e:
            logger.error(f"캐시 메트릭 업데이트 실패: {e}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """현재 메트릭 반환"""
        try:
            if self.performance_history:
                return self.performance_history[-1]
            return None
        except Exception as e:
            logger.error(f"현재 메트릭 조회 실패: {e}")
            return None
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """성능 요약 반환"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # 최근 메트릭 필터링
            recent_metrics = [
                m for m in self.performance_history 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"error": "데이터 없음"}
            
            # 통계 계산
            cpu_values = [m.cpu_percent for m in recent_metrics]
            memory_values = [m.memory_percent for m in recent_metrics]
            response_times = [m.response_time for m in self.api_history if m.timestamp >= cutoff_time]
            
            return {
                "period_hours": hours,
                "sample_count": len(recent_metrics),
                "cpu": {
                    "avg": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values)
                },
                "memory": {
                    "avg": sum(memory_values) / len(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values)
                },
                "api_calls": {
                    "total": len(response_times),
                    "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "max_response_time": max(response_times) if response_times else 0
                },
                "cache_metrics": {
                    name: {
                        "hit_rate": metrics.hit_rate,
                        "size": metrics.size,
                        "max_size": metrics.max_size
                    } for name, metrics in self.cache_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"성능 요약 조회 실패: {e}")
            return {"error": str(e)}
    
    def optimize_memory(self):
        """메모리 최적화"""
        try:
            # 가비지 컬렉션 실행
            collected = gc.collect()
            logger.info(f"가비지 컬렉션 완료: {collected}개 객체 해제")
            
            # 히스토리 크기 조정
            if len(self.performance_history) > self.max_history * 0.8:
                # 오래된 데이터 제거
                while len(self.performance_history) > self.max_history // 2:
                    self.performance_history.popleft()
                logger.info("성능 히스토리 크기 조정됨")
            
            if len(self.api_history) > self.max_history * 0.8:
                while len(self.api_history) > self.max_history // 2:
                    self.api_history.popleft()
                logger.info("API 히스토리 크기 조정됨")
            
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
    
    def print_performance_status(self):
        """성능 상태 출력"""
        try:
            current = self.get_current_metrics()
            if not current:
                print("📊 성능 데이터 없음")
                return
            
            print("=" * 60)
            print("📊 성능 상태")
            print("=" * 60)
            
            print(f"🖥️  CPU 사용률: {current.cpu_percent:.1f}%")
            print(f"💾 메모리 사용률: {current.memory_percent:.1f}%")
            print(f"   사용 중: {current.memory_used_mb:.1f} MB")
            print(f"   사용 가능: {current.memory_available_mb:.1f} MB")
            print(f"💿 디스크 사용률: {current.disk_usage_percent:.1f}%")
            print(f"🌐 네트워크: 송신 {current.network_sent_mb:.1f} MB, 수신 {current.network_recv_mb:.1f} MB")
            print(f"🧵 활성 스레드: {current.active_threads}개")
            print(f"📁 열린 파일: {current.open_files}개")
            
            # API 통계
            if self.api_history:
                recent_apis = [api for api in self.api_history 
                             if api.timestamp >= datetime.now(timezone.utc) - timedelta(minutes=10)]
                if recent_apis:
                    avg_response = sum(api.response_time for api in recent_apis) / len(recent_apis)
                    success_rate = sum(1 for api in recent_apis if api.success) / len(recent_apis)
                    print(f"🔗 API 호출: {len(recent_apis)}회 (평균 응답시간: {avg_response:.2f}s, 성공률: {success_rate:.1%})")
            
            # 캐시 통계
            if self.cache_metrics:
                print(f"\n💾 캐시 상태:")
                for name, metrics in self.cache_metrics.items():
                    print(f"   {name}: 히트율 {metrics.hit_rate:.1%}, 크기 {metrics.size}/{metrics.max_size}")
            
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"성능 상태 출력 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 성능 모니터링 테스트")
    
    # 모니터 초기화
    monitor = PerformanceMonitor(monitoring_interval=5)
    
    # 알림 콜백 추가
    def alert_callback(alerts):
        print(f"🚨 알림: {', '.join(alerts)}")
    
    monitor.add_alert_callback(alert_callback)
    
    # 모니터링 시작
    monitor.start_monitoring()
    
    try:
        print("성능 모니터링 시작... (10초간)")
        time.sleep(10)
        
        # 성능 상태 출력
        monitor.print_performance_status()
        
        # 성능 요약
        summary = monitor.get_performance_summary()
        print(f"\n성능 요약: {summary}")
        
    finally:
        monitor.stop_monitoring()
