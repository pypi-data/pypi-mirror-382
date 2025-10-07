#!/usr/bin/env python3
"""
암호화 및 보안 저장 모듈
API 키 및 민감한 데이터 보안 관리
"""

import os
import base64
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json

logger = logging.getLogger(__name__)

class SecureStorage:
    """보안 저장소 클래스"""
    
    def __init__(self, master_key: Optional[str] = None, key_file: str = ".secure_key"):
        self.key_file = key_file
        self.master_key = master_key or self._load_or_generate_master_key()
        self.fernet = self._create_fernet()
        
    def _load_or_generate_master_key(self) -> str:
        """마스터 키 로드 또는 생성"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # 새 마스터 키 생성
                master_key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(master_key)
                # 파일 권한 설정 (소유자만 읽기/쓰기)
                os.chmod(self.key_file, 0o600)
                return master_key
                
        except Exception as e:
            logger.error(f"마스터 키 처리 실패: {e}")
            # 임시 키 생성
            return Fernet.generate_key()
    
    def _create_fernet(self) -> Fernet:
        """Fernet 암호화 객체 생성"""
        try:
            return Fernet(self.master_key)
        except Exception as e:
            logger.error(f"Fernet 객체 생성 실패: {e}")
            return Fernet(Fernet.generate_key())
    
    def encrypt_data(self, data: Union[str, Dict[str, Any]]) -> str:
        """데이터 암호화"""
        try:
            if isinstance(data, dict):
                data_str = json.dumps(data, ensure_ascii=False)
            else:
                data_str = str(data)
            
            # 데이터를 바이트로 변환
            data_bytes = data_str.encode('utf-8')
            
            # 암호화
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # Base64 인코딩
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"데이터 암호화 실패: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict[str, Any]]:
        """데이터 복호화"""
        try:
            # Base64 디코딩
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 복호화
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # 문자열로 변환
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # JSON 파싱 시도
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"데이터 복호화 실패: {e}")
            raise
    
    def store_secure_data(self, key: str, data: Union[str, Dict[str, Any]], 
                         file_path: str = ".secure_data") -> bool:
        """보안 데이터 저장"""
        try:
            # 기존 데이터 로드
            secure_data = self._load_secure_data(file_path)
            
            # 새 데이터 암호화 및 저장
            secure_data[key] = self.encrypt_data(data)
            
            # 파일에 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(secure_data, f, ensure_ascii=False, indent=2)
            
            # 파일 권한 설정
            os.chmod(file_path, 0o600)
            
            logger.info(f"보안 데이터 저장됨: {key}")
            return True
            
        except Exception as e:
            logger.error(f"보안 데이터 저장 실패: {e}")
            return False
    
    def load_secure_data(self, key: str, file_path: str = ".secure_data") -> Optional[Union[str, Dict[str, Any]]]:
        """보안 데이터 로드"""
        try:
            secure_data = self._load_secure_data(file_path)
            
            if key not in secure_data:
                return None
            
            return self.decrypt_data(secure_data[key])
            
        except Exception as e:
            logger.error(f"보안 데이터 로드 실패: {e}")
            return None
    
    def _load_secure_data(self, file_path: str) -> Dict[str, str]:
        """보안 데이터 파일 로드"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"보안 데이터 파일 로드 실패: {e}")
            return {}
    
    def delete_secure_data(self, key: str, file_path: str = ".secure_data") -> bool:
        """보안 데이터 삭제"""
        try:
            secure_data = self._load_secure_data(file_path)
            
            if key in secure_data:
                del secure_data[key]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(secure_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"보안 데이터 삭제됨: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"보안 데이터 삭제 실패: {e}")
            return False
    
    def list_secure_keys(self, file_path: str = ".secure_data") -> List[str]:
        """보안 데이터 키 목록"""
        try:
            secure_data = self._load_secure_data(file_path)
            return list(secure_data.keys())
        except Exception as e:
            logger.error(f"보안 데이터 키 목록 조회 실패: {e}")
            return []

class APIKeyManager:
    """API 키 관리자"""
    
    def __init__(self, secure_storage: SecureStorage):
        self.secure_storage = secure_storage
        self.api_keys = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """API 키 로드"""
        try:
            # 암호화된 API 키 로드
            encrypted_keys = self.secure_storage.load_secure_data("api_keys")
            if encrypted_keys:
                self.api_keys = encrypted_keys
                logger.info("API 키 로드됨")
        except Exception as e:
            logger.error(f"API 키 로드 실패: {e}")
    
    def store_api_key(self, exchange: str, api_key: str, api_secret: str, 
                     additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """API 키 저장"""
        try:
            key_data = {
                "api_key": api_key,
                "api_secret": api_secret,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "additional_data": additional_data or {}
            }
            
            self.api_keys[exchange] = key_data
            
            # 보안 저장소에 저장
            success = self.secure_storage.store_secure_data("api_keys", self.api_keys)
            
            if success:
                logger.info(f"API 키 저장됨: {exchange}")
            
            return success
            
        except Exception as e:
            logger.error(f"API 키 저장 실패: {e}")
            return False
    
    def get_api_key(self, exchange: str) -> Optional[Dict[str, Any]]:
        """API 키 조회"""
        try:
            return self.api_keys.get(exchange)
        except Exception as e:
            logger.error(f"API 키 조회 실패: {e}")
            return None
    
    def get_api_key_value(self, exchange: str) -> Optional[str]:
        """API 키 값만 조회"""
        try:
            key_data = self.api_keys.get(exchange)
            return key_data.get("api_key") if key_data else None
        except Exception as e:
            logger.error(f"API 키 값 조회 실패: {e}")
            return None
    
    def get_api_secret(self, exchange: str) -> Optional[str]:
        """API 시크릿 조회"""
        try:
            key_data = self.api_keys.get(exchange)
            return key_data.get("api_secret") if key_data else None
        except Exception as e:
            logger.error(f"API 시크릿 조회 실패: {e}")
            return None
    
    def delete_api_key(self, exchange: str) -> bool:
        """API 키 삭제"""
        try:
            if exchange in self.api_keys:
                del self.api_keys[exchange]
                
                # 보안 저장소에 저장
                success = self.secure_storage.store_secure_data("api_keys", self.api_keys)
                
                if success:
                    logger.info(f"API 키 삭제됨: {exchange}")
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"API 키 삭제 실패: {e}")
            return False
    
    def list_exchanges(self) -> List[str]:
        """거래소 목록"""
        try:
            return list(self.api_keys.keys())
        except Exception as e:
            logger.error(f"거래소 목록 조회 실패: {e}")
            return []
    
    def mask_api_key(self, api_key: str) -> str:
        """API 키 마스킹"""
        try:
            if len(api_key) <= 8:
                return "*" * len(api_key)
            
            return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        except Exception as e:
            logger.error(f"API 키 마스킹 실패: {e}")
            return "***"
    
    def validate_api_key(self, exchange: str) -> bool:
        """API 키 유효성 검증"""
        try:
            key_data = self.api_keys.get(exchange)
            if not key_data:
                return False
            
            # 필수 필드 확인
            required_fields = ["api_key", "api_secret"]
            for field in required_fields:
                if not key_data.get(field):
                    return False
            
            # API 키 형식 검증 (기본적인 길이 체크)
            api_key = key_data.get("api_key", "")
            if len(api_key) < 10:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"API 키 유효성 검증 실패: {e}")
            return False

class PasswordManager:
    """비밀번호 관리자"""
    
    def __init__(self, secure_storage: SecureStorage):
        self.secure_storage = secure_storage
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """비밀번호 해시"""
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            # PBKDF2를 사용한 해시 생성
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = base64.b64encode(kdf.derive(password.encode()))
            salt_b64 = base64.b64encode(salt).decode()
            key_b64 = key.decode()
            
            return {
                "hash": key_b64,
                "salt": salt_b64
            }
            
        except Exception as e:
            logger.error(f"비밀번호 해시 실패: {e}")
            raise
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """비밀번호 검증"""
        try:
            salt_bytes = base64.b64decode(salt.encode())
            
            # 동일한 방식으로 해시 생성
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=default_backend()
            )
            
            key = base64.b64encode(kdf.derive(password.encode()))
            return key.decode() == stored_hash
            
        except Exception as e:
            logger.error(f"비밀번호 검증 실패: {e}")
            return False
    
    def store_password(self, service: str, password: str) -> bool:
        """비밀번호 저장"""
        try:
            hash_data = self.hash_password(password)
            
            password_data = {
                "service": service,
                "hash": hash_data["hash"],
                "salt": hash_data["salt"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return self.secure_storage.store_secure_data(f"password_{service}", password_data)
            
        except Exception as e:
            logger.error(f"비밀번호 저장 실패: {e}")
            return False
    
    def verify_stored_password(self, service: str, password: str) -> bool:
        """저장된 비밀번호 검증"""
        try:
            password_data = self.secure_storage.load_secure_data(f"password_{service}")
            if not password_data:
                return False
            
            return self.verify_password(
                password,
                password_data["hash"],
                password_data["salt"]
            )
            
        except Exception as e:
            logger.error(f"저장된 비밀번호 검증 실패: {e}")
            return False

class DataMasker:
    """데이터 마스킹 클래스"""
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """API 키 마스킹"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    @staticmethod
    def mask_email(email: str) -> str:
        """이메일 마스킹"""
        if "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """전화번호 마스킹"""
        if len(phone) <= 4:
            return "*" * len(phone)
        return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """신용카드 번호 마스킹"""
        if len(card_number) <= 8:
            return "*" * len(card_number)
        return card_number[:4] + "*" * (len(card_number) - 8) + card_number[-4:]
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], 
                           sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """민감한 데이터 마스킹"""
        if sensitive_fields is None:
            sensitive_fields = [
                "api_key", "api_secret", "password", "token",
                "email", "phone", "credit_card", "ssn"
            ]
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if isinstance(value, str):
                key_lower = key.lower()
                if any(field in key_lower for field in sensitive_fields):
                    if "api_key" in key_lower or "api_secret" in key_lower:
                        masked_data[key] = DataMasker.mask_api_key(value)
                    elif "email" in key_lower:
                        masked_data[key] = DataMasker.mask_email(value)
                    elif "phone" in key_lower:
                        masked_data[key] = DataMasker.mask_phone(value)
                    elif "card" in key_lower:
                        masked_data[key] = DataMasker.mask_credit_card(value)
                    else:
                        masked_data[key] = "*" * len(value)
            elif isinstance(value, dict):
                masked_data[key] = DataMasker.mask_sensitive_data(value, sensitive_fields)
        
        return masked_data

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 암호화 및 보안 저장 테스트")
    
    # 보안 저장소 초기화
    secure_storage = SecureStorage()
    
    # API 키 관리자 테스트
    print("1. API 키 관리 테스트")
    api_manager = APIKeyManager(secure_storage)
    
    # API 키 저장
    success = api_manager.store_api_key(
        "upbit",
        "test_api_key_123456789",
        "test_secret_987654321",
        {"testnet": True}
    )
    print(f"API 키 저장: {'성공' if success else '실패'}")
    
    # API 키 조회
    api_data = api_manager.get_api_key("upbit")
    print(f"API 키 조회: {bool(api_data)}")
    
    # API 키 마스킹
    masked_key = api_manager.mask_api_key("test_api_key_123456789")
    print(f"마스킹된 API 키: {masked_key}")
    
    # 비밀번호 관리자 테스트
    print("\n2. 비밀번호 관리 테스트")
    password_manager = PasswordManager(secure_storage)
    
    # 비밀번호 저장
    success = password_manager.store_password("test_service", "test_password_123")
    print(f"비밀번호 저장: {'성공' if success else '실패'}")
    
    # 비밀번호 검증
    is_valid = password_manager.verify_stored_password("test_service", "test_password_123")
    print(f"비밀번호 검증: {'성공' if is_valid else '실패'}")
    
    # 데이터 마스킹 테스트
    print("\n3. 데이터 마스킹 테스트")
    sensitive_data = {
        "api_key": "test_api_key_123456789",
        "email": "test@example.com",
        "phone": "010-1234-5678",
        "normal_field": "normal_value"
    }
    
    masked_data = DataMasker.mask_sensitive_data(sensitive_data)
    print(f"마스킹된 데이터: {masked_data}")
