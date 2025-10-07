#!/usr/bin/env python3
"""
PyTrading Toolkit 기본 사용법 예제

이 예제는 pytrading-toolkit의 주요 기능들을 기본적으로 사용하는 방법을 보여줍니다.
"""

import sys
import os
from datetime import datetime

# 패키지 import
try:
    from pytrading_toolkit import (
        BaseConfigLoader,
        UpbitConfigLoader,
        BybitConfigLoader,
        TelegramNotifier,
        setup_logger,
        HealthMonitor,
        get_kst_now,
        get_utc_now
    )
    print("✅ pytrading-toolkit import 성공!")
except ImportError as e:
    print(f"❌ pytrading-toolkit import 실패: {e}")
    print("💡 패키지를 먼저 설치해주세요: pip install -e .")
    sys.exit(1)

def test_config_loaders():
    """설정 로더 테스트"""
    print("\n🔧 설정 로더 테스트")
    print("=" * 50)
    
    try:
        # 기본 설정 로더
        print("1. 기본 설정 로더 테스트...")
        base_loader = BaseConfigLoader("example_config.yaml")
        print("   ✅ BaseConfigLoader 생성 성공")
        
        # 업비트 설정 로더
        print("2. 업비트 설정 로더 테스트...")
        upbit_loader = UpbitConfigLoader()
        print("   ✅ UpbitConfigLoader 생성 성공")
        
        # 바이비트 설정 로더
        print("3. 바이비트 설정 로더 테스트...")
        bybit_loader = BybitConfigLoader()
        print("   ✅ BybitConfigLoader 생성 성공")
        
        print("   🎯 모든 설정 로더 생성 성공!")
        
    except Exception as e:
        print(f"   ❌ 설정 로더 테스트 실패: {e}")

def test_logging():
    """로깅 시스템 테스트"""
    print("\n📝 로깅 시스템 테스트")
    print("=" * 50)
    
    try:
        # 로거 설정
        logger = setup_logger('example', log_dir='./logs', level='INFO')
        print("✅ 로거 설정 성공")
        
        # 로그 메시지 테스트
        logger.info("정보 로그 메시지")
        logger.warning("경고 로그 메시지")
        logger.error("에러 로그 메시지")
        
        print("✅ 로그 메시지 출력 성공")
        print("📁 로그 파일 확인: ./logs/")
        
    except Exception as e:
        print(f"❌ 로깅 테스트 실패: {e}")

def test_telegram():
    """텔레그램 알림 테스트 (설정이 있는 경우)"""
    print("\n📱 텔레그램 알림 테스트")
    print("=" * 50)
    
    try:
        # 설정 파일에서 텔레그램 정보 확인
        upbit_loader = UpbitConfigLoader()
        config = upbit_loader.load_config()
        
        bot_token = config.get('telegram', {}).get('bot_token')
        chat_id = config.get('telegram', {}).get('chat_id')
        
        if bot_token and chat_id and not bot_token.startswith('your-'):
            print("✅ 텔레그램 설정 발견")
            
            # 텔레그램 노티파이어 생성
            notifier = TelegramNotifier(bot_token, chat_id)
            print("✅ TelegramNotifier 생성 성공")
            
            # 테스트 메시지 전송
            message = f"🧪 PyTrading Toolkit 테스트 메시지\n시간: {get_kst_now()}"
            notifier.send_message(message)
            print("✅ 테스트 메시지 전송 성공")
            
        else:
            print("⚠️  텔레그램 설정이 없거나 기본값입니다")
            print("   📝 env.yaml에서 bot_token과 chat_id를 설정해주세요")
            
    except Exception as e:
        print(f"❌ 텔레그램 테스트 실패: {e}")

def test_time_utils():
    """시간 유틸리티 테스트"""
    print("\n⏰ 시간 유틸리티 테스트")
    print("=" * 50)
    
    try:
        # KST 시간
        kst_now = get_kst_now()
        print(f"✅ KST 현재 시간: {kst_now}")
        
        # UTC 시간
        utc_now = get_utc_now()
        print(f"✅ UTC 현재 시간: {utc_now}")
        
        # 시간 차이 계산
        time_diff = kst_now - utc_now
        print(f"✅ KST-UTC 차이: {time_diff}")
        
    except Exception as e:
        print(f"❌ 시간 유틸리티 테스트 실패: {e}")

def test_health_monitor():
    """헬스 모니터 테스트"""
    print("\n🏥 헬스 모니터 테스트")
    print("=" * 50)
    
    try:
        # 헬스 모니터 생성
        health_monitor = HealthMonitor("example_system", None)
        print("✅ HealthMonitor 생성 성공")
        
        # 상태 체크
        status = health_monitor.get_status()
        print(f"✅ 시스템 상태: {status}")
        
        print("✅ 헬스 모니터 테스트 성공")
        
    except Exception as e:
        print(f"❌ 헬스 모니터 테스트 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 PyTrading Toolkit 기본 사용법 예제")
    print("=" * 60)
    print(f"시작 시간: {datetime.now()}")
    
    # 각 기능 테스트
    test_config_loaders()
    test_logging()
    test_telegram()
    test_time_utils()
    test_health_monitor()
    
    print("\n" + "=" * 60)
    print("🎉 모든 기본 기능 테스트 완료!")
    print("💡 더 자세한 사용법은 README.md를 참조하세요")

if __name__ == "__main__":
    main()
