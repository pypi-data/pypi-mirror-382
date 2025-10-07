#!/usr/bin/env python3
"""
로그 분석 도구 모듈
로그 파일 분석 및 통계 생성
"""

import os
import json
import gzip
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd

@dataclass
class LogAnalysisResult:
    """로그 분석 결과"""
    total_logs: int
    time_range: Tuple[datetime, datetime]
    level_distribution: Dict[str, int]
    logger_distribution: Dict[str, int]
    error_patterns: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    trends: Dict[str, List[Tuple[datetime, int]]]

class LogAnalyzer:
    """로그 분석기"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_files = self._find_log_files()
    
    def _find_log_files(self) -> List[Path]:
        """로그 파일 찾기"""
        try:
            log_files = []
            
            # 일반 로그 파일
            for pattern in ["*.log", "*.log.gz"]:
                log_files.extend(self.log_dir.glob(pattern))
            
            return sorted(log_files, key=lambda x: x.stat().st_mtime)
            
        except Exception as e:
            print(f"로그 파일 찾기 실패: {e}")
            return []
    
    def _read_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """로그 파일 읽기"""
        try:
            logs = []
            
            # 파일 열기
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # JSON 로그 파싱
            for line_num, line in enumerate(lines, 1):
                try:
                    log_entry = json.loads(line.strip())
                    log_entry['file_path'] = str(file_path)
                    log_entry['line_number'] = line_num
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    # JSON이 아닌 경우 기본 파싱
                    logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'UNKNOWN',
                        'message': line.strip(),
                        'file_path': str(file_path),
                        'line_number': line_num
                    })
            
            return logs
            
        except Exception as e:
            print(f"로그 파일 읽기 실패: {file_path}: {e}")
            return []
    
    def analyze_logs(self, hours: int = 24) -> LogAnalysisResult:
        """로그 분석"""
        try:
            # 시간 범위 설정
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            all_logs = []
            
            # 모든 로그 파일 읽기
            for log_file in self.log_files:
                logs = self._read_log_file(log_file)
                
                # 시간 필터링
                filtered_logs = []
                for log in logs:
                    try:
                        log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                        if start_time <= log_time <= end_time:
                            filtered_logs.append(log)
                    except (ValueError, KeyError):
                        # 시간 파싱 실패시 포함
                        filtered_logs.append(log)
                
                all_logs.extend(filtered_logs)
            
            if not all_logs:
                return LogAnalysisResult(
                    total_logs=0,
                    time_range=(start_time, end_time),
                    level_distribution={},
                    logger_distribution={},
                    error_patterns=[],
                    performance_metrics={},
                    trends={}
                )
            
            # 분석 수행
            level_dist = self._analyze_level_distribution(all_logs)
            logger_dist = self._analyze_logger_distribution(all_logs)
            error_patterns = self._analyze_error_patterns(all_logs)
            performance_metrics = self._analyze_performance_metrics(all_logs)
            trends = self._analyze_trends(all_logs, start_time, end_time)
            
            # 시간 범위 계산
            timestamps = [datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) 
                         for log in all_logs if 'timestamp' in log]
            actual_time_range = (min(timestamps), max(timestamps)) if timestamps else (start_time, end_time)
            
            return LogAnalysisResult(
                total_logs=len(all_logs),
                time_range=actual_time_range,
                level_distribution=level_dist,
                logger_distribution=logger_dist,
                error_patterns=error_patterns,
                performance_metrics=performance_metrics,
                trends=trends
            )
            
        except Exception as e:
            print(f"로그 분석 실패: {e}")
            return LogAnalysisResult(
                total_logs=0,
                time_range=(start_time, end_time),
                level_distribution={},
                logger_distribution={},
                error_patterns=[],
                performance_metrics={},
                trends={}
            )
    
    def _analyze_level_distribution(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """레벨별 분포 분석"""
        try:
            level_counter = Counter()
            for log in logs:
                level = log.get('level', 'UNKNOWN')
                level_counter[level] += 1
            
            return dict(level_counter)
            
        except Exception as e:
            print(f"레벨 분포 분석 실패: {e}")
            return {}
    
    def _analyze_logger_distribution(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """로거별 분포 분석"""
        try:
            logger_counter = Counter()
            for log in logs:
                logger_name = log.get('logger_name', 'UNKNOWN')
                logger_counter[logger_name] += 1
            
            return dict(logger_counter)
            
        except Exception as e:
            print(f"로거 분포 분석 실패: {e}")
            return {}
    
    def _analyze_error_patterns(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """에러 패턴 분석"""
        try:
            error_patterns = []
            error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL']]
            
            # 에러 메시지 패턴 분석
            error_messages = [log.get('message', '') for log in error_logs]
            message_counter = Counter(error_messages)
            
            for message, count in message_counter.most_common(10):
                if count > 1:  # 2회 이상 발생한 에러만
                    error_patterns.append({
                        'message': message,
                        'count': count,
                        'percentage': count / len(error_logs) * 100
                    })
            
            return error_patterns
            
        except Exception as e:
            print(f"에러 패턴 분석 실패: {e}")
            return []
    
    def _analyze_performance_metrics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """성능 메트릭 분석"""
        try:
            metrics = {
                'api_calls': 0,
                'avg_response_time': 0,
                'slow_requests': 0,
                'error_rate': 0
            }
            
            api_logs = [log for log in logs if 'api' in log.get('message', '').lower()]
            error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL']]
            
            metrics['api_calls'] = len(api_logs)
            metrics['error_rate'] = len(error_logs) / len(logs) * 100 if logs else 0
            
            # 응답 시간 분석
            response_times = []
            for log in api_logs:
                extra_data = log.get('extra_data', {})
                if 'response_time' in extra_data:
                    response_times.append(extra_data['response_time'])
            
            if response_times:
                metrics['avg_response_time'] = sum(response_times) / len(response_times)
                metrics['slow_requests'] = len([rt for rt in response_times if rt > 5.0])
            
            return metrics
            
        except Exception as e:
            print(f"성능 메트릭 분석 실패: {e}")
            return {}
    
    def _analyze_trends(self, logs: List[Dict[str, Any]], 
                       start_time: datetime, end_time: datetime) -> Dict[str, List[Tuple[datetime, int]]]:
        """트렌드 분석"""
        try:
            trends = {
                'total_logs': [],
                'error_logs': [],
                'warning_logs': []
            }
            
            # 시간별 그룹화
            time_groups = defaultdict(int)
            error_groups = defaultdict(int)
            warning_groups = defaultdict(int)
            
            for log in logs:
                try:
                    log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                    hour_key = log_time.replace(minute=0, second=0, microsecond=0)
                    
                    time_groups[hour_key] += 1
                    
                    if log.get('level') in ['ERROR', 'CRITICAL']:
                        error_groups[hour_key] += 1
                    elif log.get('level') == 'WARNING':
                        warning_groups[hour_key] += 1
                        
                except (ValueError, KeyError):
                    continue
            
            # 트렌드 데이터 생성
            trends['total_logs'] = sorted(time_groups.items())
            trends['error_logs'] = sorted(error_groups.items())
            trends['warning_logs'] = sorted(warning_groups.items())
            
            return trends
            
        except Exception as e:
            print(f"트렌드 분석 실패: {e}")
            return {}
    
    def search_logs(self, query: str, level: Optional[str] = None, 
                   hours: int = 24) -> List[Dict[str, Any]]:
        """로그 검색"""
        try:
            # 시간 범위 설정
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            results = []
            
            # 모든 로그 파일 검색
            for log_file in self.log_files:
                logs = self._read_log_file(log_file)
                
                for log in logs:
                    # 시간 필터링
                    try:
                        log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                        if not (start_time <= log_time <= end_time):
                            continue
                    except (ValueError, KeyError):
                        continue
                    
                    # 레벨 필터링
                    if level and log.get('level') != level:
                        continue
                    
                    # 메시지 검색
                    message = log.get('message', '')
                    if query.lower() in message.lower():
                        results.append(log)
            
            # 시간순 정렬
            results.sort(key=lambda x: x.get('timestamp', ''))
            
            return results
            
        except Exception as e:
            print(f"로그 검색 실패: {e}")
            return []
    
    def generate_report(self, hours: int = 24) -> str:
        """분석 보고서 생성"""
        try:
            analysis = self.analyze_logs(hours)
            
            report = []
            report.append("=" * 80)
            report.append("📊 로그 분석 보고서")
            report.append("=" * 80)
            
            # 기본 정보
            report.append(f"📅 분석 기간: {analysis.time_range[0]} ~ {analysis.time_range[1]}")
            report.append(f"📈 총 로그 수: {analysis.total_logs:,}개")
            report.append("")
            
            # 레벨별 분포
            if analysis.level_distribution:
                report.append("📋 레벨별 분포:")
                for level, count in sorted(analysis.level_distribution.items()):
                    percentage = count / analysis.total_logs * 100
                    report.append(f"  {level}: {count:,}개 ({percentage:.1f}%)")
                report.append("")
            
            # 로거별 분포
            if analysis.logger_distribution:
                report.append("🏷️ 로거별 분포:")
                for logger_name, count in sorted(analysis.logger_distribution.items()):
                    percentage = count / analysis.total_logs * 100
                    report.append(f"  {logger_name}: {count:,}개 ({percentage:.1f}%)")
                report.append("")
            
            # 에러 패턴
            if analysis.error_patterns:
                report.append("❌ 주요 에러 패턴:")
                for i, pattern in enumerate(analysis.error_patterns[:5], 1):
                    report.append(f"  {i}. {pattern['message'][:50]}...")
                    report.append(f"     발생 횟수: {pattern['count']}회 ({pattern['percentage']:.1f}%)")
                report.append("")
            
            # 성능 메트릭
            if analysis.performance_metrics:
                report.append("⚡ 성능 메트릭:")
                metrics = analysis.performance_metrics
                report.append(f"  API 호출 수: {metrics.get('api_calls', 0):,}회")
                report.append(f"  평균 응답 시간: {metrics.get('avg_response_time', 0):.2f}초")
                report.append(f"  느린 요청: {metrics.get('slow_requests', 0):,}회")
                report.append(f"  에러율: {metrics.get('error_rate', 0):.2f}%")
                report.append("")
            
            # 트렌드
            if analysis.trends.get('total_logs'):
                report.append("📈 시간별 트렌드 (최근 5시간):")
                recent_trends = analysis.trends['total_logs'][-5:]
                for time_point, count in recent_trends:
                    report.append(f"  {time_point.strftime('%H:%M')}: {count}개")
                report.append("")
            
            report.append("=" * 80)
            
            return "\n".join(report)
            
        except Exception as e:
            return f"보고서 생성 실패: {e}"
    
    def export_to_csv(self, output_file: str, hours: int = 24):
        """로그를 CSV로 내보내기"""
        try:
            analysis = self.analyze_logs(hours)
            
            # 시간 범위 설정
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            all_logs = []
            
            # 모든 로그 파일 읽기
            for log_file in self.log_files:
                logs = self._read_log_file(log_file)
                
                # 시간 필터링
                filtered_logs = []
                for log in logs:
                    try:
                        log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                        if start_time <= log_time <= end_time:
                            filtered_logs.append(log)
                    except (ValueError, KeyError):
                        filtered_logs.append(log)
                
                all_logs.extend(filtered_logs)
            
            if not all_logs:
                print("내보낼 로그가 없습니다")
                return
            
            # DataFrame 생성
            df = pd.DataFrame(all_logs)
            
            # 필요한 컬럼만 선택
            columns = ['timestamp', 'level', 'logger_name', 'message', 'module', 'function']
            available_columns = [col for col in columns if col in df.columns]
            df = df[available_columns]
            
            # CSV 저장
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"로그가 CSV로 내보내졌습니다: {output_file}")
            
        except Exception as e:
            print(f"CSV 내보내기 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 로그 분석 도구 테스트")
    
    # 로그 분석기 초기화
    analyzer = LogAnalyzer("test_logs")
    
    # 분석 수행
    print("1. 로그 분석")
    analysis = analyzer.analyze_logs(hours=24)
    print(f"총 로그 수: {analysis.total_logs}")
    print(f"레벨 분포: {analysis.level_distribution}")
    
    # 검색 테스트
    print("\n2. 로그 검색")
    results = analyzer.search_logs("error", level="ERROR", hours=24)
    print(f"에러 로그 검색 결과: {len(results)}개")
    
    # 보고서 생성
    print("\n3. 분석 보고서")
    report = analyzer.generate_report(hours=24)
    print(report)
