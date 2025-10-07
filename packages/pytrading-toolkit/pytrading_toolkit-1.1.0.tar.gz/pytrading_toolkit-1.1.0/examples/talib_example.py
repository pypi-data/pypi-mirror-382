#!/usr/bin/env python3
"""
TA-Lib 기반 기술지표 계산 예제
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytrading_toolkit.indicators import (
    calculate_indicators_talib,
    calculate_advanced_indicators_talib,
    get_market_sentiment_talib,
    calculate_trend_indicators_talib,
    get_talib_version,
    TALIB_AVAILABLE
)

def create_sample_data():
    """샘플 캔들 데이터 생성"""
    import pandas as pd
    import numpy as np
    
    # 가상의 가격 데이터 생성 (100일)
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # 기본 가격 (100에서 시작)
    base_price = 100
    returns = np.random.normal(0.001, 0.02, 100)  # 일일 수익률
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # OHLCV 데이터 생성
    candles = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # 간단한 OHLCV 생성 (실제로는 더 복잡한 로직 필요)
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = prices[i-1] if i > 0 else price
        volume = np.random.randint(1000, 10000)
        
        candles.append({
            'timestamp': date.isoformat(),
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    return candles

def main():
    """메인 함수"""
    print("🧪 TA-Lib 기반 기술지표 계산 예제")
    print("=" * 50)
    
    # TA-Lib 사용 가능 여부 확인
    if not TALIB_AVAILABLE:
        print("❌ TA-Lib이 설치되지 않았습니다.")
        print("설치 방법:")
        print("  pip install TA-Lib")
        print("  또는")
        print("  conda install -c conda-forge ta-lib")
        return
    
    print(f"✅ TA-Lib 버전: {get_talib_version()}")
    print()
    
    # 샘플 데이터 생성
    print("📊 샘플 데이터 생성 중...")
    candles = create_sample_data()
    print(f"생성된 캔들 데이터: {len(candles)}개")
    print()
    
    # 기본 지표 계산
    print("🔍 기본 기술지표 계산 중...")
    indicator_configs = [
        {'type': 'SMA', 'period': 20},
        {'type': 'EMA', 'period': 12},
        {'type': 'RSI', 'period': 14},
        {'type': 'MACD', 'fast': 12, 'slow': 26, 'signal': 9},
        {'type': 'BB', 'period': 20, 'std': 2},
        {'type': 'STOCH', 'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3},
        {'type': 'ATR', 'period': 14},
        {'type': 'CCI', 'period': 14},
        {'type': 'WILLR', 'period': 14},
        {'type': 'ADX', 'period': 14},
        {'type': 'AROON', 'period': 14},
        {'type': 'VOLUME_SMA', 'period': 20},
        {'type': 'OBV'},
        {'type': 'MFI', 'period': 14}
    ]
    
    basic_indicators = calculate_indicators_talib(candles, indicator_configs)
    
    print("📈 계산된 기본 지표:")
    for key, value in basic_indicators.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    print()
    
    # 고급 지표 계산
    print("🚀 고급 지표 계산 중...")
    advanced_indicators = calculate_advanced_indicators_talib(candles)
    
    print("📊 계산된 고급 지표:")
    for key, value in advanced_indicators.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    print()
    
    # 트렌드 지표 계산
    print("📈 트렌드 지표 계산 중...")
    trend_indicators = calculate_trend_indicators_talib(candles)
    
    print("🎯 계산된 트렌드 지표:")
    for key, value in trend_indicators.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    print()
    
    # 시장 심리 분석
    print("🧠 시장 심리 분석 중...")
    all_indicators = {**basic_indicators, **advanced_indicators, **trend_indicators}
    sentiment = get_market_sentiment_talib(all_indicators)
    
    print("💭 시장 심리 분석 결과:")
    print(f"  종합 점수: {sentiment['score']}")
    print(f"  전체 심리: {sentiment['overall']}")
    print(f"  심리 강도: {sentiment['strength']}")
    print("  신호들:")
    for signal in sentiment['signals']:
        print(f"    - {signal}")
    print()
    
    # 성능 비교 (선택적)
    print("⚡ 성능 비교 테스트...")
    import time
    
    # TA-Lib 성능 테스트
    start_time = time.time()
    for _ in range(100):
        calculate_indicators_talib(candles, indicator_configs)
    talib_time = time.time() - start_time
    
    print(f"TA-Lib 100회 계산 시간: {talib_time:.4f}초")
    print(f"평균 계산 시간: {talib_time/100*1000:.2f}ms")
    print()
    
    print("✅ 모든 테스트 완료!")
    print()
    print("📚 사용 가능한 TA-Lib 지표들:")
    print("  - 이동평균: SMA, EMA")
    print("  - 모멘텀: RSI, MACD, STOCH, CCI, WILLR, MFI")
    print("  - 변동성: BB, ATR")
    print("  - 트렌드: ADX, AROON")
    print("  - 거래량: OBV, Volume SMA")
    print("  - 패턴: Doji, Hammer, Engulfing")
    print("  - 피벗: Pivot Points, Support/Resistance")

if __name__ == "__main__":
    main()
