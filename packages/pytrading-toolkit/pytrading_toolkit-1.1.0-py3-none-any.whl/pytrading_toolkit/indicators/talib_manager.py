"""
TA-Lib 기반 기술적 지표 계산 모듈
업계 표준 TA-Lib 라이브러리를 사용하여 고성능 지표 계산
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

class TALibIndicatorManager:
    """TA-Lib 기반 기술적 지표 관리 클래스"""
    
    def __init__(self):
        self.default_indicators = [
            {'type': 'SMA', 'period': 20},
            {'type': 'SMA', 'period': 50},
            {'type': 'EMA', 'period': 12},
            {'type': 'EMA', 'period': 26},
            {'type': 'RSI', 'period': 14},
            {'type': 'MACD', 'fast': 12, 'slow': 26, 'signal': 9},
            {'type': 'BB', 'period': 20, 'std': 2},
            {'type': 'STOCH', 'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3},
            {'type': 'ATR', 'period': 14},
            {'type': 'CCI', 'period': 14},
            {'type': 'WILLR', 'period': 14},
            {'type': 'ADX', 'period': 14},
            {'type': 'AROON', 'period': 14},
            {'type': 'PREV_HIGH', 'period': 1},
            {'type': 'PREV_LOW', 'period': 1}
        ]
    
    def get_default_config(self) -> List[Dict[str, Any]]:
        """기본 지표 설정 반환"""
        return self.default_indicators.copy()
    
    def _prepare_data(self, candles: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """캔들 데이터를 TA-Lib 형식으로 변환"""
        try:
            if not candles or len(candles) < 2:
                raise ValueError("캔들 데이터 부족")
            
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
            
            # 필수 컬럼 확인
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"필수 컬럼 누락: {col}")
            
            # 데이터 타입 변환 및 NaN 제거
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=required_columns)
            
            if len(df) < 2:
                raise ValueError("유효한 캔들 데이터 부족")
            
            # numpy 배열로 변환
            open_prices = df['open'].values.astype(np.float64)
            high_prices = df['high'].values.astype(np.float64)
            low_prices = df['low'].values.astype(np.float64)
            close_prices = df['close'].values.astype(np.float64)
            volumes = df['volume'].values.astype(np.float64)
            
            return open_prices, high_prices, low_prices, close_prices, volumes
            
        except Exception as e:
            logger.error(f"데이터 준비 실패: {e}")
            raise

def calculate_indicators_talib(candles: List[Dict], indicator_configs: List[Dict]) -> Dict[str, float]:
    """TA-Lib 기반 기술 지표 계산
    
    Args:
        candles: 캔들 데이터 리스트 [{'open', 'high', 'low', 'close', 'volume', 'timestamp'}, ...]
        indicator_configs: 지표 설정 리스트
        
    Returns:
        계산된 지표 딕셔너리
    """
    try:
        manager = TALibIndicatorManager()
        open_prices, high_prices, low_prices, close_prices, volumes = manager._prepare_data(candles)
        
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
                    if data_length >= period + 1:
                        rsi = talib.RSI(close_prices, timeperiod=period)
                        result = rsi[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'rsi_{period}'] = float(result)
                
                # MACD (Moving Average Convergence Divergence)
                elif indicator_type == 'MACD':
                    fast = config.get('fast', 12)
                    slow = config.get('slow', 26)
                    signal = config.get('signal', 9)
                    if data_length >= slow + signal:
                        macd_line, macd_signal, macd_histogram = talib.MACD(
                            close_prices, 
                            fastperiod=fast, 
                            slowperiod=slow, 
                            signalperiod=signal
                        )
                        
                        if not np.isnan(macd_line[-1]) and not np.isinf(macd_line[-1]):
                            indicators['macd_line'] = float(macd_line[-1])
                        if not np.isnan(macd_signal[-1]) and not np.isinf(macd_signal[-1]):
                            indicators['macd_signal'] = float(macd_signal[-1])
                        if not np.isnan(macd_histogram[-1]) and not np.isinf(macd_histogram[-1]):
                            indicators['macd_histogram'] = float(macd_histogram[-1])
                
                # 볼린저 밴드
                elif indicator_type == 'BB':
                    period = config.get('period', 20)
                    std = config.get('std', 2)
                    if data_length >= period:
                        bb_upper, bb_middle, bb_lower = talib.BBANDS(
                            close_prices, 
                            timeperiod=period, 
                            nbdevup=std, 
                            nbdevdn=std, 
                            matype=0
                        )
                        
                        if not np.isnan(bb_upper[-1]) and not np.isinf(bb_upper[-1]):
                            indicators['bb_upper'] = float(bb_upper[-1])
                        if not np.isnan(bb_middle[-1]) and not np.isinf(bb_middle[-1]):
                            indicators['bb_middle'] = float(bb_middle[-1])
                        if not np.isnan(bb_lower[-1]) and not np.isinf(bb_lower[-1]):
                            indicators['bb_lower'] = float(bb_lower[-1])
                        
                        # 볼린저 밴드 폭
                        if (all(not np.isnan(x) and not np.isinf(x) for x in [bb_upper[-1], bb_lower[-1], bb_middle[-1]]) 
                            and bb_middle[-1] > 0):
                            bb_width = (bb_upper[-1] - bb_lower[-1]) / bb_middle[-1] * 100
                            indicators['bb_width'] = float(bb_width)
                
                # 스토캐스틱 오실레이터
                elif indicator_type == 'STOCH':
                    fastk_period = config.get('fastk_period', 14)
                    slowk_period = config.get('slowk_period', 3)
                    slowd_period = config.get('slowd_period', 3)
                    if data_length >= fastk_period + slowk_period + slowd_period:
                        stoch_k, stoch_d = talib.STOCH(
                            high_prices, 
                            low_prices, 
                            close_prices,
                            fastk_period=fastk_period,
                            slowk_period=slowk_period,
                            slowd_period=slowd_period
                        )
                        
                        if not np.isnan(stoch_k[-1]) and not np.isinf(stoch_k[-1]):
                            indicators['stoch_k'] = float(stoch_k[-1])
                        if not np.isnan(stoch_d[-1]) and not np.isinf(stoch_d[-1]):
                            indicators['stoch_d'] = float(stoch_d[-1])
                
                # ATR (Average True Range)
                elif indicator_type == 'ATR':
                    period = config.get('period', 14)
                    if data_length >= period:
                        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)
                        result = atr[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'atr_{period}'] = float(result)
                
                # CCI (Commodity Channel Index)
                elif indicator_type == 'CCI':
                    period = config.get('period', 14)
                    if data_length >= period:
                        cci = talib.CCI(high_prices, low_prices, close_prices, timeperiod=period)
                        result = cci[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'cci_{period}'] = float(result)
                
                # Williams %R
                elif indicator_type == 'WILLR':
                    period = config.get('period', 14)
                    if data_length >= period:
                        willr = talib.WILLR(high_prices, low_prices, close_prices, timeperiod=period)
                        result = willr[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'willr_{period}'] = float(result)
                
                # ADX (Average Directional Index)
                elif indicator_type == 'ADX':
                    period = config.get('period', 14)
                    if data_length >= period * 2:
                        adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=period)
                        result = adx[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'adx_{period}'] = float(result)
                
                # Aroon
                elif indicator_type == 'AROON':
                    period = config.get('period', 14)
                    if data_length >= period:
                        aroon_down, aroon_up = talib.AROON(high_prices, low_prices, timeperiod=period)
                        
                        if not np.isnan(aroon_down[-1]) and not np.isinf(aroon_down[-1]):
                            indicators[f'aroon_down_{period}'] = float(aroon_down[-1])
                        if not np.isnan(aroon_up[-1]) and not np.isinf(aroon_up[-1]):
                            indicators[f'aroon_up_{period}'] = float(aroon_up[-1])
                        
                        # Aroon Oscillator
                        aroon_oscillator = aroon_up - aroon_down
                        if not np.isnan(aroon_oscillator[-1]) and not np.isinf(aroon_oscillator[-1]):
                            indicators[f'aroon_oscillator_{period}'] = float(aroon_oscillator[-1])
                
                # 이전 고가/저가
                elif indicator_type == 'PREV_HIGH':
                    period = config.get('period', 1)
                    if data_length > period:
                        prev_high = high_prices[-(period + 1)]
                        if not np.isnan(prev_high) and not np.isinf(prev_high):
                            if period == 1:
                                indicators['prev_high_1'] = float(prev_high)
                            else:
                                indicators[f'prev_high_{period}'] = float(prev_high)
                
                elif indicator_type == 'PREV_LOW':
                    period = config.get('period', 1)
                    if data_length > period:
                        prev_low = low_prices[-(period + 1)]
                        if not np.isnan(prev_low) and not np.isinf(prev_low):
                            if period == 1:
                                indicators['prev_low_1'] = float(prev_low)
                            else:
                                indicators[f'prev_low_{period}'] = float(prev_low)
                
                # 거래량 지표
                elif indicator_type == 'VOLUME_SMA':
                    period = config.get('period', 20)
                    if data_length >= period:
                        volume_sma = talib.SMA(volumes, timeperiod=period)
                        result = volume_sma[-1]
                        if not np.isnan(result) and not np.isinf(result) and result > 0:
                            indicators[f'volume_sma_{period}'] = float(result)
                            
                            # 현재 거래량과 평균 거래량 비율
                            current_volume = volumes[-1]
                            if not np.isnan(current_volume) and not np.isinf(current_volume):
                                volume_ratio = current_volume / result
                                indicators[f'volume_ratio_{period}'] = float(volume_ratio)
                
                # OBV (On Balance Volume)
                elif indicator_type == 'OBV':
                    if data_length >= 2:
                        obv = talib.OBV(close_prices, volumes)
                        result = obv[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators['obv'] = float(result)
                
                # MFI (Money Flow Index)
                elif indicator_type == 'MFI':
                    period = config.get('period', 14)
                    if data_length >= period:
                        mfi = talib.MFI(high_prices, low_prices, close_prices, volumes, timeperiod=period)
                        result = mfi[-1]
                        if not np.isnan(result) and not np.isinf(result):
                            indicators[f'mfi_{period}'] = float(result)
                
            except Exception as e:
                logger.warning(f"지표 계산 실패 ({indicator_type}): {e}")
                continue
        
        logger.debug(f"TA-Lib 지표 계산 완료: {len(indicators)}개")
        return indicators
        
    except Exception as e:
        logger.error(f"TA-Lib 지표 계산 예외: {e}")
        return {}

def calculate_advanced_indicators_talib(candles: List[Dict]) -> Dict[str, Any]:
    """고급 TA-Lib 지표 계산"""
    try:
        manager = TALibIndicatorManager()
        open_prices, high_prices, low_prices, close_prices, volumes = manager._prepare_data(candles)
        
        advanced_indicators = {}
        data_length = len(close_prices)
        
        # 패턴 인식 (Pattern Recognition)
        if data_length >= 60:  # 충분한 데이터 필요
            # Doji 패턴
            doji = talib.CDLDOJI(open_prices, high_prices, low_prices, close_prices)
            advanced_indicators['doji'] = int(doji[-1]) if not np.isnan(doji[-1]) else 0
            
            # Hammer 패턴
            hammer = talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)
            advanced_indicators['hammer'] = int(hammer[-1]) if not np.isnan(hammer[-1]) else 0
            
            # Engulfing 패턴
            engulfing = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
            advanced_indicators['engulfing'] = int(engulfing[-1]) if not np.isnan(engulfing[-1]) else 0
        
        # 피벗 포인트
        if data_length >= 20:
            # 피벗 포인트 계산 (일반적인 방법)
            recent_highs = high_prices[-20:]
            recent_lows = low_prices[-20:]
            recent_closes = close_prices[-20:]
            
            pivot_high = np.max(recent_highs)
            pivot_low = np.min(recent_lows)
            pivot_close = recent_closes[-1]
            
            advanced_indicators['pivot_high'] = float(pivot_high)
            advanced_indicators['pivot_low'] = float(pivot_low)
            advanced_indicators['pivot_close'] = float(pivot_close)
            
            # 피벗 레벨 계산
            advanced_indicators['pivot_point'] = float((pivot_high + pivot_low + pivot_close) / 3)
            advanced_indicators['resistance_1'] = float(2 * advanced_indicators['pivot_point'] - pivot_low)
            advanced_indicators['support_1'] = float(2 * advanced_indicators['pivot_point'] - pivot_high)
        
        # 변동성 지표
        if data_length >= 20:
            # Historical Volatility
            returns = np.diff(np.log(close_prices))
            if len(returns) >= 20:
                hv = np.std(returns[-20:]) * np.sqrt(252) * 100  # 연간 변동률
                advanced_indicators['historical_volatility'] = float(hv)
        
        return advanced_indicators
        
    except Exception as e:
        logger.error(f"고급 TA-Lib 지표 계산 예외: {e}")
        return {}

def get_market_sentiment_talib(indicators: Dict[str, float]) -> Dict[str, Any]:
    """TA-Lib 지표 기반 시장 심리 분석"""
    try:
        sentiment = {'score': 0, 'signals': [], 'strength': 'neutral'}
        
        # RSI 기반 신호
        if 'rsi_14' in indicators:
            rsi = indicators['rsi_14']
            if rsi < 30:
                sentiment['score'] += 2
                sentiment['signals'].append('RSI 과매도 (강력)')
                sentiment['strength'] = 'strong_bullish'
            elif rsi < 40:
                sentiment['score'] += 1
                sentiment['signals'].append('RSI 과매도')
            elif rsi > 70:
                sentiment['score'] -= 2
                sentiment['signals'].append('RSI 과매수 (강력)')
                sentiment['strength'] = 'strong_bearish'
            elif rsi > 60:
                sentiment['score'] -= 1
                sentiment['signals'].append('RSI 과매수')
        
        # MACD 기반 신호
        if 'macd_line' in indicators and 'macd_signal' in indicators:
            macd_diff = indicators['macd_line'] - indicators['macd_signal']
            if macd_diff > 0:
                sentiment['score'] += 1
                sentiment['signals'].append('MACD 상승신호')
            else:
                sentiment['score'] -= 1
                sentiment['signals'].append('MACD 하락신호')
        
        # 스토캐스틱 기반 신호
        if 'stoch_k' in indicators and 'stoch_d' in indicators:
            if indicators['stoch_k'] < 20 and indicators['stoch_d'] < 20:
                sentiment['score'] += 1.5
                sentiment['signals'].append('스토캐스틱 과매도')
            elif indicators['stoch_k'] > 80 and indicators['stoch_d'] > 80:
                sentiment['score'] -= 1.5
                sentiment['signals'].append('스토캐스틱 과매수')
        
        # 볼린저 밴드 기반 신호
        if 'bb_upper' in indicators and 'bb_lower' in indicators and 'bb_middle' in indicators:
            current_price = indicators.get('close', 0)
            if current_price > 0:
                if current_price <= indicators['bb_lower']:
                    sentiment['score'] += 1
                    sentiment['signals'].append('볼린저 밴드 하단 터치')
                elif current_price >= indicators['bb_upper']:
                    sentiment['score'] -= 1
                    sentiment['signals'].append('볼린저 밴드 상단 터치')
        
        # 거래량 기반 신호
        if 'volume_ratio_20' in indicators:
            volume_ratio = indicators['volume_ratio_20']
            if volume_ratio > 2.0:
                sentiment['signals'].append('거래량 폭증')
            elif volume_ratio > 1.5:
                sentiment['signals'].append('거래량 급증')
            elif volume_ratio < 0.5:
                sentiment['signals'].append('거래량 급감')
        
        # 종합 판단
        if sentiment['score'] >= 3:
            sentiment['overall'] = 'strong_bullish'
        elif sentiment['score'] >= 1:
            sentiment['overall'] = 'bullish'
        elif sentiment['score'] <= -3:
            sentiment['overall'] = 'strong_bearish'
        elif sentiment['score'] <= -1:
            sentiment['overall'] = 'bearish'
        else:
            sentiment['overall'] = 'neutral'
        
        return sentiment
        
    except Exception as e:
        logger.error(f"시장 심리 분석 예외: {e}")
        return {'score': 0, 'signals': [], 'overall': 'neutral', 'strength': 'neutral'}

def calculate_trend_indicators_talib(candles: List[Dict]) -> Dict[str, Any]:
    """TA-Lib 기반 트렌드 지표 계산"""
    try:
        manager = TALibIndicatorManager()
        open_prices, high_prices, low_prices, close_prices, volumes = manager._prepare_data(candles)
        
        trend_indicators = {}
        data_length = len(close_prices)
        
        if data_length >= 50:
            # 이동평균 기울기 계산
            sma_20 = talib.SMA(close_prices, timeperiod=20)
            sma_50 = talib.SMA(close_prices, timeperiod=50)
            
            if len(sma_20) >= 5 and not np.isnan(sma_20[-1]):
                sma_20_slope = (sma_20[-1] - sma_20[-5]) / 5
                trend_indicators['sma_20_slope'] = float(sma_20_slope)
            
            if len(sma_50) >= 5 and not np.isnan(sma_50[-1]):
                sma_50_slope = (sma_50[-1] - sma_50[-5]) / 5
                trend_indicators['sma_50_slope'] = float(sma_50_slope)
            
            # 트렌드 방향 판단
            if not np.isnan(sma_20[-1]) and not np.isnan(sma_50[-1]):
                if sma_20[-1] > sma_50[-1] and trend_indicators.get('sma_20_slope', 0) > 0:
                    trend_indicators['trend'] = 'bullish'
                elif sma_20[-1] < sma_50[-1] and trend_indicators.get('sma_20_slope', 0) < 0:
                    trend_indicators['trend'] = 'bearish'
                else:
                    trend_indicators['trend'] = 'sideways'
            
            # ADX로 트렌드 강도 측정
            if data_length >= 28:
                adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=14)
                if not np.isnan(adx[-1]):
                    trend_indicators['trend_strength'] = float(adx[-1])
                    
                    if adx[-1] > 50:
                        trend_indicators['trend_quality'] = 'strong'
                    elif adx[-1] > 25:
                        trend_indicators['trend_quality'] = 'moderate'
                    else:
                        trend_indicators['trend_quality'] = 'weak'
        
        return trend_indicators
        
    except Exception as e:
        logger.error(f"트렌드 지표 계산 예외: {e}")
        return {}

def get_talib_version() -> str:
    """TA-Lib 버전 정보 반환"""
    try:
        return talib.__version__
    except:
        return "Unknown"
