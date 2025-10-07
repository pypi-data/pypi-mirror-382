#!/usr/bin/env python3
"""
설정 관리 모듈 테스트 스크립트

이 스크립트는 pytrading-toolkit의 설정 관리 기능을 테스트합니다.
"""

import sys
import os
import tempfile
import yaml
from datetime import datetime

# 패키지 import
try:
    from pytrading_toolkit import (
        BaseConfigLoader,
        UpbitConfigLoader,
        BybitConfigLoader
    )
    print("✅ 설정 모듈 import 성공!")
except ImportError as e:
    print(f"❌ 설정 모듈 import 실패: {e}")
    sys.exit(1)

def create_test_config():
    """테스트용 설정 파일 생성"""
    config = {
        'env': 'test',
        'active_user': 'test_user',
        'test_mode': True,
        'exchange_keys': {
            'upbit': {
                'access_key': 'test_access_key',
                'secret_key': 'test_secret_key'
            },
            'bybit': {
                'api_key': 'test_api_key',
                'secret_key': 'test_secret_key'
            }
        },
        'telegram': {
            'bot_token': 'test_bot_token',
            'chat_id': 'test_chat_id'
        },
        'trading': {
            'market': 'KRW-BTC',
            'amount': 10000
        }
    }
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file, default_flow_style=False)
    temp_file.close()
    
    return temp_file.name

def test_base_config_loader():
    """BaseConfigLoader 테스트"""
    print("\n🔧 BaseConfigLoader 테스트")
    print("-" * 40)
    
    try:
        # 테스트 설정 파일 생성
        config_file = create_test_config()
        print(f"📁 테스트 설정 파일 생성: {config_file}")
        
        # BaseConfigLoader 생성
        loader = BaseConfigLoader(config_file)
        print("✅ BaseConfigLoader 생성 성공")
        
        # 설정 로드
        config = loader.load_config()
        print("✅ 설정 로드 성공")
        
        # 설정 내용 확인
        assert config['env'] == 'test'
        assert config['active_user'] == 'test_user'
        print("✅ 설정 내용 검증 성공")
        
        # 중첩 값 조회 테스트
        upbit_key = loader.get_nested_value(config, 'exchange_keys.upbit.access_key')
        assert upbit_key == 'test_access_key'
        print("✅ 중첩 값 조회 성공")
        
        # 기본값 테스트
        default_value = loader.get_nested_value(config, 'nonexistent.key', 'default')
        assert default_value == 'default'
        print("✅ 기본값 처리 성공")
        
        # 임시 파일 정리
        os.unlink(config_file)
        print("✅ 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ BaseConfigLoader 테스트 실패: {e}")
        return False

def test_upbit_config_loader():
    """UpbitConfigLoader 테스트"""
    print("\n🔧 UpbitConfigLoader 테스트")
    print("-" * 40)
    
    try:
        # 테스트 설정 파일 생성
        config_file = create_test_config()
        
        # UpbitConfigLoader 생성
        loader = UpbitConfigLoader(config_file)
        print("✅ UpbitConfigLoader 생성 성공")
        
        # 설정 검증
        config = loader.load_config()
        is_valid = loader.validate_config(config)
        print(f"✅ 설정 검증 결과: {is_valid}")
        
        # 알고리즘 설정 테스트
        algo_config = loader.get_algorithm_config()
        print(f"✅ 알고리즘 설정: {algo_config}")
        
        # 거래 규칙 테스트
        trading_rules = loader.get_trading_rules()
        print(f"✅ 거래 규칙: {trading_rules}")
        
        # 임시 파일 정리
        os.unlink(config_file)
        print("✅ 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ UpbitConfigLoader 테스트 실패: {e}")
        return False

def test_bybit_config_loader():
    """BybitConfigLoader 테스트"""
    print("\n🔧 BybitConfigLoader 테스트")
    print("-" * 40)
    
    try:
        # 테스트 설정 파일 생성
        config_file = create_test_config()
        
        # BybitConfigLoader 생성
        loader = BybitConfigLoader(config_file)
        print("✅ BybitConfigLoader 생성 성공")
        
        # 설정 검증
        config = loader.load_config()
        is_valid = loader.validate_config(config)
        print(f"✅ 설정 검증 결과: {is_valid}")
        
        # 알고리즘 설정 테스트
        algo_config = loader.get_algorithm_config()
        print(f"✅ 알고리즘 설정: {algo_config}")
        
        # 거래 규칙 테스트
        trading_rules = loader.get_trading_rules()
        print(f"✅ 거래 규칙: {trading_rules}")
        
        # 임시 파일 정리
        os.unlink(config_file)
        print("✅ 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ BybitConfigLoader 테스트 실패: {e}")
        return False

def test_config_validation():
    """설정 검증 테스트"""
    print("\n🔧 설정 검증 테스트")
    print("-" * 40)
    
    try:
        # 잘못된 설정 테스트
        invalid_config = {
            'exchange_keys': {
                'upbit': {
                    'access_key': 'your-access-key',  # 기본값
                    'secret_key': 'your-secret-key'   # 기본값
                }
            }
        }
        
        # UpbitConfigLoader로 검증
        loader = UpbitConfigLoader()
        is_valid = loader.validate_config(invalid_config)
        print(f"✅ 잘못된 설정 검증 결과: {is_valid} (예상: False)")
        
        # 올바른 설정 테스트
        valid_config = {
            'exchange_keys': {
                'upbit': {
                    'access_key': 'real_access_key',
                    'secret_key': 'real_secret_key'
                }
            }
        }
        
        is_valid = loader.validate_config(valid_config)
        print(f"✅ 올바른 설정 검증 결과: {is_valid} (예상: True)")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 검증 테스트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🧪 PyTrading Toolkit 설정 관리 모듈 테스트")
    print("=" * 60)
    print(f"시작 시간: {datetime.now()}")
    
    # 테스트 실행
    tests = [
        test_base_config_loader,
        test_upbit_config_loader,
        test_bybit_config_loader,
        test_config_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
