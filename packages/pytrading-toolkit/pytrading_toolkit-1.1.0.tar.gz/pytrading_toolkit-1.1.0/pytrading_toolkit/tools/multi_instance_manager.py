#!/usr/bin/env python3
"""
멀티 인스턴스 트레이더 관리 도구
여러 거래소와 사용자의 트레이더 인스턴스를 통합 관리
"""

import os
import sys
import json
import yaml
import time
import subprocess
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

class MultiInstanceManager:
    """멀티 인스턴스 트레이더 관리자"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.trader_dir = Path(__file__).parent.parent
        self.instances = {}
        self.load_instances()
    
    def load_instances(self):
        """설정 파일에서 인스턴스 정보 로드"""
        print("🔍 인스턴스 설정 파일 검색 중...")
        
        # 업비트 인스턴스 검색
        upbit_dir = self.trader_dir / "app" / "upbit"
        if (upbit_dir / "env.yaml").exists():
            try:
                with open(upbit_dir / "env.yaml", 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if 'instance' in config:
                        instance_info = config['instance']
                        instance_name = instance_info.get('name', 'upbit_unknown')
                        self.instances[instance_name] = {
                            'type': 'upbit',
                            'path': str(upbit_dir),
                            'config': config,
                            'status': 'unknown'
                        }
                        print(f"✅ 업비트 인스턴스 발견: {instance_name}")
            except Exception as e:
                print(f"⚠️ 업비트 설정 파일 읽기 실패: {e}")
        
        # 바이비트 인스턴스 검색
        bybit_dir = self.trader_dir / "app" / "bybit"
        if (bybit_dir / "env.yaml").exists():
            try:
                with open(bybit_dir / "env.yaml", 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if 'instance' in config:
                        instance_info = config['instance']
                        instance_name = instance_info.get('name', 'bybit_unknown')
                        self.instances[instance_name] = {
                            'type': 'bybit',
                            'path': str(bybit_dir),
                            'config': config,
                            'status': 'unknown'
                        }
                        print(f"✅ 바이비트 인스턴스 발견: {instance_name}")
            except Exception as e:
                print(f"⚠️ 바이비트 설정 파일 읽기 실패: {e}")
        
        print(f"📊 총 {len(self.instances)}개 인스턴스 발견")
    
    def check_instance_status(self, instance_name: str) -> str:
        """인스턴스 상태 확인"""
        if instance_name not in self.instances:
            return 'not_found'
        
        instance = self.instances[instance_name]
        instance_path = Path(instance['path'])
        
        # PID 파일 확인
        pid_file = instance_path / f"{instance['type']}-trader.pid"
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    if psutil.pid_exists(pid):
                        # 프로세스가 실제로 main.py를 실행하고 있는지 확인
                        try:
                            process = psutil.Process(pid)
                            cmdline = ' '.join(process.cmdline())
                            if 'main.py' in cmdline:
                                return 'running'
                            else:
                                return 'pid_mismatch'
                        except:
                            return 'pid_mismatch'
                    else:
                        return 'pid_dead'
            except:
                return 'pid_invalid'
        
        return 'stopped'
    
    def update_all_statuses(self):
        """모든 인스턴스 상태 업데이트"""
        for instance_name in self.instances:
            self.instances[instance_name]['status'] = self.check_instance_status(instance_name)
    
    def start_instance(self, instance_name: str) -> bool:
        """인스턴스 시작"""
        if instance_name not in self.instances:
            print(f"❌ 인스턴스를 찾을 수 없습니다: {instance_name}")
            return False
        
        instance = self.instances[instance_name]
        current_status = self.check_instance_status(instance_name)
        
        if current_status == 'running':
            print(f"⚠️ {instance_name}은 이미 실행 중입니다")
            return True
        
        # 리소스 사용량 확인
        if not self._check_system_resources():
            print(f"❌ 시스템 리소스 부족으로 {instance_name} 시작 불가")
            return False
        
        print(f"🚀 {instance_name} 시작 중...")
        
        try:
            # start_trader.sh 실행
            start_script = Path(instance['path']) / "start_trader.sh"
            if start_script.exists():
                result = subprocess.run(
                    [str(start_script)],
                    cwd=instance['path'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✅ {instance_name} 시작 성공")
                    # 상태 업데이트 대기
                    time.sleep(3)
                    self.update_all_statuses()
                    return True
                else:
                    print(f"❌ {instance_name} 시작 실패")
                    print(f"에러: {result.stderr}")
                    return False
            else:
                print(f"❌ 시작 스크립트를 찾을 수 없습니다: {start_script}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {instance_name} 시작 시간 초과")
            return False
        except Exception as e:
            print(f"❌ {instance_name} 시작 중 오류: {e}")
            return False
    
    def _check_system_resources(self) -> bool:
        """시스템 리소스 확인"""
        try:
            # 메모리 사용량 확인
            memory = psutil.virtual_memory()
            if memory.percent > 85:  # 메모리 사용률 85% 초과 시
                print(f"⚠️ 메모리 사용률이 높습니다: {memory.percent:.1f}%")
                return False
            
            # CPU 사용량 확인
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:  # CPU 사용률 90% 초과 시
                print(f"⚠️ CPU 사용률이 높습니다: {cpu_percent:.1f}%")
                return False
            
            return True
        except Exception as e:
            print(f"⚠️ 리소스 확인 실패: {e}")
            return True  # 확인 실패 시 허용
    
    def stop_instance(self, instance_name: str) -> bool:
        """인스턴스 중지"""
        if instance_name not in self.instances:
            print(f"❌ 인스턴스를 찾을 수 없습니다: {instance_name}")
            return False
        
        instance = self.instances[instance_name]
        current_status = self.check_instance_status(instance_name)
        
        if current_status == 'stopped':
            print(f"⚠️ {instance_name}은 이미 중지되어 있습니다")
            return True
        
        print(f"🛑 {instance_name} 중지 중...")
        
        try:
            # stop_trader.sh 실행
            stop_script = Path(instance['path']) / "stop_trader.sh"
            if stop_script.exists():
                result = subprocess.run(
                    [str(stop_script)],
                    cwd=instance['path'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✅ {instance_name} 중지 성공")
                    # 상태 업데이트 대기
                    time.sleep(2)
                    self.update_all_statuses()
                    return True
                else:
                    print(f"❌ {instance_name} 중지 실패")
                    print(f"에러: {result.stderr}")
                    return False
            else:
                print(f"❌ 중지 스크립트를 찾을 수 없습니다: {stop_script}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {instance_name} 중지 시간 초과")
            return False
        except Exception as e:
            print(f"❌ {instance_name} 중지 중 오류: {e}")
            return False
    
    def restart_instance(self, instance_name: str) -> bool:
        """인스턴스 재시작"""
        print(f"🔄 {instance_name} 재시작 중...")
        
        if self.stop_instance(instance_name):
            time.sleep(2)  # 중지 완료 대기
            return self.start_instance(instance_name)
        
        return False
    
    def show_status(self):
        """모든 인스턴스 상태 표시"""
        self.update_all_statuses()
        
        print("\n" + "="*80)
        print("📊 멀티 인스턴스 트레이더 상태")
        print("="*80)
        
        if not self.instances:
            print("❌ 등록된 인스턴스가 없습니다")
            return
        
        # 상태별 그룹화
        status_groups = {
            'running': [],
            'stopped': [],
            'error': []
        }
        
        for instance_name, instance in self.instances.items():
            status = instance['status']
            if status == 'running':
                status_groups['running'].append(instance_name)
            elif status == 'stopped':
                status_groups['stopped'].append(instance_name)
            else:
                status_groups['error'].append(instance_name)
        
        # 실행 중인 인스턴스
        if status_groups['running']:
            print(f"\n🟢 실행 중 ({len(status_groups['running'])}개):")
            for instance_name in status_groups['running']:
                instance = self.instances[instance_name]
                config = instance['config']
                instance_info = config.get('instance', {})
                print(f"  • {instance_name}")
                print(f"    └─ 타입: {instance_info.get('type', 'N/A')}")
                print(f"    └─ 사용자: {instance_info.get('user_id', 'N/A')}")
                print(f"    └─ 설명: {instance_info.get('description', 'N/A')}")
        
        # 중지된 인스턴스
        if status_groups['stopped']:
            print(f"\n🔴 중지됨 ({len(status_groups['stopped'])}개):")
            for instance_name in status_groups['stopped']:
                instance = self.instances[instance_name]
                config = instance['config']
                instance_info = config.get('instance', {})
                print(f"  • {instance_name}")
                print(f"    └─ 타입: {instance_info.get('type', 'N/A')}")
                print(f"    └─ 사용자: {instance_info.get('user_id', 'N/A')}")
        
        # 오류 상태 인스턴스
        if status_groups['error']:
            print(f"\n⚠️ 오류 상태 ({len(status_groups['error'])}개):")
            for instance_name in status_groups['error']:
                instance = self.instances[instance_name]
                status = instance['status']
                print(f"  • {instance_name} - {status}")
        
        print("\n" + "="*80)
    
    def start_all(self) -> bool:
        """모든 인스턴스 시작"""
        print("🚀 모든 인스턴스 시작 중...")
        
        success_count = 0
        total_count = len(self.instances)
        
        for instance_name in self.instances:
            if self.start_instance(instance_name):
                success_count += 1
            time.sleep(2)  # 인스턴스 간 간격
        
        print(f"\n📊 시작 결과: {success_count}/{total_count} 성공")
        return success_count == total_count
    
    def stop_all(self) -> bool:
        """모든 인스턴스 중지"""
        print("🛑 모든 인스턴스 중지 중...")
        
        success_count = 0
        total_count = len(self.instances)
        
        for instance_name in self.instances:
            if self.stop_instance(instance_name):
                success_count += 1
            time.sleep(1)  # 인스턴스 간 간격
        
        print(f"\n📊 중지 결과: {success_count}/{total_count} 성공")
        return success_count == total_count
    
    def restart_all(self) -> bool:
        """모든 인스턴스 재시작"""
        print("🔄 모든 인스턴스 재시작 중...")
        
        if self.stop_all():
            time.sleep(3)  # 중지 완료 대기
            return self.start_all()
        
        return False

def main():
    """메인 함수"""
    manager = MultiInstanceManager()
    
    if len(sys.argv) < 2:
        print("📖 사용법:")
        print("  python multi_instance_manager.py [명령] [인스턴스명]")
        print("\n📋 명령:")
        print("  status                    - 모든 인스턴스 상태 표시")
        print("  start [인스턴스명]        - 특정 인스턴스 시작")
        print("  stop [인스턴스명]         - 특정 인스턴스 중지")
        print("  restart [인스턴스명]      - 특정 인스턴스 재시작")
        print("  start-all                 - 모든 인스턴스 시작")
        print("  stop-all                  - 모든 인스턴스 중지")
        print("  restart-all               - 모든 인스턴스 재시작")
        print("\n📝 예시:")
        print("  python multi_instance_manager.py status")
        print("  python multi_instance_manager.py start upbit_user1")
        print("  python multi_instance_manager.py start-all")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        manager.show_status()
    
    elif command == 'start':
        if len(sys.argv) < 3:
            print("❌ 인스턴스명을 지정해주세요")
            return
        instance_name = sys.argv[2]
        manager.start_instance(instance_name)
    
    elif command == 'stop':
        if len(sys.argv) < 3:
            print("❌ 인스턴스명을 지정해주세요")
            return
        instance_name = sys.argv[2]
        manager.stop_instance(instance_name)
    
    elif command == 'restart':
        if len(sys.argv) < 3:
            print("❌ 인스턴스명을 지정해주세요")
            return
        instance_name = sys.argv[2]
        manager.restart_instance(instance_name)
    
    elif command == 'start-all':
        manager.start_all()
    
    elif command == 'stop-all':
        manager.stop_all()
    
    elif command == 'restart-all':
        manager.restart_all()
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")

if __name__ == "__main__":
    main()
