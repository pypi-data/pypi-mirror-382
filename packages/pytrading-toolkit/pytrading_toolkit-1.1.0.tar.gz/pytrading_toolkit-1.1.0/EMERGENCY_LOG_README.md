# 🚨 장애 로그 추출 도구 (Emergency Log Extractor)

트레이딩 시스템에서 장애가 발생했을 때 문제 분석에 필요한 로그만 빠르게 추출하는 도구입니다.

## ✨ 주요 기능

- **🔍 스마트 로그 필터링**: 에러, 트레이딩, 시스템 로그를 자동으로 분류
- **⚡ 빠른 분석**: 최근 2시간부터 24시간까지 시간 범위 설정 가능
- **📊 컨텍스트 포함**: 에러 발생 전후 상황을 함께 분석
- **📁 자동 파일 생성**: 분석 결과를 체계적으로 정리하여 저장
- **📋 요약 리포트**: 장애 상황을 한눈에 파악할 수 있는 요약 제공

## 🚀 빠른 시작

### 1. 기본 사용법 (최근 6시간 분석)

```bash
./extract_emergency_logs.sh
```

### 2. 빠른 모드 (최근 2시간 분석)

```bash
./extract_emergency_logs.sh -q
```

### 3. 전체 모드 (최근 24시간 분석)

```bash
./extract_emergency_logs.sh -f
```

### 4. 사용자 정의 시간 범위

```bash
./extract_emergency_logs.sh -t 12  # 최근 12시간
```

## 📖 상세 사용법

### 명령행 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-h, --help` | 도움말 표시 | - |
| `-l, --log-dir DIR` | 로그 디렉토리 경로 | `logs` |
| `-o, --output-dir DIR` | 출력 디렉토리 경로 | `emergency_logs` |
| `-t, --hours HOURS` | 분석할 시간 범위 (시간) | `6` |
| `-e, --error-types TYPES` | 에러 타입들 | `ERROR CRITICAL EXCEPTION` |
| `-c, --no-context` | 에러 로그에서 컨텍스트 제외 | `false` |
| `-q, --quick` | 빠른 모드 (최근 2시간) | `false` |
| `-f, --full` | 전체 모드 (최근 24시간) | `false` |

### 사용 예시

#### 기본 분석
```bash
# 최근 6시간 로그 분석
./extract_emergency_logs.sh
```

#### 빠른 문제 진단
```bash
# 최근 2시간만 빠르게 분석
./extract_emergency_logs.sh -q
```

#### 전체 시스템 점검
```bash
# 최근 24시간 전체 분석
./extract_emergency_logs.sh -f
```

#### 특정 로그 디렉토리 분석
```bash
# 다른 위치의 로그 분석
./extract_emergency_logs.sh -l /var/log/trader
```

#### 에러 타입 지정
```bash
# 특정 에러 타입만 분석
./extract_emergency_logs.sh -e "ERROR TIMEOUT"
```

## 📊 출력 결과

### 생성되는 파일들

1. **에러 로그 파일**
   - `emergency_error_YYYYMMDD_HHMMSS.log`
   - `emergency_critical_YYYYMMDD_HHMMSS.log`
   - `emergency_exception_YYYYMMDD_HHMMSS.log`

2. **트레이딩 로그 파일**
   - `emergency_trading_YYYYMMDD_HHMMSS.log`

3. **시스템 로그 파일**
   - `emergency_system_YYYYMMDD_HHMMSS.log`

4. **요약 리포트**
   - `emergency_summary_YYYYMMDD_HHMMSS.txt`

### 요약 리포트 예시

```
🚨 장애 로그 분석 리포트
==================================================
📅 생성 시간: 2024-01-15 14:30:25

🔴 에러 로그: 15건
  - ERROR: 8건
  - CRITICAL: 3건
  - EXCEPTION: 4건

📊 트레이딩 로그: 45건

⚙️ 시스템 로그: 23건

⚠️ 중요도별 분류:
  - 🚨 Critical: 3건
  - 🟡 Warning: 2건
  - 🔴 Error: 10건
```

## 🔧 고급 사용법

### Python 스크립트 직접 실행

```bash
python3 emergency_log_extractor.py \
    --log-dir logs \
    --output-dir emergency_logs \
    --hours 12 \
    --error-types ERROR CRITICAL \
    --include-context
```

### 커스텀 키워드 설정

`emergency_log_extractor.py` 파일에서 다음 변수들을 수정하여 검색 키워드를 커스터마이즈할 수 있습니다:

```python
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
```

## 🚨 장애 대응 워크플로우

### 1. 장애 감지
```bash
# 텔레그램 알림 수신 또는 모니터링 시스템에서 장애 감지
```

### 2. 빠른 로그 분석
```bash
# 최근 2시간 로그 빠르게 분석
./extract_emergency_logs.sh -q
```

### 3. 상세 분석 (필요시)
```bash
# 더 넓은 범위로 상세 분석
./extract_emergency_logs.sh -f
```

### 4. 문제 진단
- 생성된 로그 파일들을 검토
- 요약 리포트로 전체 상황 파악
- 에러 패턴과 트렌드 분석

### 5. 복구 및 모니터링
- 문제 해결 후 시스템 복구
- 지속적인 모니터링으로 안정성 확인

## 📋 요구사항

- **Python 3.6+**
- **Bash shell** (Linux/macOS/WSL)
- **로그 파일**: `.log` 확장자

## 🔍 문제 해결

### 로그 파일을 찾을 수 없는 경우
```bash
# 현재 디렉토리에서 로그 파일 찾기
find . -name "*.log" -type f

# 특정 패턴으로 로그 파일 찾기
find . -name "*trading*" -type f
```

### 권한 문제가 발생하는 경우
```bash
# 스크립트에 실행 권한 부여
chmod +x extract_emergency_logs.sh

# 출력 디렉토리 권한 확인
ls -la emergency_logs/
```

### Python 모듈 오류가 발생하는 경우
```bash
# Python 버전 확인
python3 --version

# 필요한 패키지 설치
pip3 install pathlib typing
```

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해 주세요.

## 📄 라이선스

이 도구는 MIT 라이선스 하에 배포됩니다.
