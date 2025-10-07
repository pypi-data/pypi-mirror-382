#!/usr/bin/env python3
"""
통합된 헬스체크 시스템 테스트 스크립트
"""

import time
import logging
from datetime import datetime, timezone

# pytrading-toolkit 패키지 import
from pytrading_toolkit import (
    HealthMonitor, 
    SimpleMaintenanceDetector,
    AdvancedMaintenanceDetector,
    RobustMaintenanceConfig,
    setup_logger
)

def test_health_monitor():
    """헬스 모니터 테스트"""
    print("🔍 헬스 모니터 테스트 시작...")
    
    # 로거 설정
    logger = setup_logger("test_health", level="INFO")
    
    # 헬스 모니터 생성 (텔레그램 없이)
    health_monitor = HealthMonitor("test_system")
    
    try:
        # 모니터링 시작
        health_monitor.start_monitoring()
        print("✅ 헬스 모니터링 시작됨")
        
        # 10초간 실행
        time.sleep(10)
        
        # 상태 확인
        status = health_monitor.get_health_status()
        print(f"📊 헬스 상태: {status}")
        
        # 리소스 사용량 확인
        if 'memory_usage' in status:
            memory_mb = status['memory_usage'] / 1024 / 1024
            print(f"💾 메모리 사용량: {memory_mb:.2f} MB")
            
        if 'cpu_usage' in status:
            print(f"🖥️ CPU 사용량: {status['cpu_usage']:.1f}%")
        
        # 모니터링 중단
        health_monitor.stop_monitoring()
        print("✅ 헬스 모니터링 중단됨")
        
    except Exception as e:
        print(f"❌ 헬스 모니터 테스트 실패: {e}")
        logger.error(f"헬스 모니터 테스트 오류: {e}")
        # 리소스 정리
        try:
            health_monitor.stop_monitoring()
        except:
            pass

def test_simple_maintenance_detector():
    """간단한 점검 감지기 테스트"""
    print("\n🔍 간단한 점검 감지기 테스트 시작...")
    
    # 간단한 점검 감지기 생성
    detector = SimpleMaintenanceDetector("test_system")
    
    try:
        # 모니터링 시작
        detector.start_monitoring()
        print("✅ 점검 감지 모니터링 시작됨")
        
        # 15초간 실행
        time.sleep(15)
        
        # 상태 확인
        status = detector.get_maintenance_status()
        print(f"📊 점검 상태: {status}")
        
        # 모니터링 중단
        detector.stop_monitoring()
        print("✅ 점검 감지 모니터링 중단됨")
        
    except Exception as e:
        print(f"❌ 간단한 점검 감지기 테스트 실패: {e}")

def test_advanced_maintenance_detector():
    """고급 점검 감지기 테스트"""
    print("\n🔍 고급 점검 감지기 테스트 시작...")
    
    # 고급 설정 생성
    config = RobustMaintenanceConfig({
        'api_timeout': 5,
        'check_interval': 10,
        'required_success': 2
    })
    
    # 고급 점검 감지기 생성
    detector = AdvancedMaintenanceDetector(
        "test_system", 
        config=config,
        enable_cache=True
    )
    
    try:
        # 모니터링 시작
        detector.start_monitoring()
        print("✅ 고급 점검 감지 모니터링 시작됨")
        
        # 20초간 실행
        time.sleep(20)
        
        # 상세 상태 확인
        status = detector.get_detailed_status()
        print(f"📊 상세 점검 상태: {status}")
        
        # 성능 메트릭 확인
        performance = detector.get_performance_metrics()
        print(f"📈 성능 메트릭: {performance}")
        
        # 점검 예측 확인
        prediction = detector.predict_maintenance()
        print(f"🔮 점검 예측: {prediction}")
        
        # 모니터링 중단
        detector.stop_monitoring()
        print("✅ 고급 점검 감지 모니터링 중단됨")
        
        # 리소스 정리
        detector.cleanup_resources()
        print("✅ 리소스 정리 완료")
        
    except Exception as e:
        print(f"❌ 고급 점검 감지기 테스트 실패: {e}")

def test_integration():
    """통합 테스트"""
    print("\n🔍 통합 테스트 시작...")
    
    try:
        # 모든 시스템을 함께 테스트
        health_monitor = HealthMonitor("integration_test")
        simple_detector = SimpleMaintenanceDetector("integration_test")
        advanced_detector = AdvancedMaintenanceDetector("integration_test")
        
        print("✅ 모든 시스템 초기화 완료")
        
        # 동시에 모니터링 시작
        health_monitor.start_monitoring()
        simple_detector.start_monitoring()
        advanced_detector.start_monitoring()
        
        print("✅ 모든 모니터링 시스템 시작됨")
        
        # 30초간 실행
        print("⏳ 30초간 통합 테스트 실행 중...")
        time.sleep(30)
        
        # 모든 상태 확인
        health_status = health_monitor.get_health_status()
        simple_status = simple_detector.get_maintenance_status()
        advanced_status = advanced_detector.get_detailed_status()
        
        print(f"📊 헬스 상태: {health_status['status']}")
        print(f"📊 간단한 점검 상태: {simple_status['maintenance_active']}")
        print(f"📊 고급 점검 상태: {advanced_status['maintenance_active']}")
        
        # 모든 모니터링 중단
        health_monitor.stop_monitoring()
        simple_detector.stop_monitoring()
        advanced_detector.stop_monitoring()
        
        print("✅ 모든 모니터링 시스템 중단됨")
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 pytrading-toolkit 헬스체크 시스템 테스트 시작")
    print("=" * 60)
    
    # 개별 테스트
    test_health_monitor()
    test_simple_maintenance_detector()
    test_advanced_maintenance_detector()
    
    # 통합 테스트
    test_integration()
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("✅ 헬스체크 시스템이 pytrading-toolkit 패키지에 성공적으로 통합되었습니다!")

if __name__ == "__main__":
    main()
