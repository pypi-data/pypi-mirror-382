#!/usr/bin/env python3
"""
캐시 관리 모듈
효율적인 데이터 캐싱 시스템
"""

import time
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass
from collections import OrderedDict
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """캐시 엔트리"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at

class CacheManager:
    """캐시 관리 클래스"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
        # 통계
        self.hits = 0
        self.misses = 0
        
        # 정리 스레드
        self.cleanup_thread = None
        self.cleanup_interval = 60  # 1분마다 정리
        self.running = False
    
    def start_cleanup(self):
        """캐시 정리 스레드 시작"""
        try:
            if self.running:
                return
            
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            logger.info("캐시 정리 스레드 시작")
            
        except Exception as e:
            logger.error(f"캐시 정리 스레드 시작 실패: {e}")
    
    def stop_cleanup(self):
        """캐시 정리 스레드 중지"""
        try:
            self.running = False
            if self.cleanup_thread:
                self.cleanup_thread.join(timeout=5)
            logger.info("캐시 정리 스레드 중지")
            
        except Exception as e:
            logger.error(f"캐시 정리 스레드 중지 실패: {e}")
    
    def _cleanup_loop(self):
        """캐시 정리 루프"""
        try:
            while self.running:
                self._cleanup_expired()
                time.sleep(self.cleanup_interval)
        except Exception as e:
            logger.error(f"캐시 정리 루프 오류: {e}")
    
    def _cleanup_expired(self):
        """만료된 캐시 정리"""
        try:
            with self.lock:
                current_time = datetime.now(timezone.utc)
                expired_keys = []
                
                for key, entry in self.cache.items():
                    if entry.expires_at and entry.expires_at <= current_time:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.debug(f"만료된 캐시 {len(expired_keys)}개 정리됨")
                    
        except Exception as e:
            logger.error(f"캐시 정리 실패: {e}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        try:
            # 인자들을 문자열로 변환하여 키 생성
            key_data = {
                'args': args,
                'kwargs': sorted(kwargs.items()) if kwargs else {}
            }
            key_str = json.dumps(key_data, sort_keys=True, default=str)
            return hashlib.md5(key_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"캐시 키 생성 실패: {e}")
            return str(hash(str(args) + str(kwargs)))
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        try:
            with self.lock:
                if key not in self.cache:
                    self.misses += 1
                    return None
                
                entry = self.cache[key]
                
                # 만료 확인
                if entry.expires_at and entry.expires_at <= datetime.now(timezone.utc):
                    del self.cache[key]
                    self.misses += 1
                    return None
                
                # 접근 통계 업데이트
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                
                # LRU 업데이트 (맨 뒤로 이동)
                self.cache.move_to_end(key)
                
                self.hits += 1
                return entry.value
                
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 값 저장"""
        try:
            with self.lock:
                current_time = datetime.now(timezone.utc)
                expires_at = None
                
                if ttl is not None:
                    expires_at = current_time + timedelta(seconds=ttl)
                elif self.default_ttl > 0:
                    expires_at = current_time + timedelta(seconds=self.default_ttl)
                
                # 새 엔트리 생성
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=current_time,
                    expires_at=expires_at
                )
                
                # 기존 키가 있으면 제거
                if key in self.cache:
                    del self.cache[key]
                
                # 캐시 크기 확인
                if len(self.cache) >= self.max_size:
                    # 가장 오래된 항목 제거 (LRU)
                    self.cache.popitem(last=False)
                
                # 새 엔트리 추가
                self.cache[key] = entry
                return True
                
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        try:
            with self.lock:
                if key in self.cache:
                    del self.cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False
    
    def clear(self):
        """캐시 전체 삭제"""
        try:
            with self.lock:
                self.cache.clear()
                self.hits = 0
                self.misses = 0
                logger.info("캐시 전체 삭제됨")
        except Exception as e:
            logger.error(f"캐시 전체 삭제 실패: {e}")
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """캐시에서 조회하거나 함수 실행 후 저장"""
        try:
            # 캐시에서 조회
            value = self.get(key)
            if value is not None:
                return value
            
            # 함수 실행
            value = func(*args, **kwargs)
            
            # 캐시에 저장
            self.set(key, value, ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"캐시 get_or_set 실패: {e}")
            # 캐시 실패시 함수만 실행
            return func(*args, **kwargs)
    
    def cached(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """캐시 데코레이터"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                try:
                    # 캐시 키 생성
                    if key_func:
                        cache_key = key_func(*args, **kwargs)
                    else:
                        cache_key = self._generate_key(func.__name__, *args, **kwargs)
                    
                    return self.get_or_set(cache_key, func, ttl, *args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"캐시 데코레이터 실행 실패: {e}")
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        try:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {}
    
    def get_entries(self) -> List[Dict[str, Any]]:
        """캐시 엔트리 목록 반환"""
        try:
            with self.lock:
                entries = []
                for key, entry in self.cache.items():
                    entries.append({
                        "key": key,
                        "created_at": entry.created_at.isoformat(),
                        "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                        "access_count": entry.access_count,
                        "last_accessed": entry.last_accessed.isoformat(),
                        "size": len(str(entry.value)) if entry.value else 0
                    })
                return entries
        except Exception as e:
            logger.error(f"캐시 엔트리 목록 조회 실패: {e}")
            return []
    
    def print_cache_status(self):
        """캐시 상태 출력"""
        try:
            stats = self.get_stats()
            
            print("=" * 60)
            print("💾 캐시 상태")
            print("=" * 60)
            
            print(f"📊 크기: {stats['size']}/{stats['max_size']}")
            print(f"🎯 히트율: {stats['hit_rate']:.1%}")
            print(f"📈 총 요청: {stats['total_requests']}회")
            print(f"✅ 히트: {stats['hits']}회")
            print(f"❌ 미스: {stats['misses']}회")
            
            if stats['size'] > 0:
                print(f"\n📋 캐시 엔트리 (최대 10개):")
                entries = self.get_entries()
                for i, entry in enumerate(entries[:10], 1):
                    print(f"  {i}. {entry['key'][:20]}...")
                    print(f"     생성: {entry['created_at']}")
                    print(f"     접근: {entry['access_count']}회")
                    print(f"     크기: {entry['size']} bytes")
                    print()
            
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"캐시 상태 출력 실패: {e}")

# 전역 캐시 매니저
_global_cache = CacheManager()

def get_global_cache() -> CacheManager:
    """전역 캐시 매니저 반환"""
    return _global_cache

def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """전역 캐시 데코레이터"""
    return _global_cache.cached(ttl, key_func)

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 캐시 관리 테스트")
    
    # 캐시 매니저 초기화
    cache = CacheManager(max_size=5, default_ttl=10)
    cache.start_cleanup()
    
    try:
        # 기본 캐시 테스트
        print("1. 기본 캐시 테스트")
        cache.set("test1", "value1", ttl=5)
        cache.set("test2", "value2", ttl=10)
        
        print(f"test1 조회: {cache.get('test1')}")
        print(f"test2 조회: {cache.get('test2')}")
        
        # 데코레이터 테스트
        print("\n2. 데코레이터 테스트")
        
        @cache.cached(ttl=5)
        def expensive_function(n):
            print(f"expensive_function({n}) 실행됨")
            return n * n
        
        print(f"expensive_function(5): {expensive_function(5)}")
        print(f"expensive_function(5): {expensive_function(5)}")  # 캐시에서 조회
        print(f"expensive_function(3): {expensive_function(3)}")
        
        # 통계 출력
        print("\n3. 캐시 통계")
        cache.print_cache_status()
        
        # 만료 테스트
        print("\n4. 만료 테스트 (5초 대기)")
        time.sleep(6)
        print(f"test1 조회 (만료됨): {cache.get('test1')}")
        print(f"test2 조회 (유효함): {cache.get('test2')}")
        
    finally:
        cache.stop_cleanup()
