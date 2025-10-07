#!/usr/bin/env python3
"""
공통 사용자 설정 관리 도구
텔레그램, API 키 등 개인 설정을 한 곳에서 관리
"""

import os
import yaml
import getpass
from datetime import datetime
from typing import Dict, Any

class UserConfigManager:
    """사용자 공통 설정 관리자"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.user_config_file = os.path.join(self.config_dir, 'user_config.yaml')
        os.makedirs(self.config_dir, exist_ok=True)
    
    def setup_telegram(self) -> Dict[str, Any]:
        """텔레그램 설정"""
        print("\n📱 텔레그램 알림 설정 (모든 거래소 공통)")
        print("=" * 50)
        
        enabled = input("텔레그램 알림 사용? (y/n) [y]: ").strip().lower()
        if enabled == 'n':
            return {'enabled': False}
        
        print("\n🤖 텔레그램 봇 설정:")
        print("1. @BotFather에게 /newbot 명령어로 봇 생성")
        print("2. 봇 토큰을 복사해두기")
        print("3. 봇과 대화 시작 후 채팅방 ID 확인")
        
        bot_token = getpass.getpass("\n봇 토큰: ").strip()
        chat_id = input("채팅방 ID: ").strip()
        account_name = input("계정 이름 [자동매매봇]: ").strip() or "자동매매봇"
        
        if not bot_token or bot_token.startswith('your-'):
            print("⚠️ 봇 토큰이 설정되지 않았습니다")
            return {'enabled': False}
        
        # 알림 세부 설정
        print("\n🔔 알림 상세 설정:")
        notifications = {}
        notifications['system_start'] = input("시스템 시작 알림? (y/n) [y]: ").strip().lower() != 'n'
        notifications['trade_signals'] = input("거래 신호 알림? (y/n) [y]: ").strip().lower() != 'n'
        notifications['order_execution'] = input("주문 체결 알림? (y/n) [y]: ").strip().lower() != 'n'
        notifications['position_updates'] = input("포지션 업데이트 알림? (y/n) [n]: ").strip().lower() == 'y'
        notifications['errors'] = input("에러 알림? (y/n) [y]: ").strip().lower() != 'n'
        notifications['daily_summary'] = input("일일 요약 알림? (y/n) [y]: ").strip().lower() != 'n'
        
        return {
            'enabled': True,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'account_name': account_name,
            'notifications': notifications
        }
    
    def setup_exchange_keys(self) -> Dict[str, Dict[str, str]]:
        """거래소 API 키 설정"""
        print("\n🔑 거래소 API 키 설정")
        print("=" * 50)
        
        exchanges = {}
        
        # 업비트 API 키
        print("\n💙 업비트 API 키:")
        print("1. 업비트 홈페이지 > 마이페이지 > API 관리")
        print("2. '자산 조회', '주문 조회', '주문하기' 권한 선택")
        print("3. IP 주소 등록 (선택사항)")
        
        setup_upbit = input("업비트 API 키 설정? (y/n) [y]: ").strip().lower() != 'n'
        if setup_upbit:
            access_key = getpass.getpass("Access Key: ").strip()
            secret_key = getpass.getpass("Secret Key: ").strip()
            
            if access_key and secret_key and not access_key.startswith('your-'):
                exchanges['upbit'] = {
                    'access_key': access_key,
                    'secret_key': secret_key
                }
                print("✅ 업비트 API 키 설정 완료")
            else:
                print("⚠️ 업비트 API 키 설정을 건너뛰었습니다")
        
        # 바이비트 API 키
        print("\n🟡 바이비트 API 키:")
        print("1. 바이비트 홈페이지 > API Management")
        print("2. 'Derivatives' 권한 선택 (선물 거래용)")
        print("3. IP 제한 설정 권장")
        
        setup_bybit = input("바이비트 API 키 설정? (y/n) [y]: ").strip().lower() != 'n'
        if setup_bybit:
            api_key = getpass.getpass("API Key: ").strip()
            api_secret = getpass.getpass("API Secret: ").strip()
            
            if api_key and api_secret and not api_key.startswith('your-'):
                exchanges['bybit'] = {
                    'api_key': api_key,
                    'api_secret': api_secret
                }
                print("✅ 바이비트 API 키 설정 완료")
            else:
                print("⚠️ 바이비트 API 키 설정을 건너뛰었습니다")
        
        return exchanges
    
    def setup_general_settings(self) -> Dict[str, Any]:
        """일반 설정"""
        print("\n⚙️ 일반 설정")
        print("=" * 50)
        
        user_name = input("사용자 이름 [트레이더]: ").strip() or "트레이더"
        
        environment = input("환경 (development/production) [development]: ").strip()
        if environment not in ['development', 'production']:
            environment = 'development'
        
        # 보안 설정
        print("\n🔒 보안 설정:")
        hide_balance = input("잔고 정보 숨김? (y/n) [y]: ").strip().lower() != 'n'
        exit_on_error = input("API 에러 시 프로그램 종료? (y/n) [y]: ").strip().lower() != 'n'
        
        # 로깅 설정
        print("\n📝 로깅 설정:")
        log_level = input("로그 레벨 (DEBUG/INFO/WARNING/ERROR) [INFO]: ").strip().upper()
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            log_level = 'INFO'
        
        return {
            'user_name': user_name,
            'environment': environment,
            'security': {
                'hide_balance_details': hide_balance,
                'exit_on_api_error': exit_on_error
            },
            'logging': {
                'level': log_level,
                'console_output': True,
                'file_output': True,
                'max_file_size': '100MB',
                'backup_count': 30
            },
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0'
        }
    
    def load_user_config(self) -> Dict[str, Any]:
        """기존 사용자 설정 로드"""
        if os.path.exists(self.user_config_file):
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ 기존 설정 로드 실패: {e}")
        return {}
    
    def save_user_config(self, config: Dict[str, Any]) -> bool:
        """사용자 설정 저장"""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            return True
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False
    
    def create_backup(self) -> bool:
        """기존 설정 백업"""
        if os.path.exists(self.user_config_file):
            backup_file = f"{self.user_config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(self.user_config_file, backup_file)
                print(f"💾 기존 설정 백업: {backup_file}")
                return True
            except Exception as e:
                print(f"⚠️ 백업 실패: {e}")
                return False
        return True
    
    def setup_complete_user_config(self) -> bool:
        """완전한 사용자 설정 수행"""
        print("="*60)
        print("👤 공통 사용자 설정 (모든 거래소에서 사용)")
        print("="*60)
        
        # 기존 설정 확인
        existing_config = self.load_user_config()
        if existing_config:
            print("🔍 기존 설정이 발견되었습니다.")
            update = input("기존 설정을 업데이트하시겠습니까? (y/n) [n]: ").strip().lower() == 'y'
            if not update:
                print("❌ 설정을 건너뛰었습니다.")
                return False
            self.create_backup()
        
        # 새 설정 수집
        config = {}
        
        # 일반 설정
        config.update(self.setup_general_settings())
        
        # 텔레그램 설정
        config['telegram'] = self.setup_telegram()
        
        # 거래소 API 키
        config['exchange_keys'] = self.setup_exchange_keys()
        
        # 설정 저장
        if self.save_user_config(config):
            print("\n" + "="*60)
            print("✅ 공통 사용자 설정 완료!")
            print("="*60)
            print("\n📋 다음 단계:")
            print("1. 각 거래소별 알고리즘 설정:")
            print("   - cd upbit && python setup_algorithm.py")
            print("   - cd bybit && python setup_algorithm.py")
            print("2. 거래 시스템 시작:")
            print("   - cd upbit && ./start_trader.sh")
            print("   - cd bybit && python run_trader.py")
            print("\n🔒 보안 주의사항:")
            print("- config/user_config.yaml 파일을 git에 커밋하지 마세요")
            print("- API 키는 절대 공유하지 마세요")
            return True
        
        return False

def main():
    """메인 함수"""
    manager = UserConfigManager()
    manager.setup_complete_user_config()

if __name__ == "__main__":
    main()
