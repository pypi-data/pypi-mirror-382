"""
공통 유틸리티 함수들
업비트와 바이비트 시스템에서 공통으로 사용
"""

import re
from datetime import datetime, timezone
from typing import Any, Optional, Union

def format_timestamp(dt: Optional[datetime] = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """타임스탬프 포맷팅
    
    Args:
        dt: datetime 객체 (None이면 현재 시간)
        format_str: 포맷 문자열
        
    Returns:
        포맷된 시간 문자열
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    return dt.strftime(format_str)

def format_currency(amount: float, currency: str = "KRW", decimals: int = 0) -> str:
    """통화 포맷팅
    
    Args:
        amount: 금액
        currency: 통화 코드
        decimals: 소수점 자리수
        
    Returns:
        포맷된 통화 문자열
    """
    try:
        if currency.upper() in ["KRW", "USDC", "USDT"]:
            return f"{amount:,.{decimals}f} {currency.upper()}"
        else:
            # BTC, ETH 등 암호화폐
            return f"{amount:.8f} {currency.upper()}"
    except:
        return f"{amount} {currency}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """퍼센트 포맷팅
    
    Args:
        value: 값 (0.01 = 1%)
        decimals: 소수점 자리수
        
    Returns:
        포맷된 퍼센트 문자열
    """
    try:
        percentage = value * 100
        return f"{percentage:+.{decimals}f}%"
    except:
        return f"{value}%"

def safe_float(value: Any, default: float = 0.0) -> float:
    """안전한 float 변환
    
    Args:
        value: 변환할 값
        default: 기본값
        
    Returns:
        float 값
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            # 쉼표 제거 후 변환
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """안전한 int 변환
    
    Args:
        value: 변환할 값
        default: 기본값
        
    Returns:
        int 값
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            # 쉼표 제거 후 변환
            value = value.replace(',', '')
        return int(float(value))  # float을 거쳐서 변환 (소수점 있는 문자열 처리)
    except (ValueError, TypeError):
        return default

def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검사
    
    Args:
        api_key: API 키 문자열
        
    Returns:
        유효 여부
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # 기본값인지 확인
    default_patterns = [
        'your-',
        'example-',
        'test-',
        'placeholder'
    ]
    
    api_key_lower = api_key.lower()
    for pattern in default_patterns:
        if pattern in api_key_lower:
            return False
    
    # 최소 길이 확인
    if len(api_key) < 10:
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """파일명 안전화
    
    Args:
        filename: 원본 파일명
        
    Returns:
        안전한 파일명
    """
    # 위험한 문자 제거
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 연속된 언더스코어 정리
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    # 앞뒤 공백 및 언더스코어 제거
    sanitized = sanitized.strip(' _')
    
    # 빈 문자열 방지
    if not sanitized:
        sanitized = 'untitled'
    
    return sanitized

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """문자열 자르기
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        suffix: 생략 표시
        
    Returns:
        자른 문자열
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_timeframe(timeframe: str) -> int:
    """시간 프레임 파싱 (분 단위로 변환)
    
    Args:
        timeframe: "1m", "5m", "1h", "1d" 등
        
    Returns:
        분 단위 시간
    """
    try:
        timeframe = timeframe.lower().strip()
        
        if timeframe.endswith('m'):
            return int(timeframe[:-1])
        elif timeframe.endswith('h'):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith('d'):
            return int(timeframe[:-1]) * 60 * 24
        else:
            # 숫자만 있으면 분으로 가정
            return int(timeframe)
    except:
        return 1  # 기본값: 1분

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """퍼센트 변화율 계산
    
    Args:
        old_value: 이전 값
        new_value: 새로운 값
        
    Returns:
        변화율 (0.01 = 1%)
    """
    try:
        if old_value == 0:
            return 0.0
        
        return (new_value - old_value) / old_value
    except:
        return 0.0

def round_to_precision(value: float, precision: int) -> float:
    """정밀도에 맞춰 반올림
    
    Args:
        value: 값
        precision: 소수점 자리수
        
    Returns:
        반올림된 값
    """
    try:
        return round(value, precision)
    except:
        return value

def is_market_hours(market: str = "crypto") -> bool:
    """시장 운영 시간 확인
    
    Args:
        market: 시장 타입 ("crypto", "stock", "forex")
        
    Returns:
        운영 중 여부
    """
    if market.lower() == "crypto":
        # 암호화폐는 24/7
        return True
    
    # 다른 시장은 기본적으로 운영 중으로 가정
    # 실제로는 더 복잡한 로직이 필요
    return True

def get_memory_usage() -> dict:
    """메모리 사용량 확인
    
    Returns:
        메모리 정보 딕셔너리
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # 물리 메모리
            'vms': memory_info.vms,  # 가상 메모리
            'percent': process.memory_percent(),  # 퍼센트
        }
    except ImportError:
        return {}
    except Exception:
        return {}

def cleanup_old_files(directory: str, days: int = 7, pattern: str = "*.log"):
    """오래된 파일 정리
    
    Args:
        directory: 디렉토리 경로
        days: 보관 일수
        pattern: 파일 패턴
    """
    try:
        import os
        import glob
        from pathlib import Path
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"오래된 파일 삭제: {file_path}")
                    except OSError:
                        pass
    except Exception as e:
        print(f"파일 정리 중 오류: {e}")

def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """예외 발생시 재시도 데코레이터
    
    Args:
        max_retries: 최대 재시도 횟수
        delay: 재시도 간격(초)
    """
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay)
                        continue
                    else:
                        raise last_exception
            
        return wrapper
    return decorator
