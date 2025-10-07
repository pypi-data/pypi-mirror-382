#!/usr/bin/env python3
"""
다중 거래소 설정 도구
새로운 통합 설정 구조를 생성하는 도구
"""

import os
import sys

# 공통 모듈 경로 추가 (새로운 구조)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'pytrading-toolkit'))

try:
    from config_wizard import ConfigWizard
except ImportError:
    print("⚠️ pytrading-toolkit의 config_wizard를 찾을 수 없습니다.")
    print("가상환경에서 실행하거나 패키지를 설치하세요.")
    sys.exit(1)
import yaml
import json

def update_trading_rules():
    """거래 규칙을 롱/숏 분리 구조로 업데이트"""
    
    # 현물용 규칙
    SPOT_RULES = {
        "description": "현물 거래 규칙 (매수/매도)",
        "type": "spot",
        "open": [
            ["prev_high_1d < close_1d", True],
            ["ma_200_1d < close_1d", True], 
            ["hour >= 9", True]
        ],
        "close": [
            ["low_1d < prev_low_1d", True],
            ["close_1d < ma_200_1d", True]
        ],
        "risk_management": {
            "max_loss_percent": 5.0,
            "take_profit_percent": 10.0,
            "stop_loss_percent": 3.0
        }
    }
    
    # 선물용 규칙
    FUTURES_RULES = {
        "description": "선물 거래 규칙 (롱/숏 분리)",
        "type": "futures",
        "long": {
            "entry": [
                ["prev_high_1d < close_1d", True],
                ["ma_200_1d < close_1d", True], 
                ["hour >= 9", True]
            ],
            "exit": [
                ["low_1d < prev_low_1d", True],
                ["close_1d < ma_200_1d", True]
            ]
        },
        "short": {
            "entry": [
                ["prev_low_1d > close_1d", True],
                ["ma_200_1d > close_1d", True],
                ["hour >= 9", True]
            ],
            "exit": [
                ["high_1d > prev_high_1d", True],
                ["close_1d > ma_200_1d", True]
            ]
        },
        "risk_management": {
            "max_loss_percent": 5.0,
            "take_profit_percent": 15.0,
            "stop_loss_percent": 3.0,
            "max_leverage": 10
        }
    }
    
    # 기존 통합 규칙 (호환성)
    NEW_TRADING_RULES = {
        "long": {
            "entry": [
                ["prev_high_1d < close_1d", True],
                ["ma_200_1d < close_1d", True], 
                ["hour >= 9", True]
            ],
            "exit": [
                ["low_1d < prev_low_1d", True],
                ["close_1d < ma_200_1d", True]
            ]
        },
        "short": {
            "entry": [
                ["prev_low_1d > close_1d", True],
                ["ma_200_1d > close_1d", True],
                ["hour >= 9", True]
            ],
            "exit": [
                ["high_1d > prev_high_1d", True],
                ["close_1d > ma_200_1d", True]
            ]
        },
        "legacy": {
            "entry": [
                ["prev_high_1d < close_1d", True],
                ["ma_200_1d < close_1d", True],
                ["hour >= 9", True]
            ],
            "exit": [
                ["low_1d < prev_low_1d", True],
                ["close_1d < ma_200_1d", True]
            ]
        }
    }
    
    config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'trader', 'config')
    
    # dev와 prod 환경 모두 업데이트
    for env in ['dev', 'prod']:
        env_dir = os.path.join(config_dir, env)
        os.makedirs(env_dir, exist_ok=True)
        
        # 거래 유형별 규칙 파일 생성
        spot_rules_file = os.path.join(env_dir, 'spot_rules.json')
        futures_rules_file = os.path.join(env_dir, 'futures_rules.json')
        trading_rules_file = os.path.join(env_dir, 'trading_rules.json')
        
        # 환경별 리스크 조정
        spot_rules = SPOT_RULES.copy()
        futures_rules = FUTURES_RULES.copy()
        
        if env == 'prod':
            # 운영환경에서는 더 보수적으로
            spot_rules['risk_management']['max_loss_percent'] = 3.0
            spot_rules['risk_management']['take_profit_percent'] = 8.0
            spot_rules['risk_management']['stop_loss_percent'] = 2.0
            
            futures_rules['risk_management']['max_loss_percent'] = 3.0
            futures_rules['risk_management']['take_profit_percent'] = 12.0
            futures_rules['risk_management']['stop_loss_percent'] = 2.0
            futures_rules['risk_management']['max_leverage'] = 5
        
        # 거래 유형별 파일 생성
        with open(spot_rules_file, 'w', encoding='utf-8') as f:
            json.dump(spot_rules, f, indent=2, ensure_ascii=False)
        print(f"✅ {env}/spot_rules.json 생성 완료")
        
        with open(futures_rules_file, 'w', encoding='utf-8') as f:
            json.dump(futures_rules, f, indent=2, ensure_ascii=False)
        print(f"✅ {env}/futures_rules.json 생성 완료")
        
        # 레거시 trading_rules.json은 더 이상 생성하지 않음
        # 새로운 구조: spot_rules.json, futures_rules.json 사용

def setup_multi_exchange():
    """다중 거래소 설정"""
    print("="*60)
    print("🌐 다중 거래소 통합 설정 도구")
    print("="*60)
    
    wizard = ConfigWizard()
    
    # 환경 선택
    print("\n🏗️ 환경 설정:")
    print("1. dev (개발/테스트)")
    print("2. prod (실제 운영)")
    env_choice = input("환경 선택 (1/2) [1]: ").strip()
    environment = 'prod' if env_choice == '2' else 'dev'
    
    # 시스템 설정
    config = wizard.get_system_config('다중거래소')
    config['environment'] = environment
    
    # 보안 설정
    config['security'] = wizard.get_security_config()
    
    # 로깅 설정
    config['logging'] = wizard.get_logging_config()
    
    # 텔레그램 설정
    config['telegram'] = wizard.get_telegram_config()
    
    # 거래소별 API 키 설정
    print("\n🔑 거래소 API 키 설정")
    print("=" * 40)
    
    exchange_keys = {}
    
    # 업비트
    setup_upbit = input("업비트 API 키 설정? (y/n) [y]: ").strip().lower() != 'n'
    if setup_upbit:
        upbit_keys = wizard.get_api_keys('upbit')
        if upbit_keys:
            exchange_keys['upbit'] = upbit_keys
    
    # 바이비트
    setup_bybit = input("바이비트 API 키 설정? (y/n) [y]: ").strip().lower() != 'n'
    if setup_bybit:
        bybit_keys = wizard.get_api_keys('bybit')
        if bybit_keys:
            exchange_keys['bybit'] = bybit_keys
    
    # 바이낸스 (기존 호환성)
    setup_binance = input("바이낸스 API 키 설정? (y/n) [n]: ").strip().lower() == 'y'
    if setup_binance:
        print("\n🟡 바이낸스 API 키:")
        import getpass
        api_key = getpass.getpass("API Key: ").strip()
        api_secret = getpass.getpass("API Secret: ").strip()
        
        if api_key and api_secret:
            exchange_keys['binance'] = {
                'api_key': api_key,
                'secret_key': api_secret
            }
    
    config['exchange_keys'] = exchange_keys
    
    # 새로운 설정 구조 생성
    config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'trader', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # 환경별 디렉토리 생성 (레거시 - 비활성화)
    # env_dir = os.path.join(config_dir, environment)
    # users_dir = os.path.join(env_dir, 'users')
    # exchanges_dir = os.path.join(env_dir, 'exchanges')
    # algorithms_dir = os.path.join(env_dir, 'algorithms')
    
    # os.makedirs(users_dir, exist_ok=True)
    # os.makedirs(exchanges_dir, exist_ok=True)
    # os.makedirs(algorithms_dir, exist_ok=True)
    
    # 거래 규칙 업데이트 (롱/숏 분리) - 레거시 비활성화
    # print("\n📊 거래 규칙 업데이트 중...")
    # update_trading_rules()
    
    # 사용자 설정 파일 생성
    user_name = config.get('user_name', 'default_user')
    user_config = {
        'user': {
            'id': user_name,
            'name': config.get('user_name', '기본 사용자'),
            'email': config.get('email', 'default@example.com'),
            'environment': environment
        },
        'api_keys': exchange_keys,
        'telegram': config['telegram'],
        'trading': {
            'test_mode': environment == 'dev',
            'risk_level': 'medium',
            'max_daily_loss': 0.05,
            'max_position_size': 0.1
        },
        'upbit': {
            'market': 'KRW-BTC',
            'amount': 10000,
            'buy_fill_rate_threshold': 0.9
        },
        'bybit': {
            'market': 'BTCUSDC',
            'leverage': 10,
            'position_size_ratio': 0.1
        },
        'security': config['security']
    }
    
    user_file = os.path.join(users_dir, f"{user_name}.yaml")
    with open(user_file, 'w', encoding='utf-8') as f:
        yaml.dump(user_config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    # 거래소별 설정 파일 생성
    upbit_config = {
        'exchange': {
            'name': 'upbit',
            'type': 'spot',
            'country': 'KR',
            'base_currency': 'KRW'
        },
        'api': {
            'base_url': 'https://api.upbit.com',
            'websocket_url': 'wss://api.upbit.com/websocket/v1',
            'rate_limit': 10
        },
        'trading': {
            'min_order_amount': 5000,
            'max_order_amount': 10000000,
            'supported_markets': ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        },
        'security': {
            'require_2fa': False,
            'ip_whitelist': False
        },
        'telegram': {
            'enabled': False,
            'bot_token': '',
            'chat_id': ''
        },
        'logging': config['logging']
    }
    
    upbit_file = os.path.join(exchanges_dir, 'upbit.yaml')
    with open(upbit_file, 'w', encoding='utf-8') as f:
        yaml.dump(upbit_config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    bybit_config = {
        'exchange': {
            'name': 'bybit',
            'type': 'futures',
            'country': 'SG',
            'base_currency': 'USDC'
        },
        'api': {
            'base_url': 'https://api-testnet.bybit.com' if environment == 'dev' else 'https://api.bybit.com',
            'websocket_url': 'wss://stream-testnet.bybit.com/v5/public/linear' if environment == 'dev' else 'wss://stream.bybit.com/v5/public/linear',
            'rate_limit': 20
        },
        'trading': {
            'min_order_amount': 10,
            'max_order_amount': 10000,
            'supported_markets': ['BTCUSDC', 'ETHUSDC', 'XRPUSDC'],
            'max_leverage': 100
        },
        'futures': {
            'category': 'linear',
            'position_mode': 'BothSide',
            'default_leverage': 10
        },
        'security': {
            'require_2fa': False,
            'ip_whitelist': False
        },
        'telegram': {
            'enabled': False,
            'bot_token': '',
            'chat_id': ''
        },
        'logging': config['logging']
    }
    
    bybit_file = os.path.join(exchanges_dir, 'bybit.yaml')
    with open(bybit_file, 'w', encoding='utf-8') as f:
        yaml.dump(bybit_config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print("\n" + "="*60)
    print("✅ 새로운 설정 구조 생성 완료!")
    print("="*60)
    print(f"\n📁 생성된 설정 파일:")
    print(f"• 사용자 설정: {user_file}")
    print(f"• 업비트 설정: {upbit_file}")
    print(f"• 바이비트 설정: {bybit_file}")
    print(f"• 거래 규칙: {algorithms_dir}/spot_rules.json, futures_rules.json")
    
    print(f"\n📋 다음 단계:")
    print("1. API 키 설정:")
    print(f"   - {user_file} 파일에서 API 키를 실제 값으로 변경")
    print("2. 시스템 테스트:")
    print("   - ./start_upbit.sh --live")
    print("   - ./start_bybit.sh --live")
    
    return True

def main():
    """메인 함수"""
    setup_multi_exchange()

if __name__ == "__main__":
    main()
