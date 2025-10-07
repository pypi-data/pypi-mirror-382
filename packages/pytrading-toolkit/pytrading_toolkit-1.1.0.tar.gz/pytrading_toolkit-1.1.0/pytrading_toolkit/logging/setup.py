"""
공통 로깅 설정 모듈
업비트와 바이비트 시스템에서 공통으로 사용
"""

import logging
import logging.handlers
import os
from datetime import datetime, timezone
from typing import Optional

def setup_logger(system_name: str, log_dir: Optional[str] = None, 
                 level: str = "INFO", max_bytes: int = 100*1024*1024,
                 backup_count: int = 30, instance_info: Optional[dict] = None) -> logging.Logger:
    """공통 로깅 시스템 설정
    
    Args:
        system_name: 시스템 이름 (upbit, bybit 등)
        log_dir: 로그 디렉토리 경로
        level: 로그 레벨
        max_bytes: 최대 로그 파일 크기
        backup_count: 백업 파일 개수
        instance_info: 인스턴스 정보 (name, type, user_id 등)
        
    Returns:
        설정된 로거
    """
    
    # 인스턴스 정보가 있으면 로그 포맷에 추가
    if instance_info:
        instance_name = instance_info.get('name', 'unknown')
        instance_type = instance_info.get('type', 'unknown')
        user_id = instance_info.get('user_id', 'unknown')
        
        # 인스턴스 정보가 포함된 로그 포맷
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s:%(instance)s:%(user)s] - %(levelname)s - %(message)s'
        )
        
        # 인스턴스 정보를 로그 레코드에 추가
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.instance = instance_name
            record.user = user_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    else:
        # 기존 로그 포맷
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # 로그 디렉토리 설정
    if log_dir is None:
        # 현재 작업 디렉토리에서 logs 폴더 생성
        log_dir = os.path.join(os.getcwd(), 'logs')
    
    # 로그 디렉토리 생성
    try:
        os.makedirs(log_dir, exist_ok=True)
        print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] 📁 로그 디렉토리: {log_dir}")
    except PermissionError:
        # 권한이 없으면 현재 디렉토리에 생성
        log_dir = os.path.join(os.getcwd(), 'logs')
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 로그 디렉토리를 현재 위치에 생성: {log_dir}")
        except PermissionError:
            # 그래도 안되면 /tmp 사용
            log_dir = f'/tmp/{system_name}-trader-logs'
            os.makedirs(log_dir, exist_ok=True)
            print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 로그 디렉토리를 임시 위치에 생성: {log_dir}")
    except Exception as e:
        # 최후의 수단으로 /tmp 사용
        log_dir = f'/tmp/{system_name}-trader-logs'
        os.makedirs(log_dir, exist_ok=True)
        print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 로그 디렉토리 생성 실패, 임시 위치 사용: {log_dir}")
    
    # 로그 파일명 생성 (날짜별 + 인스턴스 구분)
    current_date = datetime.now(timezone.utc).strftime('%Y%m%d')
    if instance_info and instance_info.get('name'):
        instance_name = instance_info['name']
        log_file = os.path.join(log_dir, f'{instance_name}_trading_system_{current_date}.log')
    else:
        log_file = os.path.join(log_dir, f'{system_name}_trading_system_{current_date}.log')
    
    # 파일 핸들러 설정 (회전식)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 새 핸들러 추가
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # 시스템별 로거 반환
    logger = logging.getLogger(system_name)
    
    return logger

def setup_module_logger(module_name: str, parent_logger: Optional[logging.Logger] = None) -> logging.Logger:
    """모듈별 로거 설정
    
    Args:
        module_name: 모듈 이름
        parent_logger: 부모 로거
        
    Returns:
        모듈 로거
    """
    if parent_logger:
        logger_name = f"{parent_logger.name}.{module_name}"
    else:
        logger_name = module_name
    
    return logging.getLogger(logger_name)

class TradeLogger:
    """거래 전용 로거 클래스"""
    
    def __init__(self, system_name: str, log_dir: Optional[str] = None):
        self.system_name = system_name
        self.logger = setup_logger(system_name, log_dir)
    
    def log_trade_signal(self, signal_type: str, side: str, price: float, conditions: dict):
        """거래 신호 로그"""
        self.logger.info(f"거래 신호 발생", extra={
            'signal_type': signal_type,
            'side': side,
            'price': price,
            'conditions': conditions,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def log_order_placed(self, order_id: str, side: str, price: float, amount: float):
        """주문 실행 로그"""
        self.logger.info(f"주문 실행", extra={
            'order_id': order_id,
            'side': side,
            'price': price,
            'amount': amount,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def log_order_filled(self, order_id: str, side: str, filled_price: float, filled_amount: float):
        """주문 체결 로그"""
        self.logger.info(f"주문 체결", extra={
            'order_id': order_id,
            'side': side,
            'filled_price': filled_price,
            'filled_amount': filled_amount,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def log_balance_update(self, balances: dict):
        """잔고 업데이트 로그"""
        self.logger.info(f"잔고 업데이트", extra={
            'balances': balances,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def log_error(self, error_type: str, error_message: str, function_name: str = ""):
        """에러 로그"""
        self.logger.error(f"{error_type}: {error_message}", extra={
            'error_type': error_type,
            'function_name': function_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def log_system_event(self, event_type: str, details: dict):
        """시스템 이벤트 로그"""
        self.logger.info(f"시스템 이벤트: {event_type}", extra={
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

def create_performance_logger(system_name: str) -> logging.Logger:
    """성능 모니터링 전용 로거"""
    logger = logging.getLogger(f"{system_name}.performance")
    
    # 성능 로그는 별도 파일에 저장
    current_date = datetime.now(timezone.utc).strftime('%Y%m%d')
    perf_log_file = f"logs/{system_name}_performance_{current_date}.log"
    
    # 성능 로그 핸들러
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    
    # 성능 로그 포맷 (더 간단하게)
    perf_formatter = logging.Formatter('%(asctime)s - %(message)s')
    perf_handler.setFormatter(perf_formatter)
    
    logger.addHandler(perf_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def log_function_performance(func):
    """함수 성능 측정 데코레이터"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 성능 로그
            perf_logger = logging.getLogger("performance")
            perf_logger.info(f"{func.__name__}: {execution_time:.4f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 에러와 함께 성능 로그
            perf_logger = logging.getLogger("performance")
            perf_logger.error(f"{func.__name__}: {execution_time:.4f}s (ERROR: {e})")
            
            raise
    
    return wrapper
