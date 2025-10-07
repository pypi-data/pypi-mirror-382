"""
공통 설정 관리 기본 클래스
업비트와 바이비트 시스템에서 공통으로 사용
"""

import os
import yaml
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseConfigLoader(ABC):
    """설정 로더 기본 클래스"""
    
    def __init__(self, config_file: str = "env.yaml"):
        self.config_file = config_file
        self.config_cache = None
        self.last_modified = None
    
    def get_config_file_path(self) -> str:
        """설정 파일 경로 반환"""
        if os.path.isabs(self.config_file):
            return self.config_file
        
        # 현재 파일 기준으로 프로젝트 루트 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        config_path = os.path.join(project_root, self.config_file)
        example_path = os.path.join(project_root, f"{self.config_file}.example")
        
        # 파일 존재 확인
        if os.path.exists(config_path):
            return config_path
        elif os.path.exists(example_path):
            raise FileNotFoundError(
                f"{self.config_file} 파일이 없습니다. "
                f"{example_path}를 복사해서 {self.config_file}을 만들어주세요."
            )
        else:
            raise FileNotFoundError("설정 파일을 찾을 수 없습니다.")
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """설정 파일 로드 (캐싱 지원)"""
        config_path = self.get_config_file_path()
        
        # 파일 수정 시간 확인
        try:
            current_modified = os.path.getmtime(config_path)
        except OSError:
            current_modified = 0
        
        # 캐시된 설정이 있고 파일이 변경되지 않았으면 캐시 사용
        if (not force_reload and 
            self.config_cache is not None and 
            self.last_modified == current_modified):
            return self.config_cache
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_cache = yaml.safe_load(f)
            
            self.last_modified = current_modified
            logger.info(f"설정 파일 로드 성공: {config_path}")
            return self.config_cache
            
        except FileNotFoundError as e:
            logger.error(f"설정 파일을 찾을 수 없습니다: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            raise
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """설정 검증 (각 시스템에서 구현)"""
        pass
    
    def get_nested_value(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """중첩된 설정값 조회
        
        Args:
            config: 설정 딕셔너리
            path: 점으로 구분된 경로 (예: "trading.amounts.min_trade_amount")
            default: 기본값
            
        Returns:
            설정값
        """
        keys = path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_system_info(self) -> Dict[str, str]:
        """시스템 정보 반환"""
        config = self.load_config()
        system = config.get('system', {})
        
        return {
            'version': system.get('version', '1.0.0'),
            'build_date': system.get('build_date', '2025-01-27'),
            'release_notes': system.get('release_notes', '거래 시스템'),
            'environment': system.get('environment', 'development')
        }
    
    def should_hide_details(self) -> bool:
        """세부 정보 숨김 여부"""
        config = self.load_config()
        return self.get_nested_value(config, 'security.hide_balance_details', True)
    
    def should_exit_on_api_error(self) -> bool:
        """API 에러 시 프로그램 종료 여부"""
        config = self.load_config()
        return self.get_nested_value(config, 'security.exit_on_api_error', True)
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """텔레그램 설정 반환"""
        config = self.load_config()
        telegram = config.get('telegram', {})
        
        return {
            'enabled': telegram.get('enabled', False),
            'bot_token': telegram.get('bot_token', ''),
            'chat_id': telegram.get('chat_id', ''),
            'notifications': telegram.get('notifications', {})
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 반환"""
        config = self.load_config()
        logging_config = config.get('logging', {})
        
        return {
            'level': logging_config.get('level', 'INFO'),
            'console_output': logging_config.get('console_output', True),
            'file_output': logging_config.get('file_output', True),
            'max_file_size': logging_config.get('max_file_size', '100MB'),
            'backup_count': logging_config.get('backup_count', 30)
        }
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """설정 업데이트
        
        Args:
            updates: 업데이트할 설정 딕셔너리
            save: 파일에 저장 여부
            
        Returns:
            성공 여부
        """
        try:
            config = self.load_config()
            
            # 중첩된 딕셔너리 업데이트
            def deep_update(target: dict, source: dict):
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        deep_update(target[key], value)
                    else:
                        target[key] = value
            
            deep_update(config, updates)
            
            if save:
                config_path = self.get_config_file_path()
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
                
                # 캐시 업데이트
                self.config_cache = config
                self.last_modified = os.path.getmtime(config_path)
                
                logger.info("설정 파일 업데이트 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"설정 업데이트 실패: {e}")
            return False
    
    def create_backup(self) -> bool:
        """설정 파일 백업"""
        try:
            config_path = self.get_config_file_path()
            backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            import shutil
            shutil.copy2(config_path, backup_path)
            
            logger.info(f"설정 파일 백업 생성: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 백업 실패: {e}")
            return False
    
    def validate_api_keys(self, config: Dict[str, Any]) -> bool:
        """API 키 유효성 검사 (기본 구현)"""
        try:
            # 각 거래소별로 API 키 확인
            exchange_keys = config.get('exchange_keys', {})
            
            for exchange, keys in exchange_keys.items():
                api_key = keys.get('api_key', '')
                api_secret = keys.get('api_secret', '')
                
                # 기본값인지 확인
                if api_key.startswith('your-') or api_secret.startswith('your-'):
                    logger.warning(f"{exchange} API 키가 기본값으로 설정되어 있습니다")
                    return False
                
                # 최소 길이 확인
                if len(api_key) < 10 or len(api_secret) < 10:
                    logger.warning(f"{exchange} API 키가 너무 짧습니다")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"API 키 검증 실패: {e}")
            return False
    
    def reload_config(self) -> Dict[str, Any]:
        """설정 강제 재로드"""
        return self.load_config(force_reload=True)
