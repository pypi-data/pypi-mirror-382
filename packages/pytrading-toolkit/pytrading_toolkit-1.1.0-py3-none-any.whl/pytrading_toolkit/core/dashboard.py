#!/usr/bin/env python3
"""
시스템 상태 모니터링 대시보드
실시간 시스템 상태 모니터링 및 시각화
"""

import os
import time
import json
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class DashboardData:
    """대시보드 데이터"""
    timestamp: datetime
    system_status: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    security_metrics: Dict[str, Any]
    trading_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    trends: Dict[str, List[Tuple[datetime, float]]]

class SystemDashboard:
    """시스템 대시보드"""
    
    def __init__(self, system_manager, update_interval: int = 5):
        self.system_manager = system_manager
        self.update_interval = update_interval
        self.dashboard_data = []
        self.max_data_points = 1000
        
        # 대시보드 상태
        self.is_running = False
        self.update_thread = None
        
        # 알림 임계값
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'error_rate': 5.0,
            'risk_events': 10,
            'response_time': 5.0
        }
        
        # 트렌드 데이터
        self.trend_data = {
            'cpu_percent': [],
            'memory_percent': [],
            'error_rate': [],
            'trading_volume': [],
            'api_calls': []
        }
    
    def start_dashboard(self):
        """대시보드 시작"""
        try:
            if self.is_running:
                logger.warning("대시보드가 이미 실행 중입니다")
                return
            
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            logger.info("시스템 대시보드 시작")
            
        except Exception as e:
            logger.error(f"대시보드 시작 실패: {e}")
    
    def stop_dashboard(self):
        """대시보드 중지"""
        try:
            self.is_running = False
            if self.update_thread:
                self.update_thread.join(timeout=5)
            
            logger.info("시스템 대시보드 중지")
            
        except Exception as e:
            logger.error(f"대시보드 중지 실패: {e}")
    
    def _update_loop(self):
        """업데이트 루프"""
        try:
            while self.is_running:
                self._update_dashboard_data()
                time.sleep(self.update_interval)
                
        except Exception as e:
            logger.error(f"대시보드 업데이트 루프 오류: {e}")
    
    def _update_dashboard_data(self):
        """대시보드 데이터 업데이트"""
        try:
            # 시스템 상태 조회
            system_status = self.system_manager.get_system_status()
            
            # 성능 메트릭
            performance_metrics = self._get_performance_metrics()
            
            # 보안 메트릭
            security_metrics = self._get_security_metrics()
            
            # 거래 메트릭
            trading_metrics = self._get_trading_metrics()
            
            # 알림 확인
            alerts = self._check_alerts(system_status, performance_metrics, security_metrics)
            
            # 트렌드 데이터 업데이트
            self._update_trend_data(performance_metrics, trading_metrics)
            
            # 대시보드 데이터 생성
            dashboard_data = DashboardData(
                timestamp=datetime.now(timezone.utc),
                system_status=asdict(system_status),
                performance_metrics=performance_metrics,
                security_metrics=security_metrics,
                trading_metrics=trading_metrics,
                alerts=alerts,
                trends=self.trend_data.copy()
            )
            
            # 데이터 저장
            self.dashboard_data.append(dashboard_data)
            
            # 오래된 데이터 제거
            if len(self.dashboard_data) > self.max_data_points:
                self.dashboard_data = self.dashboard_data[-self.max_data_points:]
            
        except Exception as e:
            logger.error(f"대시보드 데이터 업데이트 실패: {e}")
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        try:
            if not self.system_manager.performance_monitor:
                return {}
            
            current_metrics = self.system_manager.performance_monitor.get_current_metrics()
            if not current_metrics:
                return {}
            
            return {
                'cpu_percent': current_metrics.cpu_percent,
                'memory_percent': current_metrics.memory_percent,
                'memory_used_mb': current_metrics.memory_used_mb,
                'memory_available_mb': current_metrics.memory_available_mb,
                'disk_usage_percent': current_metrics.disk_usage_percent,
                'network_sent_mb': current_metrics.network_sent_mb,
                'network_recv_mb': current_metrics.network_recv_mb,
                'active_threads': current_metrics.active_threads,
                'open_files': current_metrics.open_files
            }
            
        except Exception as e:
            logger.error(f"성능 메트릭 조회 실패: {e}")
            return {}
    
    def _get_security_metrics(self) -> Dict[str, Any]:
        """보안 메트릭 조회"""
        try:
            if not self.system_manager.audit_logger:
                return {}
            
            stats = self.system_manager.audit_logger.get_stats()
            return {
                'total_events': stats.get('total_events', 0),
                'risk_events': stats.get('risk_events', 0),
                'error_rate': stats.get('errors', 0) / max(stats.get('total_events', 1), 1) * 100,
                'events_by_type': stats.get('by_type', {}),
                'events_by_level': stats.get('by_level', {}),
                'events_by_user': stats.get('by_user', {})
            }
            
        except Exception as e:
            logger.error(f"보안 메트릭 조회 실패: {e}")
            return {}
    
    def _get_trading_metrics(self) -> Dict[str, Any]:
        """거래 메트릭 조회"""
        try:
            metrics = {
                'active_traders': 0,
                'total_volume': 0.0,
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'profit_loss': 0.0
            }
            
            # 바이비트 트레이더 메트릭
            if 'bybit' in self.system_manager.traders:
                trader = self.system_manager.traders['bybit']
                # 실제 구현에서는 거래 통계를 조회
                metrics['active_traders'] += 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"거래 메트릭 조회 실패: {e}")
            return {}
    
    def _check_alerts(self, system_status, performance_metrics, security_metrics) -> List[Dict[str, Any]]:
        """알림 확인"""
        try:
            alerts = []
            current_time = datetime.now(timezone.utc)
            
            # CPU 사용률 알림
            cpu_percent = performance_metrics.get('cpu_percent', 0)
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'performance',
                    'level': 'warning' if cpu_percent < 90 else 'critical',
                    'message': f"높은 CPU 사용률: {cpu_percent:.1f}%",
                    'timestamp': current_time.isoformat(),
                    'value': cpu_percent
                })
            
            # 메모리 사용률 알림
            memory_percent = performance_metrics.get('memory_percent', 0)
            if memory_percent > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'type': 'performance',
                    'level': 'warning' if memory_percent < 95 else 'critical',
                    'message': f"높은 메모리 사용률: {memory_percent:.1f}%",
                    'timestamp': current_time.isoformat(),
                    'value': memory_percent
                })
            
            # 에러율 알림
            error_rate = security_metrics.get('error_rate', 0)
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'security',
                    'level': 'warning' if error_rate < 10 else 'critical',
                    'message': f"높은 에러율: {error_rate:.1f}%",
                    'timestamp': current_time.isoformat(),
                    'value': error_rate
                })
            
            # 위험 이벤트 알림
            risk_events = security_metrics.get('risk_events', 0)
            if risk_events > self.alert_thresholds['risk_events']:
                alerts.append({
                    'type': 'security',
                    'level': 'warning' if risk_events < 20 else 'critical',
                    'message': f"높은 위험 이벤트 수: {risk_events}개",
                    'timestamp': current_time.isoformat(),
                    'value': risk_events
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"알림 확인 실패: {e}")
            return []
    
    def _update_trend_data(self, performance_metrics, trading_metrics):
        """트렌드 데이터 업데이트"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # 성능 트렌드
            self.trend_data['cpu_percent'].append((current_time, performance_metrics.get('cpu_percent', 0)))
            self.trend_data['memory_percent'].append((current_time, performance_metrics.get('memory_percent', 0)))
            self.trend_data['error_rate'].append((current_time, performance_metrics.get('error_rate', 0)))
            
            # 거래 트렌드
            self.trend_data['trading_volume'].append((current_time, trading_metrics.get('total_volume', 0)))
            self.trend_data['api_calls'].append((current_time, trading_metrics.get('total_trades', 0)))
            
            # 오래된 데이터 제거 (1시간 이상)
            cutoff_time = current_time - timedelta(hours=1)
            for key in self.trend_data:
                self.trend_data[key] = [
                    (timestamp, value) for timestamp, value in self.trend_data[key]
                    if timestamp >= cutoff_time
                ]
                
        except Exception as e:
            logger.error(f"트렌드 데이터 업데이트 실패: {e}")
    
    def get_dashboard_data(self, hours: int = 1) -> List[Dict[str, Any]]:
        """대시보드 데이터 반환"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            filtered_data = [
                asdict(data) for data in self.dashboard_data
                if data.timestamp >= cutoff_time
            ]
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"대시보드 데이터 조회 실패: {e}")
            return []
    
    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        try:
            if not self.dashboard_data:
                return {}
            
            latest_data = self.dashboard_data[-1]
            return asdict(latest_data)
            
        except Exception as e:
            logger.error(f"현재 상태 조회 실패: {e}")
            return {}
    
    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """알림 목록 반환"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            all_alerts = []
            for data in self.dashboard_data:
                if data.timestamp >= cutoff_time:
                    all_alerts.extend(data.alerts)
            
            # 시간순 정렬
            all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return all_alerts
            
        except Exception as e:
            logger.error(f"알림 목록 조회 실패: {e}")
            return []
    
    def get_trends(self, metric: str, hours: int = 1) -> List[Tuple[str, float]]:
        """트렌드 데이터 반환"""
        try:
            if metric not in self.trend_data:
                return []
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            trend_data = [
                (timestamp.isoformat(), value)
                for timestamp, value in self.trend_data[metric]
                if timestamp >= cutoff_time
            ]
            
            return trend_data
            
        except Exception as e:
            logger.error(f"트렌드 데이터 조회 실패: {e}")
            return []
    
    def print_dashboard(self):
        """대시보드 출력"""
        try:
            current_status = self.get_current_status()
            if not current_status:
                print("대시보드 데이터가 없습니다")
                return
            
            print("=" * 100)
            print("📊 시스템 대시보드")
            print("=" * 100)
            
            # 시스템 상태
            system_status = current_status.get('system_status', {})
            print(f"🔄 시스템 상태: {'실행 중' if system_status.get('is_running') else '중지됨'}")
            print(f"⏱️ 가동 시간: {system_status.get('uptime_seconds', 0):.0f}초")
            
            # 성능 메트릭
            performance = current_status.get('performance_metrics', {})
            if performance:
                print(f"\n📈 성능 메트릭:")
                print(f"  CPU 사용률: {performance.get('cpu_percent', 0):.1f}%")
                print(f"  메모리 사용률: {performance.get('memory_percent', 0):.1f}%")
                print(f"  메모리 사용량: {performance.get('memory_used_mb', 0):.1f} MB")
                print(f"  활성 스레드: {performance.get('active_threads', 0)}개")
                print(f"  열린 파일: {performance.get('open_files', 0)}개")
            
            # 보안 메트릭
            security = current_status.get('security_metrics', {})
            if security:
                print(f"\n🔒 보안 메트릭:")
                print(f"  총 이벤트: {security.get('total_events', 0):,}개")
                print(f"  위험 이벤트: {security.get('risk_events', 0):,}개")
                print(f"  에러율: {security.get('error_rate', 0):.2f}%")
            
            # 거래 메트릭
            trading = current_status.get('trading_metrics', {})
            if trading:
                print(f"\n💰 거래 메트릭:")
                print(f"  활성 트레이더: {trading.get('active_traders', 0)}개")
                print(f"  총 거래량: {trading.get('total_volume', 0):.2f}")
                print(f"  총 거래 수: {trading.get('total_trades', 0)}회")
                print(f"  성공률: {trading.get('successful_trades', 0) / max(trading.get('total_trades', 1), 1) * 100:.1f}%")
            
            # 최근 알림
            alerts = self.get_alerts(hours=1)
            if alerts:
                print(f"\n🚨 최근 알림 ({len(alerts)}개):")
                for alert in alerts[:5]:  # 최근 5개만
                    level_icon = "🔴" if alert['level'] == 'critical' else "🟡"
                    print(f"  {level_icon} [{alert['type']}] {alert['message']}")
            
            # 컴포넌트 상태
            components = system_status.get('components', {})
            if components:
                print(f"\n🔧 컴포넌트 상태:")
                for component, is_healthy in components.items():
                    status_icon = "✅" if is_healthy else "❌"
                    print(f"  {status_icon} {component}")
            
            print("=" * 100)
            
        except Exception as e:
            logger.error(f"대시보드 출력 실패: {e}")
    
    def export_dashboard_data(self, file_path: str, hours: int = 24):
        """대시보드 데이터 내보내기"""
        try:
            data = self.get_dashboard_data(hours)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"대시보드 데이터 내보내기 완료: {file_path}")
            
        except Exception as e:
            logger.error(f"대시보드 데이터 내보내기 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 시스템 대시보드 테스트")
    
    # 시스템 관리자와 대시보드 초기화
    from .system_manager import SystemManager
    
    system_manager = SystemManager("test_config", "test_logs")
    dashboard = SystemDashboard(system_manager)
    
    try:
        # 시스템 시작
        print("1. 시스템 시작")
        system_manager.start_system()
        
        # 대시보드 시작
        print("2. 대시보드 시작")
        dashboard.start_dashboard()
        
        # 대시보드 실행 (30초)
        print("3. 대시보드 실행 (30초)")
        for i in range(6):
            time.sleep(5)
            print(f"\n--- {i+1}번째 업데이트 ---")
            dashboard.print_dashboard()
        
        # 대시보드 중지
        print("\n4. 대시보드 중지")
        dashboard.stop_dashboard()
        
        # 시스템 중지
        print("5. 시스템 중지")
        system_manager.stop_system()
        
    except Exception as e:
        print(f"❌ 대시보드 테스트 실패: {e}")
