#!/usr/bin/env python3
"""
고급 로깅 시스템 모듈
구조화된 로깅 및 로그 관리
"""

import os
import json
import logging
import logging.handlers
import gzip
import shutil
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
import time

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    extra_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

class LogRotator:
    """로그 로테이션 관리자"""
    
    def __init__(self, log_dir: str, max_files: int = 10, max_size_mb: int = 100):
        self.log_dir = Path(log_dir)
        self.max_files = max_files
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # 로그 디렉토리 생성
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rotate(self, file_path: str) -> bool:
        """로테이션 필요 여부 확인"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            return file_size >= self.max_size_bytes
            
        except Exception as e:
            logger.error(f"로테이션 확인 실패: {e}")
            return False
    
    def rotate_file(self, file_path: str) -> str:
        """파일 로테이션"""
        try:
            if not os.path.exists(file_path):
                return file_path
            
            # 새 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(file_path).stem
            extension = Path(file_path).suffix
            rotated_name = f"{base_name}_{timestamp}{extension}"
            rotated_path = self.log_dir / rotated_name
            
            # 파일 이동
            shutil.move(file_path, rotated_path)
            
            # 압축
            self._compress_file(rotated_path)
            
            # 오래된 파일 정리
            self._cleanup_old_files(base_name, extension)
            
            logger.info(f"로그 파일 로테이션 완료: {rotated_path}")
            return str(rotated_path)
            
        except Exception as e:
            logger.error(f"파일 로테이션 실패: {e}")
            return file_path
    
    def _compress_file(self, file_path: Path):
        """파일 압축"""
        try:
            if file_path.suffix == '.gz':
                return  # 이미 압축됨
            
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 원본 파일 삭제
            file_path.unlink()
            
        except Exception as e:
            logger.error(f"파일 압축 실패: {e}")
    
    def _cleanup_old_files(self, base_name: str, extension: str):
        """오래된 파일 정리"""
        try:
            pattern = f"{base_name}_*{extension}.gz"
            files = list(self.log_dir.glob(pattern))
            
            if len(files) > self.max_files:
                # 수정 시간 기준으로 정렬
                files.sort(key=lambda x: x.stat().st_mtime)
                
                # 오래된 파일 삭제
                for file_to_delete in files[:-self.max_files]:
                    file_to_delete.unlink()
                    logger.debug(f"오래된 로그 파일 삭제: {file_to_delete}")
                    
        except Exception as e:
            logger.error(f"오래된 파일 정리 실패: {e}")

class LogFormatter(logging.Formatter):
    """커스텀 로그 포매터"""
    
    def __init__(self, include_extra: bool = True):
        self.include_extra = include_extra
        super().__init__()
    
    def format(self, record):
        """로그 레코드 포맷팅"""
        try:
            # 기본 정보
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                thread_id=record.thread,
                process_id=record.process,
                extra_data={}
            )
            
            # 추가 데이터
            if self.include_extra and hasattr(record, 'extra_data'):
                log_entry.extra_data = record.extra_data
            
            # 예외 정보
            if record.exc_info:
                log_entry.extra_data['exception'] = self.formatException(record.exc_info)
            
            return log_entry.to_json()
            
        except Exception as e:
            # 포맷팅 실패시 기본 포맷 사용
            return super().format(record)

class LogQueueHandler(logging.Handler):
    """큐 기반 로그 핸들러"""
    
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """로그 레코드를 큐에 추가"""
        try:
            self.log_queue.put(record)
        except Exception as e:
            self.handleError(record)

class LogProcessor:
    """로그 처리기"""
    
    def __init__(self, log_dir: str, max_queue_size: int = 10000):
        self.log_dir = Path(log_dir)
        self.max_queue_size = max_queue_size
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self.rotator = LogRotator(log_dir)
        
        # 로그 파일 핸들러들
        self.handlers: Dict[str, logging.FileHandler] = {}
        
        # 처리 스레드
        self.processing = False
        self.process_thread = None
        
        # 통계
        self.stats = {
            'total_logs': 0,
            'by_level': {},
            'by_logger': {},
            'errors': 0
        }
    
    def start_processing(self):
        """로그 처리 시작"""
        try:
            if self.processing:
                return
            
            self.processing = True
            self.process_thread = threading.Thread(target=self._process_logs, daemon=True)
            self.process_thread.start()
            logger.info("로그 처리 시작")
            
        except Exception as e:
            logger.error(f"로그 처리 시작 실패: {e}")
    
    def stop_processing(self):
        """로그 처리 중지"""
        try:
            self.processing = False
            if self.process_thread:
                self.process_thread.join(timeout=5)
            logger.info("로그 처리 중지")
            
        except Exception as e:
            logger.error(f"로그 처리 중지 실패: {e}")
    
    def _process_logs(self):
        """로그 처리 루프"""
        try:
            while self.processing:
                try:
                    # 큐에서 로그 레코드 가져오기
                    record = self.log_queue.get(timeout=1)
                    
                    # 로그 처리
                    self._write_log(record)
                    
                    # 통계 업데이트
                    self._update_stats(record)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"로그 처리 오류: {e}")
                    
        except Exception as e:
            logger.error(f"로그 처리 루프 실패: {e}")
    
    def _write_log(self, record):
        """로그 파일에 쓰기"""
        try:
            # 로그 레벨별 파일 분리
            level_name = record.levelname.lower()
            log_file = self.log_dir / f"{level_name}.log"
            
            # 핸들러 가져오기 또는 생성
            if str(log_file) not in self.handlers:
                handler = logging.FileHandler(log_file, encoding='utf-8')
                handler.setFormatter(LogFormatter())
                self.handlers[str(log_file)] = handler
            
            handler = self.handlers[str(log_file)]
            
            # 로테이션 확인
            if self.rotator.should_rotate(str(log_file)):
                handler.close()
                self.rotator.rotate_file(str(log_file))
                
                # 새 핸들러 생성
                handler = logging.FileHandler(log_file, encoding='utf-8')
                handler.setFormatter(LogFormatter())
                self.handlers[str(log_file)] = handler
            
            # 로그 쓰기
            handler.emit(record)
            
        except Exception as e:
            logger.error(f"로그 쓰기 실패: {e}")
    
    def _update_stats(self, record):
        """통계 업데이트"""
        try:
            self.stats['total_logs'] += 1
            
            # 레벨별 통계
            level = record.levelname
            self.stats['by_level'][level] = self.stats['by_level'].get(level, 0) + 1
            
            # 로거별 통계
            logger_name = record.name
            self.stats['by_logger'][logger_name] = self.stats['by_logger'].get(logger_name, 0) + 1
            
            # 에러 통계
            if record.levelno >= logging.ERROR:
                self.stats['errors'] += 1
                
        except Exception as e:
            logger.error(f"통계 업데이트 실패: {e}")
    
    def get_handler(self) -> LogQueueHandler:
        """큐 핸들러 반환"""
        return LogQueueHandler(self.log_queue)
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()
    
    def clear_stats(self):
        """통계 초기화"""
        self.stats = {
            'total_logs': 0,
            'by_level': {},
            'by_logger': {},
            'errors': 0
        }

class AdvancedLogger:
    """고급 로거 클래스"""
    
    def __init__(self, name: str, log_dir: str = "logs", level: str = "INFO"):
        self.name = name
        self.log_dir = log_dir
        self.level = getattr(logging, level.upper())
        
        # 로그 디렉토리 생성
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 로거 생성
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 로그 처리기 초기화
        self.processor = LogProcessor(log_dir)
        self.processor.start_processing()
        
        # 큐 핸들러 추가
        queue_handler = self.processor.get_handler()
        queue_handler.setLevel(self.level)
        self.logger.addHandler(queue_handler)
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 콘솔에는 WARNING 이상만
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_with_context(self, level: str, message: str, **kwargs):
        """컨텍스트와 함께 로그"""
        try:
            extra_data = kwargs.copy()
            
            # 로그 레벨 확인
            log_level = getattr(logging, level.upper())
            if self.logger.isEnabledFor(log_level):
                # 레코드 생성
                record = self.logger.makeRecord(
                    self.logger.name, log_level, "", 0, message, (), None
                )
                record.extra_data = extra_data
                
                # 로그 처리
                self.logger.handle(record)
                
        except Exception as e:
            print(f"로그 기록 실패: {e}")
    
    def info(self, message: str, **kwargs):
        """INFO 레벨 로그"""
        self.log_with_context("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """WARNING 레벨 로그"""
        self.log_with_context("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """ERROR 레벨 로그"""
        self.log_with_context("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """CRITICAL 레벨 로그"""
        self.log_with_context("CRITICAL", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """DEBUG 레벨 로그"""
        self.log_with_context("DEBUG", message, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.processor.get_stats()
    
    def print_stats(self):
        """통계 출력"""
        try:
            stats = self.get_stats()
            
            print("=" * 60)
            print("📊 로그 통계")
            print("=" * 60)
            
            print(f"📈 총 로그 수: {stats['total_logs']:,}")
            print(f"❌ 에러 수: {stats['errors']:,}")
            
            if stats['total_logs'] > 0:
                error_rate = stats['errors'] / stats['total_logs'] * 100
                print(f"📊 에러율: {error_rate:.2f}%")
            
            print(f"\n📋 레벨별 통계:")
            for level, count in sorted(stats['by_level'].items()):
                print(f"  {level}: {count:,}개")
            
            print(f"\n🏷️ 로거별 통계:")
            for logger_name, count in sorted(stats['by_logger'].items()):
                print(f"  {logger_name}: {count:,}개")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"통계 출력 실패: {e}")
    
    def cleanup(self):
        """리소스 정리"""
        try:
            self.processor.stop_processing()
            logger.info("고급 로거 정리 완료")
        except Exception as e:
            logger.error(f"로거 정리 실패: {e}")

# 전역 로거 매니저
_loggers: Dict[str, AdvancedLogger] = {}

def get_logger(name: str, log_dir: str = "logs", level: str = "INFO") -> AdvancedLogger:
    """로거 가져오기 또는 생성"""
    try:
        if name not in _loggers:
            _loggers[name] = AdvancedLogger(name, log_dir, level)
        return _loggers[name]
    except Exception as e:
        logger.error(f"로거 생성 실패: {e}")
        # 기본 로거 반환
        return AdvancedLogger("default", log_dir, level)

def cleanup_all_loggers():
    """모든 로거 정리"""
    try:
        for logger in _loggers.values():
            logger.cleanup()
        _loggers.clear()
    except Exception as e:
        logger.error(f"로거 정리 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 고급 로깅 시스템 테스트")
    
    # 로거 생성
    test_logger = get_logger("test", "test_logs", "DEBUG")
    
    try:
        # 다양한 로그 테스트
        print("1. 기본 로그 테스트")
        test_logger.info("기본 정보 로그")
        test_logger.warning("경고 로그")
        test_logger.error("에러 로그")
        test_logger.critical("치명적 로그")
        test_logger.debug("디버그 로그")
        
        print("\n2. 컨텍스트 로그 테스트")
        test_logger.info("거래 실행", symbol="BTCUSDT", price=50000, quantity=0.001)
        test_logger.error("API 오류", endpoint="/api/order", status_code=500, response_time=2.5)
        test_logger.warning("잔고 부족", current_balance=100, required_balance=200)
        
        print("\n3. 통계 확인")
        time.sleep(2)  # 로그 처리 대기
        test_logger.print_stats()
        
    finally:
        test_logger.cleanup()
