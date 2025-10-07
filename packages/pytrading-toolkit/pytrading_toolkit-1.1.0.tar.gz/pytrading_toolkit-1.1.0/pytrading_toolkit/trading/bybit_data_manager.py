#!/usr/bin/env python3
"""
바이비트 데이터 관리 모듈
공통 데이터 관리 로직을 패키지에서 제공
"""

import time
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
from .bybit_trader import BybitTrader

# 성능 최적화 도구들
from ..utils.cache_manager import CacheManager, cached
from ..utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class BybitDataManager:
    """바이비트 데이터 관리 클래스"""
    
    def __init__(self, config_loader, test_mode: bool = True):
        self.config_loader = config_loader
        self.test_mode = test_mode
        self.trader = BybitTrader(config_loader, test_mode)
        
        # 성능 최적화 도구들 초기화
        self.cache = CacheManager(max_size=1000, default_ttl=300)  # 5분 캐시
        self.performance_monitor = PerformanceMonitor()
        self.cache.start_cleanup()
        
        # 캐시 설정
        self.candle_cache = {}
        self.indicator_cache = {}
        self.last_update = {}
        
        # 기본 설정
        self.symbol = "BTCUSDT"
        self.interval = "1"  # 1분봉
        
    def fetch_latest_minute_candle(self) -> Optional[Dict[str, Any]]:
        """최신 1분봉 데이터 조회"""
        try:
            klines = self.trader.get_kline_data(self.symbol, self.interval, 1)
            
            if not klines:
                logger.warning("K라인 데이터가 없습니다")
                return None
            
            # 바이비트 K라인 데이터를 표준 형식으로 변환
            kline = klines[0]
            candle = {
                'timestamp': int(kline[0]),  # 시작 시간
                'open': float(kline[1]),     # 시가
                'high': float(kline[2]),     # 고가
                'low': float(kline[3]),      # 저가
                'close': float(kline[4]),    # 종가
                'volume': float(kline[5]),   # 거래량
                'turnover': float(kline[6])  # 거래대금
            }
            
            # 캐시에 저장
            cache_key = f"{self.symbol}_{self.interval}"
            self.candle_cache[cache_key] = candle
            self.last_update[cache_key] = datetime.now(timezone.utc)
            
            return candle
            
        except Exception as e:
            logger.error(f"1분봉 데이터 조회 실패: {e}")
            return None
    
    def fetch_latest_daily_candle(self, count: int = 1) -> List[Dict[str, Any]]:
        """최신 일봉 데이터 조회"""
        try:
            klines = self.trader.get_kline_data(self.symbol, "D", count)
            
            if not klines:
                logger.warning("일봉 데이터가 없습니다")
                return []
            
            candles = []
            for kline in klines:
                candle = {
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'turnover': float(kline[6])
                }
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            logger.error(f"일봉 데이터 조회 실패: {e}")
            return []
    
    @cached(ttl=10)  # 10초 캐시
    def get_current_price(self) -> Optional[float]:
        """현재 가격 조회 (캐시 적용)"""
        try:
            start_time = time.time()
            price = self.trader.get_ticker_price(self.symbol)
            response_time = time.time() - start_time
            
            # 성능 모니터링
            self.performance_monitor.record_api_call(
                endpoint=f"ticker/{self.symbol}",
                method="GET",
                response_time=response_time,
                status_code=200 if price else 500,
                success=price is not None
            )
            
            return price
        except Exception as e:
            logger.error(f"현재 가격 조회 실패: {e}")
            return None
    
    def calculate_indicators(self, candles: List[Dict[str, Any]], 
                           indicator_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """지표 계산"""
        try:
            if not candles or not indicator_configs:
                return {}
            
            # pandas DataFrame으로 변환
            df = pd.DataFrame(candles)
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['open'] = df['open'].astype(float)
            
            results = {}
            
            for config in indicator_configs:
                ind_type = config['type']
                period = config['period']
                key = f"{ind_type.lower()}_{period}"
                
                try:
                    if ind_type == 'SMA':
                        if len(df) >= period:
                            results[key] = df['close'].rolling(window=period).mean().iloc[-1]
                        else:
                            results[key] = None
                    
                    elif ind_type == 'EMA':
                        if len(df) >= period:
                            results[key] = df['close'].ewm(span=period).mean().iloc[-1]
                        else:
                            results[key] = None
                    
                    elif ind_type == 'PREV_HIGH':
                        if len(df) >= period:
                            results[key] = df['high'].rolling(window=period).max().iloc[-1]
                        else:
                            results[key] = None
                    
                    elif ind_type == 'PREV_LOW':
                        if len(df) >= period:
                            results[key] = df['low'].rolling(window=period).min().iloc[-1]
                        else:
                            results[key] = None
                    
                    else:
                        logger.warning(f"지원하지 않는 지표 타입: {ind_type}")
                        results[key] = None
                
                except Exception as e:
                    logger.error(f"지표 계산 오류 ({ind_type}): {e}")
                    results[key] = None
            
            return results
            
        except Exception as e:
            logger.error(f"지표 계산 실패: {e}")
            return {}
    
    def get_cached_indicators(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """캐시된 지표 조회"""
        return self.indicator_cache.get(cache_key)
    
    def cache_indicators(self, cache_key: str, indicators: Dict[str, Any]):
        """지표 캐시 저장"""
        self.indicator_cache[cache_key] = indicators
    
    def get_cached_candles(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """캐시된 캔들 조회"""
        return self.candle_cache.get(cache_key)
    
    def cache_candles(self, cache_key: str, candles: List[Dict[str, Any]]):
        """캔들 캐시 저장"""
        self.candle_cache[cache_key] = candles
    
    def is_cache_valid(self, cache_key: str, max_age_seconds: int = 60) -> bool:
        """캐시 유효성 검사"""
        if cache_key not in self.last_update:
            return False
        
        last_update = self.last_update[cache_key]
        age = (datetime.now(timezone.utc) - last_update).total_seconds()
        
        return age < max_age_seconds
    
    def clear_cache(self):
        """캐시 초기화"""
        self.candle_cache.clear()
        self.indicator_cache.clear()
        self.last_update.clear()
        logger.info("데이터 캐시 초기화 완료")
    
    def get_market_info(self) -> Dict[str, Any]:
        """시장 정보 조회"""
        try:
            current_price = self.get_current_price()
            latest_candle = self.fetch_latest_minute_candle()
            
            return {
                'symbol': self.symbol,
                'current_price': current_price,
                'latest_candle': latest_candle,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"시장 정보 조회 실패: {e}")
            return {}
