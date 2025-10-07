"""
마스터 설정 로더
새로운 계층적 설정 구조를 지원하는 설정 로더
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from .base import BaseConfigLoader

logger = logging.getLogger(__name__)

class MasterConfigLoader:
    """마스터 설정 로더 - 계층적 설정 파일 구조 지원"""
    
    def __init__(self, exchange: str = None, user_id: str = "default_user"):
        self.exchange = exchange
        self.user_id = user_id
        self.config_cache = None
        self.last_modified = None
        
        # 프로젝트 루트 경로 찾기
        self.project_root = self._find_project_root()
        
    def _find_project_root(self) -> str:
        """프로젝트 루트 경로 찾기"""
        # 현재 작업 디렉토리에서 trader 찾기
        cwd = os.getcwd()
        if os.path.basename(cwd) == 'trader':
            return cwd
        
        # 현재 디렉토리에서 trader 하위 디렉토리 찾기
        trader_path = os.path.join(cwd, 'trader')
        if os.path.exists(trader_path):
            return trader_path
        
        # 상위 디렉토리에서 trader 찾기
        parent_dir = os.path.dirname(cwd)
        trader_path = os.path.join(parent_dir, 'trader')
        if os.path.exists(trader_path):
            return trader_path
        
        # pytrading-toolkit 패키지 위치에서 상대 경로로 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # pytrading-toolkit/pytrading_toolkit/config/ 에서 시작해서
        # trader/ 디렉토리를 찾음
        while current_dir != '/':
            if os.path.basename(current_dir) == 'trader':
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # 마지막 시도: 상대 경로로 탐색
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '../../../trader'),
            os.path.join(os.path.dirname(__file__), '../../../../trader'),
            os.path.join(os.path.expanduser('~'), 'work/crypto-auto-trader/trader'),
            os.path.join(os.path.expanduser('~'), 'source/crypto-auto-trader/trader'),
            os.path.join(os.path.expanduser('~'), 'crypto-auto-trader/trader')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("trader 디렉토리를 찾을 수 없습니다")
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """계층적 설정 로드"""
        if self.config_cache and not force_reload:
            return self.config_cache
        
        try:
            # 1. 기본 설정 로드 (env.yaml)
            base_config = self._load_file('env.yaml')
            
            # 2. 환경별 설정 로드 (env.{env}.yaml)
            env = base_config.get('env', 'dev')
            env_config = self._load_file(f'env.{env}.yaml', required=False)
            
            # 3. 거래소별 설정 로드 (app/{exchange}/{exchange}.yaml)
            exchange_config = {}
            if self.exchange:
                exchange_config = self._load_file(f'app/{self.exchange}/{self.exchange}.yaml', required=False)
            
            # 4. 사용자별 설정 로드 (config/users/{user_id}.yaml)
            user_config = self._load_user_config()
            
            # 5. 설정 병합 (우선순위: user > exchange > env > base)
            self.config_cache = self._merge_configs(
                base_config, env_config, exchange_config, user_config
            )
            
            env = self.config_cache.get('env', 'dev')
            logger.info(f"마스터 설정 로드 완료: {self.exchange or 'all'} (환경: {env})")
            return self.config_cache
            
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}")
            raise
    
    def _load_file(self, file_path: str, required: bool = True) -> Dict[str, Any]:
        """설정 파일 로드"""
        full_path = os.path.join(self.project_root, file_path)
        
        if not os.path.exists(full_path):
            if required:
                raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {full_path}")
            return {}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.debug(f"설정 파일 로드: {file_path}")
            return config
        except Exception as e:
            logger.error(f"설정 파일 로드 실패 {file_path}: {e}")
            if required:
                raise
            return {}
    
    def _load_user_config(self) -> Dict[str, Any]:
        """사용자별 설정 로드"""
        try:
            # 환경 확인
            base_config = self._load_file('env.yaml')
            env = base_config.get('env', 'dev')
            
            # 사용자 설정 파일 경로 (환경별)
            user_file = f'config/{env}/{self.user_id}.yaml'
            user_config = self._load_file(user_file, required=False)
            
            if not user_config:
                logger.warning(f"사용자 설정 파일을 찾을 수 없습니다: {user_file}")
                return {}
            
            logger.debug(f"사용자 설정 로드: {self.user_id} (환경: {env})")
            return user_config
            
        except Exception as e:
            logger.error(f"사용자 설정 로드 실패: {e}")
            return {}
    
    def _merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """설정 병합 (나중에 오는 설정이 우선)"""
        merged = {}
        
        for config in configs:
            if not config:
                continue
            merged = self._deep_merge(merged, config)
        
        return merged
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """딥 머지"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def get_exchange_config(self) -> Dict[str, Any]:
        """거래소별 설정 반환"""
        config = self.load_config()
        if self.exchange:
            return config.get('exchange', {})
        return {}
    
    def get_user_config(self) -> Dict[str, Any]:
        """사용자별 설정 반환"""
        return self._load_user_config()
    
    def get_trading_config(self) -> Dict[str, Any]:
        """거래 설정 반환"""
        config = self.load_config()
        return config.get('trading', {})
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """텔레그램 설정 반환"""
        config = self.load_config()
        return config.get('telegram', {})
    
    def is_test_mode(self) -> bool:
        """테스트 모드 여부"""
        config = self.load_config()
        return config.get('test_mode', False)  # 기본값을 False로 변경
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        """알고리즘 설정 반환"""
        config = self.load_config()
        return config.get('algorithm', {})
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """설정 검증"""
        try:
            # 기본 검증
            if not config:
                logger.error("설정이 비어있습니다")
                return False
            
            # 테스트 모드가 아닌 경우 API 키 검증
            if not config.get('test_mode', True):
                exchange_keys = config.get('exchange_keys', {})
                if self.exchange and self.exchange in exchange_keys:
                    keys = exchange_keys[self.exchange]
                    if not keys.get('access_key') or not keys.get('secret_key'):
                        logger.error(f"{self.exchange} API 키가 설정되지 않았습니다")
                        return False
            
            logger.info("설정 검증 완료")
            return True
            
        except Exception as e:
            logger.error(f"설정 검증 실패: {e}")
            return False
