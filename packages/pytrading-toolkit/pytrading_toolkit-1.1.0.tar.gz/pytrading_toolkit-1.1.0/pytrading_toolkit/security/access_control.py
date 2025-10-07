#!/usr/bin/env python3
"""
접근 제어 및 권한 관리 모듈
사용자 권한 및 접근 제어 관리
"""

import os
import time
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class Permission(Enum):
    """권한 타입"""
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    EXECUTE_TRADING = "execute_trading"
    VIEW_BALANCE = "view_balance"
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_LOGS = "view_logs"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"

class Role(Enum):
    """역할 타입"""
    VIEWER = "viewer"
    TRADER = "trader"
    MANAGER = "manager"
    ADMIN = "admin"

@dataclass
class User:
    """사용자 정보"""
    username: str
    password_hash: str
    salt: str
    role: Role
    permissions: Set[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class Session:
    """세션 정보"""
    session_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class AccessControlManager:
    """접근 제어 관리자"""
    
    def __init__(self, users_file: str = ".users.json", sessions_file: str = ".sessions.json"):
        self.users_file = users_file
        self.sessions_file = sessions_file
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.role_permissions = self._initialize_role_permissions()
        
        # 보안 설정
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=24)
        self.max_sessions_per_user = 3
        
        # 이벤트 콜백
        self.event_callbacks: Dict[str, List[Callable]] = {
            "login": [],
            "logout": [],
            "permission_denied": [],
            "account_locked": [],
            "suspicious_activity": []
        }
        
        self._load_users()
        self._load_sessions()
    
    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """역할별 권한 초기화"""
        return {
            Role.VIEWER: {
                Permission.READ_CONFIG,
                Permission.VIEW_BALANCE,
                Permission.VIEW_LOGS
            },
            Role.TRADER: {
                Permission.READ_CONFIG,
                Permission.EXECUTE_TRADING,
                Permission.VIEW_BALANCE,
                Permission.VIEW_LOGS
            },
            Role.MANAGER: {
                Permission.READ_CONFIG,
                Permission.WRITE_CONFIG,
                Permission.EXECUTE_TRADING,
                Permission.VIEW_BALANCE,
                Permission.MANAGE_API_KEYS,
                Permission.VIEW_LOGS
            },
            Role.ADMIN: {
                Permission.READ_CONFIG,
                Permission.WRITE_CONFIG,
                Permission.EXECUTE_TRADING,
                Permission.VIEW_BALANCE,
                Permission.MANAGE_API_KEYS,
                Permission.VIEW_LOGS,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_ADMIN
            }
        }
    
    def _hash_password(self, password: str, salt: str) -> str:
        """비밀번호 해시"""
        try:
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        except Exception as e:
            logger.error(f"비밀번호 해시 실패: {e}")
            return ""
    
    def _generate_salt(self) -> str:
        """솔트 생성"""
        return secrets.token_hex(32)
    
    def _load_users(self):
        """사용자 데이터 로드"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for username, user_data in data.items():
                    self.users[username] = User(
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        salt=user_data['salt'],
                        role=Role(user_data['role']),
                        permissions=set(Permission(p) for p in user_data['permissions']),
                        created_at=datetime.fromisoformat(user_data['created_at']),
                        last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                        is_active=user_data.get('is_active', True),
                        failed_attempts=user_data.get('failed_attempts', 0),
                        locked_until=datetime.fromisoformat(user_data['locked_until']) if user_data.get('locked_until') else None
                    )
                    
        except Exception as e:
            logger.error(f"사용자 데이터 로드 실패: {e}")
    
    def _save_users(self):
        """사용자 데이터 저장"""
        try:
            data = {}
            for username, user in self.users.items():
                data[username] = {
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'salt': user.salt,
                    'role': user.role.value,
                    'permissions': [p.value for p in user.permissions],
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active,
                    'failed_attempts': user.failed_attempts,
                    'locked_until': user.locked_until.isoformat() if user.locked_until else None
                }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 파일 권한 설정
            os.chmod(self.users_file, 0o600)
            
        except Exception as e:
            logger.error(f"사용자 데이터 저장 실패: {e}")
    
    def _load_sessions(self):
        """세션 데이터 로드"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for session_id, session_data in data.items():
                    self.sessions[session_id] = Session(
                        session_id=session_data['session_id'],
                        username=session_data['username'],
                        created_at=datetime.fromisoformat(session_data['created_at']),
                        last_activity=datetime.fromisoformat(session_data['last_activity']),
                        ip_address=session_data['ip_address'],
                        user_agent=session_data['user_agent'],
                        is_active=session_data.get('is_active', True)
                    )
                    
        except Exception as e:
            logger.error(f"세션 데이터 로드 실패: {e}")
    
    def _save_sessions(self):
        """세션 데이터 저장"""
        try:
            data = {}
            for session_id, session in self.sessions.items():
                data[session_id] = {
                    'session_id': session.session_id,
                    'username': session.username,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'ip_address': session.ip_address,
                    'user_agent': session.user_agent,
                    'is_active': session.is_active
                }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 파일 권한 설정
            os.chmod(self.sessions_file, 0o600)
            
        except Exception as e:
            logger.error(f"세션 데이터 저장 실패: {e}")
    
    def create_user(self, username: str, password: str, role: Role, 
                   additional_permissions: Optional[Set[Permission]] = None) -> bool:
        """사용자 생성"""
        try:
            if username in self.users:
                logger.warning(f"사용자 이미 존재: {username}")
                return False
            
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            # 기본 권한 설정
            permissions = self.role_permissions.get(role, set()).copy()
            if additional_permissions:
                permissions.update(additional_permissions)
            
            user = User(
                username=username,
                password_hash=password_hash,
                salt=salt,
                role=role,
                permissions=permissions,
                created_at=datetime.now(timezone.utc)
            )
            
            self.users[username] = user
            self._save_users()
            
            logger.info(f"사용자 생성됨: {username} ({role.value})")
            return True
            
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = "", user_agent: str = "") -> Optional[str]:
        """사용자 인증"""
        try:
            if username not in self.users:
                self._trigger_event("suspicious_activity", {
                    "event": "invalid_username",
                    "username": username,
                    "ip_address": ip_address
                })
                return None
            
            user = self.users[username]
            
            # 계정 잠금 확인
            if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
                logger.warning(f"계정 잠금됨: {username}")
                return None
            
            # 비활성 계정 확인
            if not user.is_active:
                logger.warning(f"비활성 계정: {username}")
                return None
            
            # 비밀번호 검증
            password_hash = self._hash_password(password, user.salt)
            if password_hash != user.password_hash:
                user.failed_attempts += 1
                
                # 계정 잠금
                if user.failed_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now(timezone.utc) + self.lockout_duration
                    self._trigger_event("account_locked", {
                        "username": username,
                        "ip_address": ip_address
                    })
                
                self._save_users()
                return None
            
            # 로그인 성공
            user.failed_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now(timezone.utc)
            
            # 세션 생성
            session_id = self._create_session(username, ip_address, user_agent)
            
            self._save_users()
            self._trigger_event("login", {
                "username": username,
                "ip_address": ip_address,
                "session_id": session_id
            })
            
            return session_id
            
        except Exception as e:
            logger.error(f"사용자 인증 실패: {e}")
            return None
    
    def _create_session(self, username: str, ip_address: str, user_agent: str) -> str:
        """세션 생성"""
        try:
            # 기존 세션 정리
            self._cleanup_user_sessions(username)
            
            # 새 세션 생성
            session_id = secrets.token_urlsafe(32)
            session = Session(
                session_id=session_id,
                username=username,
                created_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.sessions[session_id] = session
            self._save_sessions()
            
            return session_id
            
        except Exception as e:
            logger.error(f"세션 생성 실패: {e}")
            return ""
    
    def _cleanup_user_sessions(self, username: str):
        """사용자 세션 정리"""
        try:
            user_sessions = [sid for sid, session in self.sessions.items() 
                           if session.username == username]
            
            # 최대 세션 수 초과시 오래된 세션 삭제
            if len(user_sessions) >= self.max_sessions_per_user:
                user_sessions.sort(key=lambda sid: self.sessions[sid].created_at)
                for sid in user_sessions[:-self.max_sessions_per_user + 1]:
                    del self.sessions[sid]
                    
        except Exception as e:
            logger.error(f"사용자 세션 정리 실패: {e}")
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """세션 검증"""
        try:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # 세션 활성 상태 확인
            if not session.is_active:
                return None
            
            # 세션 타임아웃 확인
            if datetime.now(timezone.utc) - session.last_activity > self.session_timeout:
                self._invalidate_session(session_id)
                return None
            
            # 사용자 존재 확인
            if session.username not in self.users:
                self._invalidate_session(session_id)
                return None
            
            user = self.users[session.username]
            if not user.is_active:
                self._invalidate_session(session_id)
                return None
            
            # 세션 활동 시간 업데이트
            session.last_activity = datetime.now(timezone.utc)
            self._save_sessions()
            
            return user
            
        except Exception as e:
            logger.error(f"세션 검증 실패: {e}")
            return None
    
    def _invalidate_session(self, session_id: str):
        """세션 무효화"""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self._save_sessions()
        except Exception as e:
            logger.error(f"세션 무효화 실패: {e}")
    
    def logout(self, session_id: str) -> bool:
        """로그아웃"""
        try:
            if session_id in self.sessions:
                username = self.sessions[session_id].username
                del self.sessions[session_id]
                self._save_sessions()
                
                self._trigger_event("logout", {
                    "username": username,
                    "session_id": session_id
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"로그아웃 실패: {e}")
            return False
    
    def check_permission(self, session_id: str, permission: Permission) -> bool:
        """권한 확인"""
        try:
            user = self.validate_session(session_id)
            if not user:
                return False
            
            return permission in user.permissions
            
        except Exception as e:
            logger.error(f"권한 확인 실패: {e}")
            return False
    
    def require_permission(self, permission: Permission):
        """권한 데코레이터"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 세션 ID 추출 (첫 번째 인자로 가정)
                session_id = args[0] if args else None
                
                if not self.check_permission(session_id, permission):
                    self._trigger_event("permission_denied", {
                        "session_id": session_id,
                        "permission": permission.value,
                        "function": func.__name__
                    })
                    raise PermissionError(f"권한 없음: {permission.value}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """이벤트 콜백 추가"""
        try:
            if event_type in self.event_callbacks:
                self.event_callbacks[event_type].append(callback)
        except Exception as e:
            logger.error(f"이벤트 콜백 추가 실패: {e}")
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """이벤트 트리거"""
        try:
            if event_type in self.event_callbacks:
                for callback in self.event_callbacks[event_type]:
                    try:
                        callback(event_type, data)
                    except Exception as e:
                        logger.error(f"이벤트 콜백 실행 실패: {e}")
        except Exception as e:
            logger.error(f"이벤트 트리거 실패: {e}")
    
    def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """사용자 정보 조회"""
        try:
            user = self.validate_session(session_id)
            if not user:
                return None
            
            return {
                "username": user.username,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            }
            
        except Exception as e:
            logger.error(f"사용자 정보 조회 실패: {e}")
            return None
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """활성 세션 목록"""
        try:
            active_sessions = []
            current_time = datetime.now(timezone.utc)
            
            for session in self.sessions.values():
                if session.is_active and current_time - session.last_activity <= self.session_timeout:
                    active_sessions.append({
                        "session_id": session.session_id,
                        "username": session.username,
                        "created_at": session.created_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "ip_address": session.ip_address,
                        "user_agent": session.user_agent
                    })
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"활성 세션 목록 조회 실패: {e}")
            return []
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        try:
            current_time = datetime.now(timezone.utc)
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if current_time - session.last_activity > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            if expired_sessions:
                self._save_sessions()
                logger.info(f"만료된 세션 {len(expired_sessions)}개 정리됨")
                
        except Exception as e:
            logger.error(f"만료된 세션 정리 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 접근 제어 및 권한 관리 테스트")
    
    # 접근 제어 관리자 초기화
    acm = AccessControlManager()
    
    # 관리자 사용자 생성
    print("1. 관리자 사용자 생성")
    success = acm.create_user("admin", "admin123", Role.ADMIN)
    print(f"관리자 생성: {'성공' if success else '실패'}")
    
    # 트레이더 사용자 생성
    print("\n2. 트레이더 사용자 생성")
    success = acm.create_user("trader", "trader123", Role.TRADER)
    print(f"트레이더 생성: {'성공' if success else '실패'}")
    
    # 사용자 인증
    print("\n3. 사용자 인증")
    session_id = acm.authenticate_user("admin", "admin123", "127.0.0.1", "test_agent")
    print(f"관리자 인증: {'성공' if session_id else '실패'}")
    
    # 권한 확인
    if session_id:
        print("\n4. 권한 확인")
        can_manage_users = acm.check_permission(session_id, Permission.MANAGE_USERS)
        can_execute_trading = acm.check_permission(session_id, Permission.EXECUTE_TRADING)
        print(f"사용자 관리 권한: {'있음' if can_manage_users else '없음'}")
        print(f"거래 실행 권한: {'있음' if can_execute_trading else '없음'}")
        
        # 사용자 정보 조회
        print("\n5. 사용자 정보")
        user_info = acm.get_user_info(session_id)
        print(f"사용자 정보: {user_info}")
        
        # 활성 세션 목록
        print("\n6. 활성 세션")
        sessions = acm.list_active_sessions()
        print(f"활성 세션 수: {len(sessions)}")
        
        # 로그아웃
        print("\n7. 로그아웃")
        logout_success = acm.logout(session_id)
        print(f"로그아웃: {'성공' if logout_success else '실패'}")
