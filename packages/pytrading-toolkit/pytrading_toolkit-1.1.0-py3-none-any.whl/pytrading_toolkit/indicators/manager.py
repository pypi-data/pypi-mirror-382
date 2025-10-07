"""
공통 기술적 지표 계산 모듈 (TA-Lib 기반)
업비트와 바이비트 시스템에서 공통으로 사용
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional, Tuple
import warnings

# TA-Lib 경고 메시지 무시
warnings.filterwarnings('ignore', category=RuntimeWarning)

logger = logging.getLogger(__name__)

class IndicatorManager:
    """기술적 지표 관리 클래스"""
    
    def __init__(self):
        self.default_indicators = [
            {'type': 'SMA', 'period': 20},
            {'type': 'SMA', 'period': 50},
            {'type': 'EMA', 'period': 12},
            {'type': 'EMA', 'period': 26},
            {'type': 'RSI', 'period': 14},
            {'type': 'MACD', 'fast': 12, 'slow': 26, 'signal': 9},
            {'type': 'BB', 'period': 20, 'std': 2},
            {'type': 'PREV_HIGH', 'period': 1},
            {'type': 'PREV_LOW', 'period': 1}
        ]
    
    def get_default_config(self) -> List[Dict[str, Any]]:
        """기본 지표 설정 반환"""
        return self.default_indicators.copy()

def _prepare_data(candles: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """캔들 데이터를 TA-Lib 형식으로 준비"""
    try:
        df = pd.DataFrame(candles)
        
        # 컬럼명 표준화
        column_mapping = {
            'trade_price': 'close',
            'opening_price': 'open',
            'high_price': 'high',
            'low_price': 'low',
            'candle_acc_trade_volume': 'volume',
            'candle_date_time_kst': 'timestamp'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
        
        # 기본 OHLCV 컬럼 확인
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"필수 컬럼 누락: {col}")
        
        # 데이터 타입 변환
        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN 값 제거
        df = df.dropna(subset=required_columns)
        
        if len(df) < 2:
            raise ValueError("유효한 캔들 데이터 부족")
        
        # NumPy 배열로 변환
        open_prices = df['open'].values.astype(np.float64)
        high_prices = df['high'].values.astype(np.float64)
        low_prices = df['low'].values.astype(np.float64)
        close_prices = df['close'].values.astype(np.float64)
        volumes = df['volume'].values.astype(np.float64)
        
        return open_prices, high_prices, low_prices, close_prices, volumes
        
    except Exception as e:
        logger.error(f"데이터 준비 실패: {e}")
        raise

def calculate_indicators(candles: List[Dict], indicator_configs: List[Dict]) -> Dict[str, float]:
    """TA-Lib 기반 기술 지표 계산
    
    Args:
        candles: 캔들 데이터 리스트 [{'open', 'high', 'low', 'close', 'volume', 'timestamp'}, ...]
        indicator_configs: 지표 설정 리스트
        
    Returns:
        계산된 지표 딕셔너리
    """
    try:
        if not candles or len(candles) < 2:
            logger.warning("캔들 데이터 부족으로 지표 계산 불가")
            return {}
        
        open_prices, high_prices, low_prices, close_prices, volumes = _prepare_data(candles)
        
        indicators = {}
        data_length = len(close_prices)
        
        for config in indicator_configs:
            try:
                indicator_type = config['type']
                
                # 단순 이동평균
                if indicator_type == 'SMA':
                    period = config['period']
                    if data_length >= period:
                        sma = talib.SMA(close_prices, timeperiod=period)
                        result = sma[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'sma_{period}'] = float(result)
                
                # 지수 이동평균
                elif indicator_type == 'EMA':
                    period = config['period']
                    if data_length >= period:
                        ema = talib.EMA(close_prices, timeperiod=period)
                        result = ema[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'ema_{period}'] = float(result)
                
                # RSI (Relative Strength Index)
                elif indicator_type == 'RSI':
                    period = config['period']
                    if data_length >= period:
                        rsi = talib.RSI(close_prices, timeperiod=period)
                        result = rsi[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'rsi_{period}'] = float(result)
                
                # MACD
                elif indicator_type == 'MACD':
                    fast = config.get('fast', 12)
                    slow = config.get('slow', 26)
                    signal = config.get('signal', 9)
                    if data_length >= slow:
                        macd, macd_signal, macd_hist = talib.MACD(close_prices, 
                                                                 fastperiod=fast, 
                                                                 slowperiod=slow, 
                                                                 signalperiod=signal)
                        if not np.isnan(macd[-1]) and not np.isinf(macd[-1]):
                            indicators['macd'] = float(macd[-1])
                        if not np.isnan(macd_signal[-1]) and not np.isinf(macd_signal[-1]):
                            indicators['macd_signal'] = float(macd_signal[-1])
                        if not np.isnan(macd_hist[-1]) and not np.isinf(macd_hist[-1]):
                            indicators['macd_histogram'] = float(macd_hist[-1])
                
                # 볼린저 밴드
                elif indicator_type == 'BB':
                    period = config.get('period', 20)
                    std = config.get('std', 2)
                    if data_length >= period:
                        upper, middle, lower = talib.BBANDS(close_prices, 
                                                           timeperiod=period, 
                                                           nbdevup=std, 
                                                           nbdevdn=std, 
                                                           matype=0)
                        if not np.isnan(upper[-1]) and not np.isinf(upper[-1]):
                            indicators[f'bb_upper_{period}'] = float(upper[-1])
                        if not np.isnan(middle[-1]) and not np.isinf(middle[-1]):
                            indicators[f'bb_middle_{period}'] = float(middle[-1])
                        if not np.isnan(lower[-1]) and not np.isinf(lower[-1]):
                            indicators[f'bb_lower_{period}'] = float(lower[-1])
                        
                        # 볼린저 밴드 폭 계산
                        if not np.isnan(upper[-1]) and not np.isnan(lower[-1]) and not np.isnan(middle[-1]) and middle[-1] != 0:
                            bb_width = (upper[-1] - lower[-1]) / middle[-1]
                            indicators[f'bb_width_{period}'] = float(bb_width)
                
                # 스토캐스틱
                elif indicator_type == 'STOCH':
                    k_period = config.get('k_period', 14)
                    d_period = config.get('d_period', 3)
                    if data_length >= k_period:
                        slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices,
                                                 fastk_period=k_period,
                                                 slowk_period=d_period,
                                                 slowd_period=d_period)
                        if not np.isnan(slowk[-1]) and not np.isinf(slowk[-1]):
                            indicators['stoch_k'] = float(slowk[-1])
                        if not np.isnan(slowd[-1]) and not np.isinf(slowd[-1]):
                            indicators['stoch_d'] = float(slowd[-1])
                
                # ATR (Average True Range)
                elif indicator_type == 'ATR':
                    period = config.get('period', 14)
                    if data_length >= period:
                        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)
                        result = atr[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'atr_{period}'] = float(result)
                
                # 거래량 이동평균
                elif indicator_type == 'VOLUME_SMA':
                    period = config.get('period', 20)
                    if data_length >= period:
                        volume_sma = talib.SMA(volumes, timeperiod=period)
                        result = volume_sma[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'volume_sma_{period}'] = float(result)
                            
                            # 현재 거래량과 평균 거래량 비율
                            current_volume = volumes[-1]
                            if result > 0 and not np.isnan(current_volume):
                                volume_ratio = current_volume / result
                                indicators[f'volume_ratio_{period}'] = float(volume_ratio)
                
                # 이전 고가
                elif indicator_type == 'PREV_HIGH':
                    period = config.get('period', 1)
                    if data_length >= period + 1:
                        indicators[f'prev_high_{period}'] = float(high_prices[-(period + 1)])
                
                # 이전 저가
                elif indicator_type == 'PREV_LOW':
                    period = config.get('period', 1)
                    if data_length >= period + 1:
                        indicators[f'prev_low_{period}'] = float(low_prices[-(period + 1)])
                
                else:
                    logger.warning(f"지원하지 않는 지표 타입: {indicator_type}")
                    
            except Exception as e:
                logger.error(f"지표 계산 오류 ({config.get('type', 'unknown')}): {e}")
                continue
        
        logger.info(f"계산된 지표 수: {len(indicators)}")
        return indicators
        
    except Exception as e:
        logger.error(f"지표 계산 전체 오류: {e}")
        return {}

def calculate_support_resistance(candles: List[Dict], lookback: int = 20) -> Dict[str, float]:
    """지지선/저항선 계산"""
    try:
        if not candles or len(candles) < lookback * 2:
            return {}
        
        df = pd.DataFrame(candles)
        
        # 컬럼명 표준화
        if 'high_price' in df.columns:
            df['high'] = df['high_price']
        if 'low_price' in df.columns:
            df['low'] = df['low_price']
        
        if 'high' not in df.columns or 'low' not in df.columns:
            return {}
        
        highs = df['high'].tail(lookback)
        lows = df['low'].tail(lookback)
        
        # 피벗 포인트 찾기
        resistance_levels = []
        support_levels = []
        
        for i in range(2, len(highs) - 2):
            # 저항선 (고점)
            if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
                resistance_levels.append(highs.iloc[i])
            
            # 지지선 (저점)
            if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
                support_levels.append(lows.iloc[i])
        
        result = {}
        if resistance_levels:
            result['resistance'] = np.mean(resistance_levels)
            result['resistance_strength'] = len(resistance_levels)
        
        if support_levels:
            result['support'] = np.mean(support_levels)
            result['support_strength'] = len(support_levels)
        
        return result
        
    except Exception as e:
        logger.error(f"지지/저항선 계산 예외: {e}")
        return {}

def calculate_trend_indicators(candles: List[Dict]) -> Dict[str, Any]:
    """트렌드 지표 계산 (TA-Lib 기반)"""
    try:
        if not candles or len(candles) < 50:
            return {}
        
        open_prices, high_prices, low_prices, close_prices, volumes = _prepare_data(candles)
        
        trend_indicators = {}
        
        # SMA 기반 트렌드 분석
        if len(close_prices) >= 50:
            sma_20 = talib.SMA(close_prices, timeperiod=20)
            sma_50 = talib.SMA(close_prices, timeperiod=50)
            
            if not np.isnan(sma_20[-1]) and not np.isnan(sma_50[-1]):
                # 이동평균 기울기 (5일 기준)
                if len(sma_20) >= 5:
                    sma_20_slope = (sma_20[-1] - sma_20[-5]) / 5
                    trend_indicators['sma_20_slope'] = float(sma_20_slope)
                
                if len(sma_50) >= 5:
                    sma_50_slope = (sma_50[-1] - sma_50[-5]) / 5
                    trend_indicators['sma_50_slope'] = float(sma_50_slope)
                
                # 트렌드 방향 판단
                if sma_20[-1] > sma_50[-1] and trend_indicators.get('sma_20_slope', 0) > 0:
                    trend_indicators['trend'] = 'bullish'
                elif sma_20[-1] < sma_50[-1] and trend_indicators.get('sma_20_slope', 0) < 0:
                    trend_indicators['trend'] = 'bearish'
                else:
                    trend_indicators['trend'] = 'sideways'
        
        # ADX 기반 트렌드 강도
        if len(close_prices) >= 14:
            adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=14)
            if not np.isnan(adx[-1]):
                trend_indicators['adx'] = float(adx[-1])
                
                # ADX 기반 트렌드 강도 판단
                if adx[-1] > 25:
                    trend_indicators['trend_strength'] = 'strong'
                elif adx[-1] > 15:
                    trend_indicators['trend_strength'] = 'moderate'
                else:
                    trend_indicators['trend_strength'] = 'weak'
        
        return trend_indicators
        
    except Exception as e:
        logger.error(f"트렌드 지표 계산 예외: {e}")
        return {}

def get_market_sentiment(indicators: Dict[str, float]) -> Dict[str, Any]:
    """시장 심리 분석"""
    try:
        sentiment = {'score': 0, 'signals': []}
        
        # RSI 기반 신호
        if 'rsi_14' in indicators:
            rsi = indicators['rsi_14']
            if rsi < 30:
                sentiment['score'] += 1
                sentiment['signals'].append('RSI 과매도')
            elif rsi > 70:
                sentiment['score'] -= 1
                sentiment['signals'].append('RSI 과매수')
        
        # MACD 기반 신호
        if 'macd' in indicators and 'macd_signal' in indicators:
            if indicators['macd'] > indicators['macd_signal']:
                sentiment['score'] += 0.5
                sentiment['signals'].append('MACD 상승신호')
            else:
                sentiment['score'] -= 0.5
                sentiment['signals'].append('MACD 하락신호')
        
        # 거래량 기반 신호
        if 'volume_ratio_20' in indicators:
            if indicators['volume_ratio_20'] > 1.5:
                sentiment['signals'].append('거래량 급증')
            elif indicators['volume_ratio_20'] < 0.5:
                sentiment['signals'].append('거래량 급감')
        
        # 종합 판단
        if sentiment['score'] > 0.5:
            sentiment['overall'] = 'bullish'
        elif sentiment['score'] < -0.5:
            sentiment['overall'] = 'bearish'
        else:
            sentiment['overall'] = 'neutral'
        
        return sentiment
        
    except Exception as e:
        logger.error(f"시장 심리 분석 예외: {e}")
        return {'score': 0, 'signals': [], 'overall': 'neutral'}