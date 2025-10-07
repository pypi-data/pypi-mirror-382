#!/usr/bin/env python3
"""
실시간 로그 모니터링 도구
로그 파일 실시간 감시 및 알림
"""

import os
import time
import json
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from collections import deque
import re

class LogMonitor:
    """실시간 로그 모니터"""
    
    def __init__(self, log_dir: str, max_lines: int = 1000):
        self.log_dir = Path(log_dir)
        self.max_lines = max_lines
        self.monitoring = False
        self.monitor_thread = None
        
        # 로그 파일 상태 추적
        self.file_positions: Dict[str, int] = {}
        self.log_buffer: deque = deque(maxlen=max_lines)
        
        # 필터 및 알림
        self.filters = []
        self.alert_callbacks: List[Callable] = []
        
        # 통계
        self.stats = {
            'total_lines': 0,
            'filtered_lines': 0,
            'alerts_sent': 0,
            'start_time': None
        }
    
    def add_filter(self, pattern: str, level: Optional[str] = None, 
                   logger_name: Optional[str] = None, case_sensitive: bool = False):
        """로그 필터 추가"""
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(pattern, flags)
            
            filter_config = {
                'pattern': compiled_pattern,
                'level': level,
                'logger_name': logger_name,
                'case_sensitive': case_sensitive
            }
            
            self.filters.append(filter_config)
            print(f"필터 추가됨: {pattern}")
            
        except Exception as e:
            print(f"필터 추가 실패: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """알림 콜백 추가"""
        try:
            self.alert_callbacks.append(callback)
            print("알림 콜백 추가됨")
        except Exception as e:
            print(f"알림 콜백 추가 실패: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            if self.monitoring:
                print("이미 모니터링 중입니다")
                return
            
            self.monitoring = True
            self.stats['start_time'] = datetime.now(timezone.utc)
            
            # 로그 파일 위치 초기화
            self._initialize_file_positions()
            
            # 모니터링 스레드 시작
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            print("실시간 로그 모니터링 시작")
            
        except Exception as e:
            print(f"모니터링 시작 실패: {e}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            print("실시간 로그 모니터링 중지")
            
        except Exception as e:
            print(f"모니터링 중지 실패: {e}")
    
    def _initialize_file_positions(self):
        """파일 위치 초기화"""
        try:
            self.file_positions = {}
            
            # 로그 파일 찾기
            for log_file in self.log_dir.glob("*.log"):
                try:
                    # 파일 끝으로 이동
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(0, 2)  # 파일 끝
                        self.file_positions[str(log_file)] = f.tell()
                except Exception as e:
                    print(f"파일 위치 초기화 실패: {log_file}: {e}")
                    self.file_positions[str(log_file)] = 0
                    
        except Exception as e:
            print(f"파일 위치 초기화 실패: {e}")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        try:
            while self.monitoring:
                self._check_log_files()
                time.sleep(1)  # 1초마다 확인
                
        except Exception as e:
            print(f"모니터링 루프 오류: {e}")
    
    def _check_log_files(self):
        """로그 파일 확인"""
        try:
            for log_file in self.log_dir.glob("*.log"):
                self._read_new_lines(str(log_file))
                
        except Exception as e:
            print(f"로그 파일 확인 실패: {e}")
    
    def _read_new_lines(self, file_path: str):
        """새로운 라인 읽기"""
        try:
            if not os.path.exists(file_path):
                return
            
            current_position = self.file_positions.get(file_path, 0)
            file_size = os.path.getsize(file_path)
            
            if file_size <= current_position:
                return  # 새 라인 없음
            
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(current_position)
                new_lines = f.readlines()
                
                # 위치 업데이트
                self.file_positions[file_path] = f.tell()
                
                # 새 라인 처리
                for line_num, line in enumerate(new_lines, 1):
                    self._process_log_line(line.strip(), file_path, line_num)
                    
        except Exception as e:
            print(f"새 라인 읽기 실패: {file_path}: {e}")
    
    def _process_log_line(self, line: str, file_path: str, line_num: int):
        """로그 라인 처리"""
        try:
            if not line:
                return
            
            self.stats['total_lines'] += 1
            
            # JSON 로그 파싱 시도
            log_entry = self._parse_log_line(line)
            log_entry['file_path'] = file_path
            log_entry['line_number'] = line_num
            
            # 버퍼에 추가
            self.log_buffer.append(log_entry)
            
            # 필터 적용
            if self._matches_filters(log_entry):
                self.stats['filtered_lines'] += 1
                
                # 알림 전송
                self._send_alert(log_entry)
                
        except Exception as e:
            print(f"로그 라인 처리 실패: {e}")
    
    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        """로그 라인 파싱"""
        try:
            # JSON 로그 시도
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass
            
            # 일반 로그 파싱
            # 형식: timestamp - logger - level - message
            pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)$'
            match = re.match(pattern, line)
            
            if match:
                timestamp, logger_name, level, message = match.groups()
                return {
                    'timestamp': timestamp,
                    'logger_name': logger_name,
                    'level': level,
                    'message': message
                }
            
            # 기본 파싱
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': line
            }
            
        except Exception as e:
            print(f"로그 라인 파싱 실패: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'level': 'UNKNOWN',
                'message': line
            }
    
    def _matches_filters(self, log_entry: Dict[str, Any]) -> bool:
        """필터 매칭 확인"""
        try:
            if not self.filters:
                return True  # 필터가 없으면 모든 로그 통과
            
            for filter_config in self.filters:
                # 레벨 필터
                if filter_config['level'] and log_entry.get('level') != filter_config['level']:
                    continue
                
                # 로거 필터
                if filter_config['logger_name'] and log_entry.get('logger_name') != filter_config['logger_name']:
                    continue
                
                # 패턴 필터
                message = log_entry.get('message', '')
                if filter_config['pattern'].search(message):
                    return True
            
            return False
            
        except Exception as e:
            print(f"필터 매칭 확인 실패: {e}")
            return False
    
    def _send_alert(self, log_entry: Dict[str, Any]):
        """알림 전송"""
        try:
            self.stats['alerts_sent'] += 1
            
            for callback in self.alert_callbacks:
                try:
                    callback(log_entry)
                except Exception as e:
                    print(f"알림 콜백 실행 실패: {e}")
                    
        except Exception as e:
            print(f"알림 전송 실패: {e}")
    
    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """최근 로그 반환"""
        try:
            return list(self.log_buffer)[-count:]
        except Exception as e:
            print(f"최근 로그 조회 실패: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        try:
            stats = self.stats.copy()
            
            if stats['start_time']:
                runtime = datetime.now(timezone.utc) - stats['start_time']
                stats['runtime_seconds'] = runtime.total_seconds()
                stats['lines_per_second'] = stats['total_lines'] / runtime.total_seconds() if runtime.total_seconds() > 0 else 0
            
            return stats
            
        except Exception as e:
            print(f"통계 조회 실패: {e}")
            return {}
    
    def print_recent_logs(self, count: int = 10):
        """최근 로그 출력"""
        try:
            recent_logs = self.get_recent_logs(count)
            
            print("=" * 80)
            print(f"📋 최근 로그 ({len(recent_logs)}개)")
            print("=" * 80)
            
            for log in recent_logs:
                timestamp = log.get('timestamp', 'N/A')
                level = log.get('level', 'N/A')
                logger_name = log.get('logger_name', 'N/A')
                message = log.get('message', 'N/A')[:100]  # 100자로 제한
                
                print(f"[{timestamp}] {level:8} {logger_name:20} {message}")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"최근 로그 출력 실패: {e}")
    
    def print_stats(self):
        """통계 출력"""
        try:
            stats = self.get_stats()
            
            print("=" * 60)
            print("📊 로그 모니터링 통계")
            print("=" * 60)
            
            print(f"📈 총 처리 라인: {stats['total_lines']:,}개")
            print(f"🔍 필터링된 라인: {stats['filtered_lines']:,}개")
            print(f"🚨 전송된 알림: {stats['alerts_sent']:,}개")
            
            if stats.get('runtime_seconds'):
                print(f"⏱️ 실행 시간: {stats['runtime_seconds']:.1f}초")
                print(f"📊 초당 처리량: {stats['lines_per_second']:.1f}라인/초")
            
            print(f"📋 활성 필터: {len(self.filters)}개")
            print(f"🔔 알림 콜백: {len(self.alert_callbacks)}개")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"통계 출력 실패: {e}")

def create_error_alert_callback():
    """에러 알림 콜백 생성"""
    def alert_callback(log_entry):
        level = log_entry.get('level', '')
        message = log_entry.get('message', '')
        
        if level in ['ERROR', 'CRITICAL']:
            print(f"🚨 에러 알림: [{level}] {message}")
    
    return alert_callback

def create_performance_alert_callback():
    """성능 알림 콜백 생성"""
    def alert_callback(log_entry):
        message = log_entry.get('message', '')
        
        if 'slow' in message.lower() or 'timeout' in message.lower():
            print(f"⚠️ 성능 알림: {message}")
    
    return alert_callback

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 실시간 로그 모니터링 테스트")
    
    # 로그 모니터 초기화
    monitor = LogMonitor("test_logs")
    
    # 필터 추가
    monitor.add_filter(r"error|exception|failed", level="ERROR")
    monitor.add_filter(r"slow|timeout|performance")
    
    # 알림 콜백 추가
    monitor.add_alert_callback(create_error_alert_callback())
    monitor.add_alert_callback(create_performance_alert_callback())
    
    try:
        # 모니터링 시작
        monitor.start_monitoring()
        
        print("실시간 로그 모니터링 시작... (30초간)")
        time.sleep(30)
        
        # 최근 로그 출력
        monitor.print_recent_logs(5)
        
        # 통계 출력
        monitor.print_stats()
        
    finally:
        monitor.stop_monitoring()
