"""시간 관련 유틸리티 함수들"""

from datetime import datetime, timezone, timedelta
import pytz

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

def get_utc_now():
    """현재 UTC 시간 반환"""
    return datetime.now(timezone.utc)

def get_kst_now():
    """현재 KST 시간 반환"""
    return datetime.now(KST)

def utc_to_kst(utc_dt):
    """UTC 시간을 KST로 변환"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(KST)

def kst_to_utc(kst_dt):
    """KST 시간을 UTC로 변환"""
    if kst_dt.tzinfo is None:
        kst_dt = KST.localize(kst_dt)
    return kst_dt.astimezone(timezone.utc)

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """datetime을 문자열로 포맷"""
    return dt.strftime(format_str)

def parse_datetime(dt_str, format_str="%Y-%m-%d %H:%M:%S"):
    """문자열을 datetime으로 파싱"""
    return datetime.strptime(dt_str, format_str)

def get_market_open_time():
    """한국 주식시장 개장 시간 (9:00 KST)"""
    now = get_kst_now()
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    return market_open

def get_market_close_time():
    """한국 주식시장 폐장 시간 (15:30 KST)"""
    now = get_kst_now()
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_close

def is_market_hours():
    """현재가 한국 주식시장 시간인지 확인"""
    now = get_kst_now()
    open_time = get_market_open_time()
    close_time = get_market_close_time()
    
    # 주말 제외
    if now.weekday() >= 5:  # 토요일(5), 일요일(6)
        return False
    
    return open_time <= now <= close_time

def sleep_until_market_open():
    """다음 시장 개장까지의 초 수 반환"""
    now = get_kst_now()
    open_time = get_market_open_time()
    
    # 이미 개장 시간이 지났으면 다음 날
    if now >= open_time:
        open_time += timedelta(days=1)
    
    # 주말이면 월요일까지
    while open_time.weekday() >= 5:
        open_time += timedelta(days=1)
    
    return (open_time - now).total_seconds()

def get_candle_time(timestamp, interval_minutes=1):
    """타임스탬프를 캔들 시간으로 변환"""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # 분 단위로 정규화
    minutes = (dt.minute // interval_minutes) * interval_minutes
    return dt.replace(minute=minutes, second=0, microsecond=0)
