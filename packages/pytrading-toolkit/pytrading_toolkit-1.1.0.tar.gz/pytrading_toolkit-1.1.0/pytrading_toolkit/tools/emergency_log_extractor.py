#!/usr/bin/env python3
"""
장애 발생 시 관련 로그만 빠르게 추출하는 도구
트레이딩 시스템에서 오류나 장애가 발생했을 때 문제 분석에 필요한 로그만 선별적으로 추출
"""

import os
import sys
import re
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

class EmergencyLogExtractor:
    """장애 시 로그 추출기"""
    
    def __init__(self, log_dir: str = "logs", output_dir: str = "emergency_logs"):
        self.log_dir = Path(log_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 로그 레벨별 색상
        self.level_colors = {
            'ERROR': '🔴',
            'WARNING': '🟡', 
            'INFO': '🔵',
            'DEBUG': '⚪',
            'CRITICAL': '🚨'
        }
        
        # 중요 키워드들
        self.critical_keywords = [
            'error', 'exception', 'traceback', 'failed', 'failure',
            'timeout', 'connection', 'network', 'api', 'auth',
            'balance', 'order', 'trade', 'position', 'risk',
            'memory', 'cpu', 'disk', 'restart', 'crash'
        ]
        
        # 트레이딩 관련 키워드
        self.trading_keywords = [
            'buy', 'sell', 'order', 'trade', 'position', 'balance',
            'profit', 'loss', 'pnl', 'margin', 'leverage', 'stop',
            'limit', 'market', 'filled', 'cancelled', 'rejected'
        ]
        
        # 시스템 관련 키워드
        self.system_keywords = [
            'startup', 'shutdown', 'restart', 'health', 'monitor',
            'websocket', 'api', 'database', 'cache', 'memory',
            'thread', 'process', 'signal', 'timeout', 'retry'
        ]
    
    def find_log_files(self, hours_back: int = 24) -> List[Path]:
        """지정된 시간 범위 내의 로그 파일들을 찾습니다"""
        log_files = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        if not self.log_dir.exists():
            print(f"❌ 로그 디렉토리를 찾을 수 없습니다: {self.log_dir}")
            return log_files
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.is_file():
                # 파일 수정 시간 확인
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime >= cutoff_time:
                    log_files.append(log_file)
        
        # 시간순 정렬
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return log_files
    
    def extract_error_logs(self, log_files: List[Path], 
                          error_types: List[str] = None,
                          include_context: bool = True) -> Dict[str, List[str]]:
        """에러 로그를 추출합니다"""
        if error_types is None:
            error_types = ['ERROR', 'CRITICAL', 'EXCEPTION']
        
        error_logs = {error_type: [] for error_type in error_types}
        
        for log_file in log_files:
            print(f"📖 로그 파일 분석 중: {log_file.name}")
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    for error_type in error_types:
                        if error_type.lower() in line.lower():
                            # 컨텍스트 포함
                            if include_context:
                                context_lines = []
                                # 앞 2줄, 뒤 3줄 포함
                                start = max(0, i - 2)
                                end = min(len(lines), i + 4)
                                
                                for j in range(start, end):
                                    if j == i:
                                        context_lines.append(f"🔴 {lines[j].rstrip()}")
                                    else:
                                        context_lines.append(f"   {lines[j].rstrip()}")
                                
                                error_logs[error_type].extend(context_lines)
                                error_logs[error_type].append("─" * 80)
                            else:
                                error_logs[error_type].append(line.rstrip())
                                
            except Exception as e:
                print(f"⚠️ 로그 파일 읽기 실패: {log_file.name} - {e}")
        
        return error_logs
    
    def extract_trading_logs(self, log_files: List[Path], 
                            time_range: Tuple[datetime, datetime] = None) -> List[str]:
        """트레이딩 관련 로그를 추출합니다"""
        trading_logs = []
        
        for log_file in log_files:
            print(f"📊 트레이딩 로그 분석 중: {log_file.name}")
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # 트레이딩 키워드가 포함된 로그 찾기
                        if any(keyword in line.lower() for keyword in self.trading_keywords):
                            # 시간 범위 체크
                            if time_range:
                                timestamp = self.extract_timestamp(line)
                                if timestamp and (time_range[0] <= timestamp <= time_range[1]):
                                    trading_logs.append(line.rstrip())
                            else:
                                trading_logs.append(line.rstrip())
                                
            except Exception as e:
                print(f"⚠️ 트레이딩 로그 추출 실패: {log_file.name} - {e}")
        
        return trading_logs
    
    def extract_system_logs(self, log_files: List[Path], 
                           hours_back: int = 6) -> List[str]:
        """시스템 상태 관련 로그를 추출합니다"""
        system_logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for log_file in log_files:
            print(f"⚙️ 시스템 로그 분석 중: {log_file.name}")
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # 시스템 키워드가 포함된 로그 찾기
                        if any(keyword in line.lower() for keyword in self.system_keywords):
                            timestamp = self.extract_timestamp(line)
                            if timestamp and timestamp >= cutoff_time:
                                system_logs.append(line.rstrip())
                                
            except Exception as e:
                print(f"⚠️ 시스템 로그 추출 실패: {log_file.name} - {e}")
        
        return system_logs
    
    def extract_timestamp(self, log_line: str) -> Optional[datetime]:
        """로그 라인에서 타임스탬프를 추출합니다"""
        # 일반적인 로그 타임스탬프 패턴들
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # ISO 형식으로 변환 시도
                    if '-' in timestamp_str and ':' in timestamp_str:
                        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    elif '/' in timestamp_str and ':' in timestamp_str:
                        if len(timestamp_str.split('/')[0]) == 4:  # YYYY/MM/DD
                            return datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                        else:  # MM/DD/YYYY
                            return datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    continue
        
        return None
    
    def create_summary_report(self, error_logs: Dict[str, List[str]], 
                             trading_logs: List[str], 
                             system_logs: List[str]) -> str:
        """요약 리포트를 생성합니다"""
        report = []
        report.append("🚨 장애 로그 분석 리포트")
        report.append("=" * 50)
        report.append(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 에러 로그 요약
        total_errors = sum(len(logs) for logs in error_logs.values())
        report.append(f"🔴 에러 로그: {total_errors}건")
        for error_type, logs in error_logs.items():
            if logs:
                report.append(f"  - {error_type}: {len(logs)}건")
        report.append("")
        
        # 트레이딩 로그 요약
        report.append(f"📊 트레이딩 로그: {len(trading_logs)}건")
        report.append("")
        
        # 시스템 로그 요약
        report.append(f"⚙️ 시스템 로그: {len(system_logs)}건")
        report.append("")
        
        # 중요도별 분류
        critical_count = len([log for logs in error_logs.values() for log in logs if 'critical' in log.lower()])
        warning_count = len([log for logs in error_logs.values() for log in logs if 'warning' in log.lower()])
        
        report.append("⚠️ 중요도별 분류:")
        report.append(f"  - 🚨 Critical: {critical_count}건")
        report.append(f"  - 🟡 Warning: {warning_count}건")
        report.append(f"  - 🔴 Error: {total_errors - critical_count - warning_count}건")
        
        return "\n".join(report)
    
    def save_logs(self, error_logs: Dict[str, List[str]], 
                  trading_logs: List[str], 
                  system_logs: List[str],
                  filename_prefix: str = "emergency") -> Dict[str, str]:
        """추출된 로그를 파일로 저장합니다"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_files = {}
        
        # 에러 로그 저장
        for error_type, logs in error_logs.items():
            if logs:
                filename = f"{filename_prefix}_{error_type.lower()}_{timestamp}.log"
                filepath = self.output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {error_type} 로그 - {datetime.now()}\n")
                    f.write(f"# 파일: {filename}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write("\n".join(logs))
                
                saved_files[error_type] = str(filepath)
        
        # 트레이딩 로그 저장
        if trading_logs:
            filename = f"{filename_prefix}_trading_{timestamp}.log"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 트레이딩 로그 - {datetime.now()}\n")
                f.write(f"# 파일: {filename}\n")
                f.write("=" * 80 + "\n\n")
                f.write("\n".join(trading_logs))
            
            saved_files['trading'] = str(filepath)
        
        # 시스템 로그 저장
        if system_logs:
            filename = f"{filename_prefix}_system_{timestamp}.log"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 시스템 로그 - {datetime.now()}\n")
                f.write(f"# 파일: {filename}\n")
                f.write("=" * 80 + "\n\n")
                f.write("\n".join(system_logs))
            
            saved_files['system'] = str(filepath)
        
        # 요약 리포트 저장
        summary = self.create_summary_report(error_logs, trading_logs, system_logs)
        summary_filename = f"{filename_prefix}_summary_{timestamp}.txt"
        summary_filepath = self.output_dir / summary_filename
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        saved_files['summary'] = str(summary_filepath)
        
        return saved_files
    
    def quick_analysis(self, hours_back: int = 6) -> Dict[str, any]:
        """빠른 분석을 수행합니다"""
        print(f"🚀 장애 로그 빠른 분석 시작... (최근 {hours_back}시간)")
        
        # 로그 파일 찾기
        log_files = self.find_log_files(hours_back)
        if not log_files:
            print("❌ 분석할 로그 파일이 없습니다.")
            return {}
        
        print(f"📁 발견된 로그 파일: {len(log_files)}개")
        
        # 에러 로그 추출
        print("🔍 에러 로그 추출 중...")
        error_logs = self.extract_error_logs(log_files)
        
        # 트레이딩 로그 추출
        print("📊 트레이딩 로그 추출 중...")
        trading_logs = self.extract_trading_logs(log_files)
        
        # 시스템 로그 추출
        print("⚙️ 시스템 로그 추출 중...")
        system_logs = self.extract_system_logs(log_files, hours_back)
        
        # 요약 리포트 생성
        summary = self.create_summary_report(error_logs, trading_logs, system_logs)
        print("\n" + summary)
        
        # 파일로 저장
        print("\n💾 로그 파일 저장 중...")
        saved_files = self.save_logs(error_logs, trading_logs, system_logs)
        
        print("\n✅ 분석 완료!")
        for log_type, filepath in saved_files.items():
            print(f"  📄 {log_type}: {filepath}")
        
        return {
            'error_logs': error_logs,
            'trading_logs': trading_logs,
            'system_logs': system_logs,
            'saved_files': saved_files,
            'summary': summary
        }

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='장애 발생 시 로그 추출 도구')
    parser.add_argument('--log-dir', default='logs', help='로그 디렉토리 경로')
    parser.add_argument('--output-dir', default='emergency_logs', help='출력 디렉토리 경로')
    parser.add_argument('--hours', type=int, default=6, help='분석할 시간 범위 (시간)')
    parser.add_argument('--error-types', nargs='+', 
                       default=['ERROR', 'CRITICAL', 'EXCEPTION'],
                       help='추출할 에러 타입들')
    parser.add_argument('--include-context', action='store_true', 
                       help='에러 로그에 컨텍스트 포함')
    
    args = parser.parse_args()
    
    # 로그 추출기 생성
    extractor = EmergencyLogExtractor(args.log_dir, args.output_dir)
    
    try:
        # 빠른 분석 실행
        result = extractor.quick_analysis(args.hours)
        
        if result:
            print(f"\n🎯 분석 완료! 결과는 '{args.output_dir}' 디렉토리에 저장되었습니다.")
        else:
            print("\n❌ 분석에 실패했습니다.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
