#!/usr/bin/env python3
"""
보안 감사 로깅 모듈
보안 관련 이벤트 감사 및 로깅
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
import queue

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """보안 이벤트 타입"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PERMISSION_DENIED = "permission_denied"
    API_KEY_ACCESS = "api_key_access"
    CONFIG_CHANGE = "config_change"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_ERROR = "system_error"
    DATA_ACCESS = "data_access"
    TRADING_ACTION = "trading_action"

class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """보안 이벤트"""
    event_id: str
    event_type: SecurityEventType
    security_level: SecurityLevel
    timestamp: datetime
    username: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    description: str
    details: Dict[str, Any]
    risk_score: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['security_level'] = self.security_level.value
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

class SecurityAuditLogger:
    """보안 감사 로거"""
    
    def __init__(self, audit_dir: str = "audit_logs", max_file_size_mb: int = 100):
        self.audit_dir = Path(audit_dir)
        self.max_file_size_mb = max_file_size_mb
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        # 감사 디렉토리 생성
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # 이벤트 큐
        self.event_queue = queue.Queue(maxsize=10000)
        self.processing = False
        self.process_thread = None
        
        # 통계
        self.stats = {
            'total_events': 0,
            'by_type': {},
            'by_level': {},
            'by_user': {},
            'risk_events': 0
        }
        
        # 위험 점수 임계값
        self.risk_thresholds = {
            SecurityLevel.LOW: 10,
            SecurityLevel.MEDIUM: 30,
            SecurityLevel.HIGH: 60,
            SecurityLevel.CRITICAL: 90
        }
        
        # 알림 콜백
        self.alert_callbacks = []
        
        self._start_processing()
    
    def _start_processing(self):
        """이벤트 처리 시작"""
        try:
            self.processing = True
            self.process_thread = threading.Thread(target=self._process_events, daemon=True)
            self.process_thread.start()
            logger.info("보안 감사 로거 시작")
        except Exception as e:
            logger.error(f"보안 감사 로거 시작 실패: {e}")
    
    def _stop_processing(self):
        """이벤트 처리 중지"""
        try:
            self.processing = False
            if self.process_thread:
                self.process_thread.join(timeout=5)
            logger.info("보안 감사 로거 중지")
        except Exception as e:
            logger.error(f"보안 감사 로거 중지 실패: {e}")
    
    def _process_events(self):
        """이벤트 처리 루프"""
        try:
            while self.processing:
                try:
                    event = self.event_queue.get(timeout=1)
                    self._write_audit_event(event)
                    self._update_stats(event)
                    self._check_risk_threshold(event)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"이벤트 처리 오류: {e}")
        except Exception as e:
            logger.error(f"이벤트 처리 루프 실패: {e}")
    
    def _write_audit_event(self, event: SecurityEvent):
        """감사 이벤트 파일에 쓰기"""
        try:
            # 날짜별 파일 분리
            date_str = event.timestamp.strftime("%Y%m%d")
            audit_file = self.audit_dir / f"audit_{date_str}.log"
            
            # 파일 크기 확인 및 로테이션
            if audit_file.exists() and audit_file.stat().st_size >= self.max_file_size_bytes:
                self._rotate_audit_file(audit_file)
            
            # 이벤트 쓰기
            with open(audit_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
            
            # 파일 권한 설정
            os.chmod(audit_file, 0o600)
            
        except Exception as e:
            logger.error(f"감사 이벤트 쓰기 실패: {e}")
    
    def _rotate_audit_file(self, file_path: Path):
        """감사 파일 로테이션"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            rotated_path = file_path.parent / rotated_name
            
            file_path.rename(rotated_path)
            
            # 압축
            self._compress_file(rotated_path)
            
        except Exception as e:
            logger.error(f"감사 파일 로테이션 실패: {e}")
    
    def _compress_file(self, file_path: Path):
        """파일 압축"""
        try:
            import gzip
            
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            file_path.unlink()
            
        except Exception as e:
            logger.error(f"파일 압축 실패: {e}")
    
    def _update_stats(self, event: SecurityEvent):
        """통계 업데이트"""
        try:
            self.stats['total_events'] += 1
            
            # 타입별 통계
            event_type = event.event_type.value
            self.stats['by_type'][event_type] = self.stats['by_type'].get(event_type, 0) + 1
            
            # 레벨별 통계
            security_level = event.security_level.value
            self.stats['by_level'][security_level] = self.stats['by_level'].get(security_level, 0) + 1
            
            # 사용자별 통계
            if event.username:
                self.stats['by_user'][event.username] = self.stats['by_user'].get(event.username, 0) + 1
            
            # 위험 이벤트 통계
            if event.risk_score >= self.risk_thresholds.get(event.security_level, 0):
                self.stats['risk_events'] += 1
                
        except Exception as e:
            logger.error(f"통계 업데이트 실패: {e}")
    
    def _check_risk_threshold(self, event: SecurityEvent):
        """위험 임계값 확인"""
        try:
            if event.risk_score >= self.risk_thresholds.get(event.security_level, 0):
                self._trigger_alert(event)
        except Exception as e:
            logger.error(f"위험 임계값 확인 실패: {e}")
    
    def _trigger_alert(self, event: SecurityEvent):
        """보안 알림 트리거"""
        try:
            for callback in self.alert_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"보안 알림 콜백 실행 실패: {e}")
        except Exception as e:
            logger.error(f"보안 알림 트리거 실패: {e}")
    
    def log_event(self, event_type: SecurityEventType, security_level: SecurityLevel,
                  description: str, username: Optional[str] = None,
                  session_id: Optional[str] = None, ip_address: str = "",
                  user_agent: str = "", details: Optional[Dict[str, Any]] = None,
                  risk_score: int = 0):
        """보안 이벤트 로깅"""
        try:
            # 이벤트 ID 생성
            event_id = self._generate_event_id()
            
            # 이벤트 생성
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                security_level=security_level,
                timestamp=datetime.now(timezone.utc),
                username=username,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                description=description,
                details=details or {},
                risk_score=risk_score
            )
            
            # 큐에 추가
            try:
                self.event_queue.put_nowait(event)
            except queue.Full:
                logger.warning("감사 이벤트 큐가 가득참")
            
        except Exception as e:
            logger.error(f"보안 이벤트 로깅 실패: {e}")
    
    def _generate_event_id(self) -> str:
        """이벤트 ID 생성"""
        try:
            timestamp = datetime.now().timestamp()
            random_data = os.urandom(16)
            data = f"{timestamp}{random_data}".encode()
            return hashlib.sha256(data).hexdigest()[:16]
        except Exception as e:
            logger.error(f"이벤트 ID 생성 실패: {e}")
            return "unknown"
    
    def log_login_success(self, username: str, ip_address: str, user_agent: str):
        """로그인 성공 로깅"""
        self.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            SecurityLevel.LOW,
            f"사용자 로그인 성공: {username}",
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_score=5
        )
    
    def log_login_failure(self, username: str, ip_address: str, user_agent: str, reason: str):
        """로그인 실패 로깅"""
        self.log_event(
            SecurityEventType.LOGIN_FAILURE,
            SecurityLevel.MEDIUM,
            f"사용자 로그인 실패: {username} - {reason}",
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            risk_score=20
        )
    
    def log_permission_denied(self, username: str, permission: str, resource: str, ip_address: str):
        """권한 거부 로깅"""
        self.log_event(
            SecurityEventType.PERMISSION_DENIED,
            SecurityLevel.HIGH,
            f"권한 거부: {username} - {permission} on {resource}",
            username=username,
            ip_address=ip_address,
            details={"permission": permission, "resource": resource},
            risk_score=40
        )
    
    def log_api_key_access(self, username: str, exchange: str, action: str, ip_address: str):
        """API 키 접근 로깅"""
        self.log_event(
            SecurityEventType.API_KEY_ACCESS,
            SecurityLevel.HIGH,
            f"API 키 접근: {username} - {action} {exchange}",
            username=username,
            ip_address=ip_address,
            details={"exchange": exchange, "action": action},
            risk_score=30
        )
    
    def log_trading_action(self, username: str, action: str, symbol: str, 
                          quantity: float, price: float, ip_address: str):
        """거래 액션 로깅"""
        self.log_event(
            SecurityEventType.TRADING_ACTION,
            SecurityLevel.CRITICAL,
            f"거래 액션: {username} - {action} {symbol}",
            username=username,
            ip_address=ip_address,
            details={
                "action": action,
                "symbol": symbol,
                "quantity": quantity,
                "price": price
            },
            risk_score=50
        )
    
    def log_suspicious_activity(self, description: str, ip_address: str, 
                               user_agent: str = "", details: Optional[Dict[str, Any]] = None):
        """의심스러운 활동 로깅"""
        self.log_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityLevel.CRITICAL,
            f"의심스러운 활동: {description}",
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            risk_score=80
        )
    
    def add_alert_callback(self, callback):
        """알림 콜백 추가"""
        try:
            self.alert_callbacks.append(callback)
        except Exception as e:
            logger.error(f"알림 콜백 추가 실패: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()
    
    def search_events(self, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     event_type: Optional[SecurityEventType] = None,
                     username: Optional[str] = None,
                     security_level: Optional[SecurityLevel] = None) -> List[SecurityEvent]:
        """이벤트 검색"""
        try:
            events = []
            
            # 감사 파일 검색
            for audit_file in self.audit_dir.glob("audit_*.log"):
                try:
                    with open(audit_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                event_data = json.loads(line.strip())
                                event = self._parse_event_data(event_data)
                                
                                # 필터 적용
                                if self._matches_filters(event, start_date, end_date, 
                                                       event_type, username, security_level):
                                    events.append(event)
                                    
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    logger.error(f"감사 파일 읽기 실패: {audit_file}: {e}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"이벤트 검색 실패: {e}")
            return []
    
    def _parse_event_data(self, event_data: Dict[str, Any]) -> SecurityEvent:
        """이벤트 데이터 파싱"""
        try:
            return SecurityEvent(
                event_id=event_data['event_id'],
                event_type=SecurityEventType(event_data['event_type']),
                security_level=SecurityLevel(event_data['security_level']),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                username=event_data.get('username'),
                session_id=event_data.get('session_id'),
                ip_address=event_data['ip_address'],
                user_agent=event_data['user_agent'],
                description=event_data['description'],
                details=event_data['details'],
                risk_score=event_data.get('risk_score', 0)
            )
        except Exception as e:
            logger.error(f"이벤트 데이터 파싱 실패: {e}")
            raise
    
    def _matches_filters(self, event: SecurityEvent, start_date: Optional[datetime],
                        end_date: Optional[datetime], event_type: Optional[SecurityEventType],
                        username: Optional[str], security_level: Optional[SecurityLevel]) -> bool:
        """필터 매칭 확인"""
        try:
            # 날짜 필터
            if start_date and event.timestamp < start_date:
                return False
            if end_date and event.timestamp > end_date:
                return False
            
            # 이벤트 타입 필터
            if event_type and event.event_type != event_type:
                return False
            
            # 사용자 필터
            if username and event.username != username:
                return False
            
            # 보안 레벨 필터
            if security_level and event.security_level != security_level:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"필터 매칭 확인 실패: {e}")
            return False
    
    def generate_security_report(self, days: int = 7) -> str:
        """보안 보고서 생성"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            events = self.search_events(start_date, end_date)
            
            report = []
            report.append("=" * 80)
            report.append("🔒 보안 감사 보고서")
            report.append("=" * 80)
            
            report.append(f"📅 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
            report.append(f"📊 총 이벤트: {len(events)}개")
            report.append("")
            
            # 이벤트 타입별 통계
            event_types = {}
            for event in events:
                event_type = event.event_type.value
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if event_types:
                report.append("📋 이벤트 타입별 통계:")
                for event_type, count in sorted(event_types.items()):
                    report.append(f"  {event_type}: {count}개")
                report.append("")
            
            # 보안 레벨별 통계
            security_levels = {}
            for event in events:
                level = event.security_level.value
                security_levels[level] = security_levels.get(level, 0) + 1
            
            if security_levels:
                report.append("🚨 보안 레벨별 통계:")
                for level, count in sorted(security_levels.items()):
                    report.append(f"  {level}: {count}개")
                report.append("")
            
            # 위험 이벤트
            risk_events = [e for e in events if e.risk_score >= 50]
            if risk_events:
                report.append("⚠️ 위험 이벤트 (최근 5개):")
                for event in risk_events[-5:]:
                    report.append(f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.description}")
                    report.append(f"    위험도: {event.risk_score}, IP: {event.ip_address}")
                report.append("")
            
            report.append("=" * 80)
            
            return "\n".join(report)
            
        except Exception as e:
            return f"보안 보고서 생성 실패: {e}"
    
    def cleanup(self):
        """리소스 정리"""
        try:
            self._stop_processing()
            logger.info("보안 감사 로거 정리 완료")
        except Exception as e:
            logger.error(f"보안 감사 로거 정리 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 보안 감사 로깅 테스트")
    
    # 보안 감사 로거 초기화
    audit_logger = SecurityAuditLogger("test_audit_logs")
    
    try:
        # 다양한 보안 이벤트 로깅
        print("1. 보안 이벤트 로깅 테스트")
        
        audit_logger.log_login_success("admin", "192.168.1.100", "Mozilla/5.0")
        audit_logger.log_login_failure("hacker", "192.168.1.200", "curl/7.0", "invalid_password")
        audit_logger.log_permission_denied("user1", "execute_trading", "BTCUSDT", "192.168.1.101")
        audit_logger.log_api_key_access("admin", "upbit", "view", "192.168.1.100")
        audit_logger.log_trading_action("trader1", "buy", "BTCUSDT", 0.001, 50000, "192.168.1.102")
        audit_logger.log_suspicious_activity("다중 로그인 실패", "192.168.1.200")
        
        # 이벤트 처리 대기
        time.sleep(2)
        
        # 통계 확인
        print("\n2. 통계 확인")
        stats = audit_logger.get_stats()
        print(f"총 이벤트: {stats['total_events']}")
        print(f"위험 이벤트: {stats['risk_events']}")
        
        # 이벤트 검색
        print("\n3. 이벤트 검색")
        events = audit_logger.search_events(username="admin")
        print(f"admin 사용자 이벤트: {len(events)}개")
        
        # 보안 보고서 생성
        print("\n4. 보안 보고서")
        report = audit_logger.generate_security_report(days=1)
        print(report[:500] + "..." if len(report) > 500 else report)
        
    finally:
        audit_logger.cleanup()
