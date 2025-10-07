#!/usr/bin/env python3
"""
비동기 처리 관리 모듈
효율적인 비동기 작업 관리
"""

import asyncio
import threading
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable, Coroutine
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

logger = logging.getLogger(__name__)

@dataclass
class AsyncTask:
    """비동기 작업"""
    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class AsyncManager:
    """비동기 처리 관리 클래스"""
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.running_tasks: Dict[str, AsyncTask] = {}
        self.completed_tasks: Dict[str, AsyncTask] = {}
        self.lock = threading.RLock()
        
        # 작업 처리 스레드
        self.worker_threads = []
        self.running = False
        
        # 통계
        self.total_tasks = 0
        self.completed_tasks_count = 0
        self.failed_tasks_count = 0
    
    def start(self):
        """비동기 매니저 시작"""
        try:
            if self.running:
                logger.warning("이미 실행 중입니다")
                return
            
            self.running = True
            
            # 워커 스레드 시작
            for i in range(self.max_workers):
                thread = threading.Thread(target=self._worker_loop, daemon=True)
                thread.start()
                self.worker_threads.append(thread)
            
            logger.info(f"비동기 매니저 시작 (워커: {self.max_workers}개)")
            
        except Exception as e:
            logger.error(f"비동기 매니저 시작 실패: {e}")
    
    def stop(self, timeout: int = 30):
        """비동기 매니저 중지"""
        try:
            self.running = False
            
            # 워커 스레드 종료 대기
            for thread in self.worker_threads:
                thread.join(timeout=timeout)
            
            # 실행기 종료
            self.executor.shutdown(wait=True)
            
            logger.info("비동기 매니저 중지됨")
            
        except Exception as e:
            logger.error(f"비동기 매니저 중지 실패: {e}")
    
    def _worker_loop(self):
        """워커 스레드 루프"""
        try:
            while self.running:
                try:
                    # 작업 대기 (1초 타임아웃)
                    priority, task = self.task_queue.get(timeout=1)
                    
                    # 작업 실행
                    self._execute_task(task)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"워커 루프 오류: {e}")
                    
        except Exception as e:
            logger.error(f"워커 루프 실패: {e}")
    
    def _execute_task(self, task: AsyncTask):
        """작업 실행"""
        try:
            with self.lock:
                task.started_at = datetime.now(timezone.utc)
                self.running_tasks[task.task_id] = task
            
            # 작업 실행
            result = task.func(*task.args, **task.kwargs)
            
            # 성공 처리
            with self.lock:
                task.completed_at = datetime.now(timezone.utc)
                task.result = result
                self.completed_tasks[task.task_id] = task
                self.completed_tasks_count += 1
                
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
            
            logger.debug(f"작업 완료: {task.task_id}")
            
        except Exception as e:
            # 실패 처리
            with self.lock:
                task.completed_at = datetime.now(timezone.utc)
                task.error = e
                self.completed_tasks[task.task_id] = task
                self.failed_tasks_count += 1
                
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
            
            logger.error(f"작업 실패: {task.task_id} - {e}")
    
    def submit_task(self, func: Callable, *args, priority: int = 0, **kwargs) -> str:
        """작업 제출"""
        try:
            task_id = f"task_{int(time.time() * 1000)}_{id(func)}"
            
            task = AsyncTask(
                task_id=task_id,
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority
            )
            
            # 큐에 추가
            self.task_queue.put((priority, task))
            
            with self.lock:
                self.total_tasks += 1
            
            logger.debug(f"작업 제출: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"작업 제출 실패: {e}")
            return ""
    
    def submit_async_task(self, coro: Coroutine, priority: int = 0) -> str:
        """비동기 작업 제출"""
        try:
            def async_wrapper():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(coro)
                finally:
                    loop.close()
            
            return self.submit_task(async_wrapper, priority=priority)
            
        except Exception as e:
            logger.error(f"비동기 작업 제출 실패: {e}")
            return ""
    
    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """작업 결과 조회"""
        try:
            start_time = time.time()
            
            while True:
                with self.lock:
                    if task_id in self.completed_tasks:
                        task = self.completed_tasks[task_id]
                        if task.error:
                            raise task.error
                        return task.result
                
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"작업 {task_id} 타임아웃")
                
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"작업 결과 조회 실패: {e}")
            raise
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """작업 완료 대기"""
        try:
            start_time = time.time()
            
            while True:
                with self.lock:
                    if task_id in self.completed_tasks:
                        return True
                
                if timeout and (time.time() - start_time) > timeout:
                    return False
                
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"작업 대기 실패: {e}")
            return False
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        try:
            with self.lock:
                if task_id in self.running_tasks:
                    # 실행 중인 작업은 취소할 수 없음 (단순히 제거)
                    del self.running_tasks[task_id]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"작업 취소 실패: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """작업 상태 조회"""
        try:
            with self.lock:
                if task_id in self.running_tasks:
                    return "running"
                elif task_id in self.completed_tasks:
                    task = self.completed_tasks[task_id]
                    return "failed" if task.error else "completed"
                else:
                    return "not_found"
                    
        except Exception as e:
            logger.error(f"작업 상태 조회 실패: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        try:
            with self.lock:
                return {
                    "total_tasks": self.total_tasks,
                    "running_tasks": len(self.running_tasks),
                    "completed_tasks": self.completed_tasks_count,
                    "failed_tasks": self.failed_tasks_count,
                    "queue_size": self.task_queue.qsize(),
                    "max_workers": self.max_workers,
                    "max_queue_size": self.max_queue_size
                }
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def clear_completed_tasks(self):
        """완료된 작업 정리"""
        try:
            with self.lock:
                self.completed_tasks.clear()
                logger.info("완료된 작업 정리됨")
        except Exception as e:
            logger.error(f"완료된 작업 정리 실패: {e}")
    
    def print_status(self):
        """상태 출력"""
        try:
            stats = self.get_stats()
            
            print("=" * 60)
            print("⚡ 비동기 처리 상태")
            print("=" * 60)
            
            print(f"📊 총 작업: {stats['total_tasks']}개")
            print(f"🏃 실행 중: {stats['running_tasks']}개")
            print(f"✅ 완료: {stats['completed_tasks']}개")
            print(f"❌ 실패: {stats['failed_tasks']}개")
            print(f"📋 대기 중: {stats['queue_size']}개")
            print(f"👥 워커: {stats['max_workers']}개")
            
            if stats['total_tasks'] > 0:
                success_rate = stats['completed_tasks'] / stats['total_tasks']
                print(f"📈 성공률: {success_rate:.1%}")
            
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"상태 출력 실패: {e}")

# 전역 비동기 매니저
_global_async_manager = AsyncManager()

def get_global_async_manager() -> AsyncManager:
    """전역 비동기 매니저 반환"""
    return _global_async_manager

def submit_task(func: Callable, *args, priority: int = 0, **kwargs) -> str:
    """전역 비동기 매니저에 작업 제출"""
    return _global_async_manager.submit_task(func, *args, priority=priority, **kwargs)

def submit_async_task(coro: Coroutine, priority: int = 0) -> str:
    """전역 비동기 매니저에 비동기 작업 제출"""
    return _global_async_manager.submit_async_task(coro, priority=priority)

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 비동기 처리 테스트")
    
    # 비동기 매니저 초기화
    async_manager = AsyncManager(max_workers=2)
    async_manager.start()
    
    try:
        # 테스트 함수들
        def slow_function(n, delay=1):
            print(f"slow_function({n}) 시작")
            time.sleep(delay)
            result = n * n
            print(f"slow_function({n}) 완료: {result}")
            return result
        
        def fast_function(n):
            print(f"fast_function({n}) 실행")
            return n + 1
        
        # 작업 제출
        print("1. 작업 제출 테스트")
        task1 = async_manager.submit_task(slow_function, 5, delay=2, priority=1)
        task2 = async_manager.submit_task(fast_function, 10, priority=2)
        task3 = async_manager.submit_task(slow_function, 3, delay=1, priority=1)
        
        print(f"제출된 작업: {task1}, {task2}, {task3}")
        
        # 상태 확인
        print("\n2. 상태 확인")
        async_manager.print_status()
        
        # 결과 대기
        print("\n3. 결과 대기")
        try:
            result1 = async_manager.get_task_result(task1, timeout=5)
            print(f"task1 결과: {result1}")
        except TimeoutError:
            print("task1 타임아웃")
        
        try:
            result2 = async_manager.get_task_result(task2, timeout=5)
            print(f"task2 결과: {result2}")
        except TimeoutError:
            print("task2 타임아웃")
        
        # 최종 상태
        print("\n4. 최종 상태")
        async_manager.print_status()
        
    finally:
        async_manager.stop()
