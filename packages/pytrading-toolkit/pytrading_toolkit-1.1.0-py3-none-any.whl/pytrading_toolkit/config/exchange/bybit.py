"""
바이비트 전용 설정 로더
공통 BaseConfigLoader를 상속받아 바이비트 특화 기능 구현
"""

import os
import logging
from typing import Dict, Any
from ..base import BaseConfigLoader

logger = logging.getLogger(__name__)

class BybitConfigLoader(BaseConfigLoader):
    """바이비트 전용 설정 로더"""
    
    def __init__(self, config_file: str = "env.yaml"):
        super().__init__(config_file)
        self._algorithm_config = None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """바이비트 설정 검증"""
        try:
            # API 키 검증
            exchange_keys = config.get('exchange_keys', {})
            bybit_keys = exchange_keys.get('bybit', {})
            
            if not bybit_keys:
                logger.error("바이비트 API 키 설정이 없습니다")
                return False
            
            api_key = bybit_keys.get('api_key', '')
            secret_key = bybit_keys.get('secret_key', '')
            
            if not api_key or not secret_key:
                logger.error("바이비트 API 키가 설정되지 않았습니다")
                return False
            
            # 기본값 검사
            if api_key.startswith('your-') or secret_key.startswith('your-'):
                logger.error("바이비트 API 키가 기본값으로 설정되어 있습니다")
                return False
            
            # 거래 설정 검증
            trading = config.get('futures_trading', {}) or config.get('trading', {})
            if trading:
                market = trading.get('market', '')
                if market and not market.endswith('USDT'):
                    logger.warning(f"바이비트는 USDT 마켓을 권장합니다: {market}")
            
            return True
            
        except Exception as e:
            logger.error(f"설정 검증 실패: {e}")
            return False
    
    def get_config_file_path(self) -> str:
        """바이비트 설정 파일 경로"""
        # 상대 경로 사용
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # pytrading-toolkit 패키지 루트로 이동
        package_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        # trader/app/bybit 디렉토리로 이동
        bybit_dir = os.path.join(package_root, '..', '..', 'trader', 'app', 'bybit')
        
        config_path = os.path.join(bybit_dir, self.config_file)
        # 절대 경로로 변환
        config_path = os.path.abspath(config_path)
        
        if os.path.exists(config_path):
            return config_path
        
        # example 파일 확인
        example_path = os.path.join(bybit_dir, f"{self.config_file}.example")
        if os.path.exists(example_path):
            raise FileNotFoundError(
                f"{self.config_file} 파일이 없습니다. {example_path}를 복사해서 {self.config_file}을 만들어주세요."
            )
        else:
            raise FileNotFoundError("바이비트 설정 파일을 찾을 수 없습니다.")
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        """알고리즘 설정 반환"""
        if self._algorithm_config is None:
            config = self.load_config()
            self._algorithm_config = config.get('algorithm', {})
        return self._algorithm_config
    
    def get_trading_rules(self) -> Dict[str, Any]:
        """거래 규칙 반환"""
        config = self.load_config()
        return config.get('trading_rules', {})
