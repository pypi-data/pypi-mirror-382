#!/usr/bin/env python3
"""
통합 설정 관리 도구
모든 거래소가 하나의 마스터 설정을 공유하되, 각각의 특화 설정 추가
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, Any

class UnifiedConfigManager:
    """통합 설정 관리자"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.config_dir = os.path.join(self.project_root, 'config')
        self.master_config_file = os.path.join(self.config_dir, 'master_config.yaml')
        
        os.makedirs(self.config_dir, exist_ok=True)
    
    def create_master_config(self, user_config: Dict[str, Any]) -> bool:
        """마스터 설정 파일 생성"""
        try:
            # 마스터 설정 구조
            master_config = {
                'meta': {
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '1.0.0',
                    'config_type': 'master'
                },
                'user': user_config.get('user', {}),
                'security': user_config.get('security', {}),
                'logging': user_config.get('logging', {}),
                'telegram': user_config.get('telegram', {}),
                'exchange_keys': user_config.get('exchange_keys', {}),
                'exchanges': {
                    'upbit': {
                        'enabled': 'upbit' in user_config.get('exchange_keys', {}),
                        'config_file': '../upbit/env.yaml'
                    },
                    'bybit': {
                        'enabled': 'bybit' in user_config.get('exchange_keys', {}),
                        'config_file': '../bybit/env.yaml'
                    }
                }
            }
            
            with open(self.master_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(master_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            
            print(f"✅ 마스터 설정 생성: {self.master_config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 마스터 설정 생성 실패: {e}")
            return False
    
    def create_exchange_config(self, exchange: str, algorithm_config: Dict[str, Any]) -> bool:
        """거래소별 설정 파일 생성 (마스터 참조 + 알고리즘)"""
        try:
            # 마스터 설정 로드
            if not os.path.exists(self.master_config_file):
                print("❌ 마스터 설정이 없습니다. 먼저 공통 설정을 완료하세요.")
                return False
            
            with open(self.master_config_file, 'r', encoding='utf-8') as f:
                master_config = yaml.safe_load(f)
            
            # 거래소별 설정 생성
            exchange_config = {
                'meta': {
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '1.0.0',
                    'config_type': f'{exchange}_algorithm',
                    'master_config': '../config/master_config.yaml'
                },
                # 마스터에서 공통 설정 상속
                'user_name': master_config['user'].get('user_name'),
                'environment': master_config['user'].get('environment'),
                'security': master_config['security'],
                'logging': master_config['logging'],
                'telegram': master_config['telegram'],
                'exchange_keys': {
                    exchange: master_config['exchange_keys'].get(exchange, {})
                },
                # 거래소별 알고리즘 설정 추가
                **algorithm_config
            }
            
            # 거래소 디렉토리에 저장
            exchange_dir = os.path.join(self.project_root, exchange)
            config_file = os.path.join(exchange_dir, 'env.yaml')
            
            # 기존 파일 백업
            if os.path.exists(config_file):
                backup_file = f"{config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(config_file, backup_file)
                print(f"💾 기존 설정 백업: {backup_file}")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(exchange_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            
            print(f"✅ {exchange} 설정 생성: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ {exchange} 설정 생성 실패: {e}")
            return False
    
    def update_master_config(self, updates: Dict[str, Any]) -> bool:
        """마스터 설정 업데이트"""
        try:
            if not os.path.exists(self.master_config_file):
                print("❌ 마스터 설정이 없습니다.")
                return False
            
            with open(self.master_config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 깊은 업데이트
            def deep_update(target, source):
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        deep_update(target[key], value)
                    else:
                        target[key] = value
            
            deep_update(config, updates)
            
            with open(self.master_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            
            print("✅ 마스터 설정 업데이트 완료")
            return True
            
        except Exception as e:
            print(f"❌ 마스터 설정 업데이트 실패: {e}")
            return False
    
    def sync_exchange_configs(self) -> bool:
        """모든 거래소 설정을 마스터와 동기화"""
        try:
            if not os.path.exists(self.master_config_file):
                print("❌ 마스터 설정이 없습니다.")
                return False
            
            with open(self.master_config_file, 'r', encoding='utf-8') as f:
                master_config = yaml.safe_load(f)
            
            # 각 거래소별 설정 업데이트
            for exchange in ['upbit', 'bybit']:
                config_file = os.path.join(self.project_root, exchange, 'env.yaml')
                
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        exchange_config = yaml.safe_load(f)
                    
                    # 공통 설정 동기화
                    exchange_config['user_name'] = master_config['user'].get('user_name')
                    exchange_config['environment'] = master_config['user'].get('environment')
                    exchange_config['security'] = master_config['security']
                    exchange_config['logging'] = master_config['logging']
                    exchange_config['telegram'] = master_config['telegram']
                    exchange_config['exchange_keys'] = {
                        exchange: master_config['exchange_keys'].get(exchange, {})
                    }
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        yaml.dump(exchange_config, f, default_flow_style=False, 
                                 allow_unicode=True, indent=2, sort_keys=False)
                    
                    print(f"✅ {exchange} 설정 동기화 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 동기화 실패: {e}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """현재 설정 상태 확인"""
        status = {
            'master_config': {
                'exists': os.path.exists(self.master_config_file),
                'path': self.master_config_file
            },
            'exchange_configs': {}
        }
        
        for exchange in ['upbit', 'bybit']:
            config_file = os.path.join(self.project_root, exchange, 'env.yaml')
            status['exchange_configs'][exchange] = {
                'exists': os.path.exists(config_file),
                'path': config_file
            }
        
        return status
    
    def cleanup_legacy_configs(self):
        """기존 중복 설정 파일 정리"""
        print("\n🧹 기존 설정 파일 정리:")
        
        # config/dev, config/prod 디렉토리 확인
        for env in ['dev', 'prod']:
            env_dir = os.path.join(self.config_dir, env)
            if os.path.exists(env_dir):
                print(f"📁 발견된 기존 환경 설정: {env_dir}")
                
                cleanup = input(f"{env} 환경 설정을 백업 후 정리하시겠습니까? (y/n) [n]: ").strip().lower() == 'y'
                if cleanup:
                    backup_dir = f"{env_dir}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    import shutil
                    shutil.move(env_dir, backup_dir)
                    print(f"💾 백업 완료: {backup_dir}")
        
        # config/user_config.yaml 확인
        user_config_file = os.path.join(self.config_dir, 'user_config.yaml')
        if os.path.exists(user_config_file):
            print(f"📄 발견된 기존 사용자 설정: {user_config_file}")
            
            migrate = input("기존 사용자 설정을 마스터 설정으로 마이그레이션하시겠습니까? (y/n) [y]: ").strip().lower() != 'n'
            if migrate:
                try:
                    with open(user_config_file, 'r', encoding='utf-8') as f:
                        user_config = yaml.safe_load(f)
                    
                    self.create_master_config(user_config)
                    
                    # 백업 후 제거
                    backup_file = f"{user_config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    import shutil
                    shutil.move(user_config_file, backup_file)
                    print(f"💾 마이그레이션 완료, 기존 파일 백업: {backup_file}")
                    
                except Exception as e:
                    print(f"❌ 마이그레이션 실패: {e}")

def main():
    """메인 함수"""
    print("="*60)
    print("🔧 통합 설정 관리 도구")
    print("="*60)
    
    manager = UnifiedConfigManager()
    
    # 현재 상태 확인
    status = manager.get_config_status()
    
    print("\n📊 현재 설정 상태:")
    print(f"• 마스터 설정: {'✅ 있음' if status['master_config']['exists'] else '❌ 없음'}")
    for exchange, info in status['exchange_configs'].items():
        print(f"• {exchange} 설정: {'✅ 있음' if info['exists'] else '❌ 없음'}")
    
    if not status['master_config']['exists']:
        print("\n⚠️ 마스터 설정이 없습니다.")
        print("먼저 다음 명령어로 공통 설정을 완료하세요:")
        print("python user_config.py")
        return
    
    # 메뉴 선택
    print("\n🔧 수행할 작업을 선택하세요:")
    print("1. 거래소 설정 동기화")
    print("2. 기존 설정 파일 정리")
    print("3. 설정 상태 확인")
    print("4. 종료")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == '1':
        manager.sync_exchange_configs()
    elif choice == '2':
        manager.cleanup_legacy_configs()
    elif choice == '3':
        import json
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print("👋 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
