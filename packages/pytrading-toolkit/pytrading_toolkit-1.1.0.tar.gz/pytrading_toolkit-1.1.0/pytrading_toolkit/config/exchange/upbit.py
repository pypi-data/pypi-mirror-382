"""
업비트 전용 설정 로더
공통 BaseConfigLoader를 상속받아 업비트 특화 기능 구현
"""

import os
import yaml
import logging
from typing import Dict, Any
from ..base import BaseConfigLoader
from ..master_config_loader import MasterConfigLoader

logger = logging.getLogger(__name__)

class UpbitConfigLoader(BaseConfigLoader):
    """업비트 전용 설정 로더"""
    
    def __init__(self, config_file: str = "env.yaml"):
        super().__init__(config_file)
        self._algorithm_config = None
        self._master_loader = MasterConfigLoader(exchange="upbit")
    
    def load_user_config(self) -> Dict[str, Any]:
        """사용자 설정 로드 (새로운 계층적 구조 지원)"""
        try:
            # 마스터 설정 로더 사용
            return self._master_loader.get_user_config()
        except Exception as e:
            logger.error(f"사용자 설정 로드 실패: {e}")
            return {}
    
    def load_master_config(self) -> Dict[str, Any]:
        """마스터 설정 로드 (새로운 계층적 구조)"""
        try:
            return self._master_loader.load_config()
        except Exception as e:
            logger.error(f"마스터 설정 로드 실패: {e}")
            return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """업비트 설정 검증"""
        try:
            # test_mode 설정 확인
            test_mode = config.get('test_mode', True)
            
            # 사용자 설정에서 API 키 로드
            user_config = self.load_user_config()
            exchange_keys = user_config.get('exchange_keys', {})
            upbit_keys = exchange_keys.get('upbit', {})
            
            # API 키가 있으면 검증
            if upbit_keys:
                access_key = upbit_keys.get('access_key', '')
                secret_key = upbit_keys.get('secret_key', '')
                
                if not access_key or not secret_key:
                    if test_mode:
                        logger.warning("업비트 API 키가 설정되지 않았습니다. 테스트 모드로 실행됩니다.")
                    else:
                        logger.error("업비트 API 키가 설정되지 않았는데 test_mode가 false입니다. API 키를 설정하거나 test_mode를 true로 변경하세요.")
                        return False
                elif access_key.startswith('your-') or secret_key.startswith('your-'):
                    if test_mode:
                        logger.warning("업비트 API 키가 기본값으로 설정되어 있습니다. 테스트 모드로 실행됩니다.")
                    else:
                        logger.error("업비트 API 키가 기본값으로 설정되어 있는데 test_mode가 false입니다. 실제 API 키를 설정하거나 test_mode를 true로 변경하세요.")
                        return False
                else:
                    logger.info("업비트 API 키 검증 완료")
            else:
                if test_mode:
                    logger.warning("업비트 API 키 설정이 없습니다. 테스트 모드로 실행됩니다.")
                else:
                    logger.error("업비트 API 키 설정이 없는데 test_mode가 false입니다. API 키를 설정하거나 test_mode를 true로 변경하세요.")
                    return False
            
            # 거래 설정 검증
            trading = config.get('spot_trading', {}) or config.get('trading', {})
            if trading:
                market = trading.get('market', '')
                if market and not market.startswith('KRW-'):
                    logger.warning(f"업비트는 KRW 마켓만 지원합니다: {market}")
            
            return True
            
        except Exception as e:
            logger.error(f"설정 검증 실패: {e}")
            return False
    
    def get_config_file_path(self) -> str:
        """업비트 설정 파일 경로"""
        # 상대 경로 사용
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # pytrading-toolkit 패키지 루트로 이동
        package_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        # trader/app/upbit 디렉토리로 이동
        upbit_dir = os.path.join(package_root, '..', '..', 'trader', 'app', 'upbit')
        
        config_path = os.path.join(upbit_dir, self.config_file)
        # 절대 경로로 변환
        config_path = os.path.abspath(config_path)
        
        if os.path.exists(config_path):
            return config_path
        
        # example 파일 확인
        example_path = os.path.join(upbit_dir, f"{self.config_file}.example")
        if os.path.exists(example_path):
            error_msg = f"""
❌ 업비트 설정 파일이 없습니다!

📁 예상 위치: {config_path}
📄 예시 파일: {example_path}

🔧 설정 파일을 생성하려면 다음 중 하나를 실행하세요:

1. 예시 파일 복사:
   cp {example_path} {config_path}

2. 자동 생성 (기본 설정):
   cd {upbit_dir}
   python3 src/set_env.py init

3. 설정 마법사 (대화형):
   cd {upbit_dir}
   python3 src/setup_config.py

⚠️  설정 파일을 생성한 후 API 키와 기타 설정을 반드시 수정하세요!
"""
            raise FileNotFoundError(error_msg)
        else:
            raise FileNotFoundError(f"업비트 설정 파일을 찾을 수 없습니다. {upbit_dir} 디렉토리를 확인하세요.")
    
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
