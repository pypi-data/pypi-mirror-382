"""
공통 기술적 지표 계산 모듈
업비트와 바이비트 시스템에서 공통으로 사용
"""

import pandas as pd
import numpy as np
import ta
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional

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

def calculate_indicators(candles: List[Dict], indicator_configs: List[Dict]) -> Dict[str, float]:
    """기술 지표 계산
    
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
        
        # DataFrame 생성 - 다양한 데이터 포맷 지원
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
                logger.error(f"필수 컬럼 누락: {col}")
                return {}
        
        # 데이터 타입 변환
        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN 값 제거
        df = df.dropna(subset=required_columns)
        
        if len(df) < 2:
            logger.warning("유효한 캔들 데이터 부족")
            return {}
        
        indicators = {}
        
        for config in indicator_configs:
            try:
                indicator_type = config['type']
                
                if indicator_type == 'SMA':
                    period = config['period']
                    if len(df) >= period:
                        sma = ta.trend.SMAIndicator(df['close'], window=period)
                        result = sma.sma_indicator().iloc[-1]
                        if not pd.isna(result):
                            indicators[f'sma_{period}'] = result
                
                elif indicator_type == 'EMA':
                    period = config['period']
                    if len(df) >= period:
                        ema = ta.trend.EMAIndicator(df['close'], window=period)
                        result = ema.ema_indicator().iloc[-1]
                        if not pd.isna(result):
                            indicators[f'ema_{period}'] = result
                
                elif indicator_type == 'RSI':
                    period = config['period']
                    if len(df) >= period + 1:
                        rsi = ta.momentum.RSIIndicator(df['close'], window=period)
                        result = rsi.rsi().iloc[-1]
                        if not pd.isna(result):
                            indicators[f'rsi_{period}'] = result
                
                elif indicator_type == 'MACD':
                    fast = config.get('fast', 12)
                    slow = config.get('slow', 26)
                    signal = config.get('signal', 9)
                    if len(df) >= slow + signal:
                        macd = ta.trend.MACD(df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
                        
                        macd_line = macd.macd().iloc[-1]
                        macd_signal = macd.macd_signal().iloc[-1]
                        macd_histogram = macd.macd_diff().iloc[-1]
                        
                        if not pd.isna(macd_line):
                            indicators['macd_line'] = macd_line
                        if not pd.isna(macd_signal):
                            indicators['macd_signal'] = macd_signal
                        if not pd.isna(macd_histogram):
                            indicators['macd_histogram'] = macd_histogram
                
                elif indicator_type == 'BB':
                    period = config.get('period', 20)
                    std = config.get('std', 2)
                    if len(df) >= period:
                        bb = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std)
                        
                        bb_upper = bb.bollinger_hband().iloc[-1]
                        bb_middle = bb.bollinger_mavg().iloc[-1]
                        bb_lower = bb.bollinger_lband().iloc[-1]
                        
                        if not pd.isna(bb_upper):
                            indicators['bb_upper'] = bb_upper
                        if not pd.isna(bb_middle):
                            indicators['bb_middle'] = bb_middle
                        if not pd.isna(bb_lower):
                            indicators['bb_lower'] = bb_lower
                        
                        # 볼린저 밴드 폭
                        if not pd.isna(bb_upper) and not pd.isna(bb_lower) and not pd.isna(bb_middle) and bb_middle > 0:
                            bb_width = (bb_upper - bb_lower) / bb_middle * 100
                            indicators['bb_width'] = bb_width
                
                elif indicator_type == 'STOCH':
                    k_period = config.get('k_period', 14)
                    d_period = config.get('d_period', 3)
                    if len(df) >= k_period + d_period:
                        stoch = ta.momentum.StochasticOscillator(
                            df['high'], df['low'], df['close'], 
                            window=k_period, smooth_window=d_period
                        )
                        
                        stoch_k = stoch.stoch().iloc[-1]
                        stoch_d = stoch.stoch_signal().iloc[-1]
                        
                        if not pd.isna(stoch_k):
                            indicators['stoch_k'] = stoch_k
                        if not pd.isna(stoch_d):
                            indicators['stoch_d'] = stoch_d
                
                elif indicator_type == 'PREV_HIGH':
                    period = config.get('period', 1)
                    if len(df) > period:
                        prev_high = df['high'].iloc[-(period + 1)]
                        if not pd.isna(prev_high):
                            if period == 1:
                                indicators['prev_high_1'] = prev_high
                            else:
                                indicators[f'prev_high_{period}'] = prev_high
                
                elif indicator_type == 'PREV_LOW':
                    period = config.get('period', 1)
                    if len(df) > period:
                        prev_low = df['low'].iloc[-(period + 1)]
                        if not pd.isna(prev_low):
                            if period == 1:
                                indicators['prev_low_1'] = prev_low
                            else:
                                indicators[f'prev_low_{period}'] = prev_low
                
                elif indicator_type == 'ATR':
                    period = config.get('period', 14)
                    if len(df) >= period:
                        atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=period)
                        result = atr.average_true_range().iloc[-1]
                        if not pd.isna(result):
                            indicators[f'atr_{period}'] = result
                
                elif indicator_type == 'VOLUME_SMA':
                    period = config.get('period', 20)
                    if len(df) >= period:
                        volume_sma = df['volume'].rolling(window=period).mean().iloc[-1]
                        if not pd.isna(volume_sma):
                            indicators[f'volume_sma_{period}'] = volume_sma
                            
                            # 현재 거래량과 평균 거래량 비율
                            current_volume = df['volume'].iloc[-1]
                            if volume_sma > 0 and not pd.isna(current_volume):
                                volume_ratio = current_volume / volume_sma
                                indicators[f'volume_ratio_{period}'] = volume_ratio
                
            except Exception as e:
                logger.warning(f"지표 계산 실패 ({indicator_type}): {e}")
                continue
        
        # NaN 값 제거
        indicators = {k: v for k, v in indicators.items() if not pd.isna(v)}
        
        logger.debug(f"지표 계산 완료: {len(indicators)}개")
        return indicators
        
    except Exception as e:
        logger.error(f"지표 계산 예외: {e}")
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
    """트렌드 지표 계산"""
    try:
        if not candles or len(candles) < 50:
            return {}
        
        df = pd.DataFrame(candles)
        
        # 컬럼명 표준화
        if 'trade_price' in df.columns:
            df['close'] = df['trade_price']
        
        if 'close' not in df.columns:
            return {}
        
        # 트렌드 강도 계산
        sma_20 = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
        sma_50 = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
        
        trend_indicators = {}
        
        if len(sma_20) > 0 and len(sma_50) > 0:
            # 이동평균 기울기
            if len(sma_20) >= 5:
                sma_20_slope = (sma_20.iloc[-1] - sma_20.iloc[-5]) / 5
                trend_indicators['sma_20_slope'] = sma_20_slope
            
            if len(sma_50) >= 5:
                sma_50_slope = (sma_50.iloc[-1] - sma_50.iloc[-5]) / 5
                trend_indicators['sma_50_slope'] = sma_50_slope
            
            # 트렌드 방향
            if sma_20.iloc[-1] > sma_50.iloc[-1] and trend_indicators.get('sma_20_slope', 0) > 0:
                trend_indicators['trend'] = 'bullish'
            elif sma_20.iloc[-1] < sma_50.iloc[-1] and trend_indicators.get('sma_20_slope', 0) < 0:
                trend_indicators['trend'] = 'bearish'
            else:
                trend_indicators['trend'] = 'sideways'
        
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
        if 'macd_line' in indicators and 'macd_signal' in indicators:
            if indicators['macd_line'] > indicators['macd_signal']:
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
