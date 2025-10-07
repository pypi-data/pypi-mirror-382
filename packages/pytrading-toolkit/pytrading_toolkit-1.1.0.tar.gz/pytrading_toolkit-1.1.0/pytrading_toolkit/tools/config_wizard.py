"""
공통 설정 마법사 - 거래소 독립적인 공통 설정들
"""

import os
import yaml
import getpass
from datetime import datetime
from typing import Dict, Any

class ConfigWizard:
    """공통 설정 마법사 클래스"""
    
    def __init__(self):
        self.config = {}
    
    def get_api_keys(self, exchange: str) -> Dict[str, str]:
        """API 키 입력 수집"""
        print(f"\n🔑 {exchange.upper()} API 키 설정")
        print("=" * 40)
        
        api_keys = {}
        
        if exchange == "upbit":
            api_keys['access_key'] = getpass.getpass("Access Key: ").strip()
            api_keys['secret_key'] = getpass.getpass("Secret Key: ").strip()
        
        elif exchange == "bybit":
            api_keys['api_key'] = getpass.getpass("API Key: ").strip()
            api_keys['api_secret'] = getpass.getpass("API Secret: ").strip()
        
        # 기본값 검증
        for key, value in api_keys.items():
            if not value or value.startswith('your-'):
                print(f"⚠️ {key}가 설정되지 않았거나 기본값입니다")
                return {}
        
        return api_keys
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """텔레그램 설정 수집"""
        print("\n📱 텔레그램 알림 설정")
        print("=" * 40)
        
        enabled = input("텔레그램 알림 사용? (y/n) [y]: ").strip().lower()
        if enabled == 'n':
            return {'enabled': False}
        
        config = {
            'enabled': True,
            'bot_token': getpass.getpass("Bot Token: ").strip(),
            'chat_id': input("Chat ID: ").strip(),
            'notifications': {
                'system_start': True,
                'trade_signals': True,
                'order_execution': True,
                'position_updates': True,
                'errors': True
            }
        }
        
        # 기본값 검증
        if not config['bot_token'] or config['bot_token'].startswith('your-'):
            print("⚠️ Bot Token이 설정되지 않았습니다")
            return {'enabled': False}
        
        if not config['chat_id'] or config['chat_id'].startswith('your-'):
            print("⚠️ Chat ID가 설정되지 않았습니다")
            return {'enabled': False}
        
        return config
    
    def get_system_config(self, system_name: str) -> Dict[str, Any]:
        """시스템 공통 설정"""
        print(f"\n⚙️ {system_name} 시스템 설정")
        print("=" * 40)
        
        environment = input("환경 (development/production) [development]: ").strip()
        if not environment:
            environment = 'development'
        
        return {
            'version': '1.0.0',
            'build_date': datetime.now().strftime('%Y-%m-%d'),
            'release_notes': f'{system_name} 거래 시스템',
            'environment': environment
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """보안 설정"""
        print("\n🔒 보안 설정")
        print("=" * 40)
        
        hide_details = input("거래 상세 정보 숨김? (y/n) [y]: ").strip().lower()
        exit_on_error = input("API 에러 시 프로그램 종료? (y/n) [y]: ").strip().lower()
        
        return {
            'hide_balance_details': hide_details != 'n',
            'exit_on_api_error': exit_on_error != 'n'
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정"""
        print("\n📝 로깅 설정")
        print("=" * 40)
        
        level = input("로그 레벨 (DEBUG/INFO/WARNING/ERROR) [INFO]: ").strip().upper()
        if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            level = 'INFO'
        
        return {
            'level': level,
            'console_output': True,
            'file_output': True,
            'max_file_size': '100MB',
            'backup_count': 30
        }
    
    def save_config(self, file_path: str, config: Dict[str, Any]):
        """설정 파일 저장"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            
            print(f"✅ 설정 파일 저장됨: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False
    
    def create_backup(self, file_path: str) -> bool:
        """기존 파일 백업"""
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"💾 기존 파일 백업: {backup_path}")
                return True
            except Exception as e:
                print(f"⚠️ 백업 실패: {e}")
                return False
        return True

def create_common_config_sections(exchange: str) -> Dict[str, Any]:
    """공통 설정 섹션들 생성"""
    wizard = ConfigWizard()
    
    config = {}
    config['system'] = wizard.get_system_config(exchange)
    config['security'] = wizard.get_security_config()
    config['logging'] = wizard.get_logging_config()
    config['telegram'] = wizard.get_telegram_config()
    
    return config
