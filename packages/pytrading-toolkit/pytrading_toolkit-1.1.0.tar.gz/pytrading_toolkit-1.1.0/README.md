# PyTrading Toolkit

Python 암호화폐 트레이딩 봇 개발을 위한 포괄적인 도구킷입니다.

## 🌐 오픈소스 패키지

이 패키지는 **MIT 라이선스** 하에 배포되는 **오픈소스 패키지**입니다.

### 📋 패키지 정보
- **라이선스**: MIT (자유로운 사용, 수정, 배포 가능)
- **기여**: 상세한 기여 가이드는 [CONTRIBUTING.md](./CONTRIBUTING.md) 참조
- **이슈**: GitHub Issues를 통한 버그 리포트 및 기능 요청
- **기여자**: 커뮤니티 기여 환영

### 🎯 사용 목적
- **공통 도구**: 암호화폐 거래 프로젝트 개발을 위한 핵심 도구
- **범용 패키지**: 다양한 암호화폐 거래 프로젝트에서 재사용 가능
- **핵심 기능**: 기술지표, 알림, 로깅, 설정 관리 등
- **독립성**: 다른 프로젝트와 독립적으로 사용 가능

## 🏗️ 패키지 구조

### 📦 전체 프로젝트 구조
```
pytrading-toolkit/              # 오픈소스 패키지 루트
├── LICENSE                     # MIT 라이선스
├── README.md                   # 패키지 소개 (현재 파일)
├── CONTRIBUTING.md             # 기여 가이드
├── requirements.txt            # 패키지 의존성
├── setup.py                    # 패키지 설치 스크립트
├── pyproject.toml              # 패키지 설정
├── pytrading_toolkit/          # 🎯 메인 패키지 소스 코드
│   ├── config/                 # 계층적 설정 관리 시스템
│   │   ├── base.py             # 기본 설정 클래스
│   │   ├── master_config_loader.py # 마스터 설정 로더
│   │   └── exchange/           # 거래소별 설정
│   │       ├── upbit.py        # 업비트 설정
│   │       └── bybit.py        # 바이비트 설정
│   ├── indicators/             # 기술지표 계산
│   ├── notifications/          # 알림 시스템
│   ├── logging/                # 로깅 시스템
│   ├── health/                 # 헬스체크 및 모니터링
│   ├── utils/                  # 유틸리티 함수들
│   ├── trading/                # 거래 관련 유틸리티
│   ├── security/               # 보안 모듈
│   ├── core/                   # 통합 시스템 관리
│   └── tools/                  # 관리 도구들
│       ├── config_setup.py     # 통합 설정 도구
│       ├── multi_instance_manager.py # 멀티 인스턴스 관리
│       ├── emergency_log_extractor.py # 긴급 로그 추출
│       └── ...                 # 기타 도구들
├── examples/                   # 사용 예제
├── tests/                      # 테스트 파일
├── run_examples.sh             # 예제 실행 스크립트
├── install_local.sh            # 로컬 설치 스크립트
└── extract_emergency_logs.sh   # 긴급 로그 추출 스크립트
```

> 📖 **상세 가이드**: 이 문서는 대표 매뉴얼이며, 모든 도구 사용법이 포함되어 있습니다.

## ✨ 주요 기능

### 🔧 계층적 설정 관리 시스템
- **기본 설정**: BaseConfigLoader를 통한 공통 설정 관리
- **거래소별 설정**: UpbitConfigLoader, BybitConfigLoader 등
- **마스터 설정**: MasterConfigLoader를 통한 통합 설정 관리
- **자동 병합**: 우선순위에 따른 설정 자동 병합
- **동적 로딩**: 런타임에 설정 변경사항 자동 반영

### 📊 기술지표 계산
- **TA-Lib 기반**: 업계 표준 TA-Lib 라이브러리 사용
  - **모멘텀**: RSI, MACD, 스토캐스틱, CCI, 윌리엄스 %R, MFI
  - **변동성**: 볼린저 밴드, ATR, Historical Volatility
  - **트렌드**: ADX, Aroon, 이동평균 기울기
  - **거래량**: OBV, Volume SMA, Volume Ratio
  - **패턴 인식**: Doji, Hammer, Engulfing 패턴
  - **피벗 포인트**: Support/Resistance 레벨 계산
- **커스텀 지표**: 사용자 정의 지표 추가 가능
- **실시간 계산**: 실시간 데이터 기반 고속 지표 계산
- **다중 타임프레임**: 1분, 5분, 1시간, 1일 등 다양한 시간대
- **성능 최적화**: C 라이브러리 기반으로 10-50배 빠른 계산 속도

### 🔔 알림 시스템
- **텔레그램**: 알림 메시지, 오류 알림, 상태 보고
- **이메일**: 중요 알림 이메일 발송
- **로그**: 상세한 시스템 로그 기록
- **웹훅**: 외부 시스템 연동
- **실시간 모니터링**: 시스템 상태, API 연결 상태

### 🏥 헬스체크 및 모니터링
- **시스템 모니터링**: CPU, 메모리, 디스크 사용량
- **API 상태**: 거래소 API 연결 상태
- **자동 복구**: 오류 발생 시 자동 재시작
- **프로세스 관리**: 멀티 인스턴스 관리

### 🛠️ 관리 도구
- **설정 마법사**: `config_setup.py` - 대화형 설정 생성
- **멀티 인스턴스**: `multi_instance_manager.py` - 여러 인스턴스 동시 관리
- **긴급 로그**: `emergency_log_extractor.py` - 문제 발생 시 로그 추출
- **의존성 관리**: 자동 패키지 설치 및 업데이트

## 🚀 설치

### 개발 모드 설치 (권장)

```bash
# 패키지 디렉토리에서 실행
cd packages/pytrading-toolkit
pip install -e .
```

### 일반 설치

```bash
cd packages/pytrading-toolkit
pip install .
```

### TA-Lib 설치 (고성능 지표를 위해 권장)

TA-Lib는 C 라이브러리 기반의 고성능 기술적 분석 라이브러리입니다:

```bash
# Linux/Ubuntu
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib

# Windows (conda 권장)
conda install -c conda-forge ta-lib
# 또는
pip install TA-Lib
```


## 📚 사용법

### 🚀 빠른 시작

```bash
# 예제 실행
chmod +x run_examples.sh
./run_examples.sh
```

### 🛠️ 관리 도구

#### 통합 설정 도구 (pytrading_toolkit.tools.config_setup)

```bash
# 패키지 설치 후 사용
pytrading-config

# 또는 직접 실행
python3 -c "from pytrading_toolkit.tools.config_setup import main; main()"

# 도움말
pytrading-config --help
```

#### 멀티 인스턴스 관리 도구 (pytrading_toolkit.tools.multi_instance_manager)

```bash
# 패키지 설치 후 사용
pytrading-manager status
pytrading-manager start upbit_user1
pytrading-manager start-all

# 또는 직접 실행
python3 -c "from pytrading_toolkit.tools.multi_instance_manager import main; main()"
```

#### 긴급 로그 추출 도구 (pytrading_toolkit.tools.emergency_log_extractor)

```bash
# 패키지 설치 후 사용
pytrading-log-extractor --help

# 또는 직접 실행
python3 -c "from pytrading_toolkit.tools.emergency_log_extractor import main; main()"
```

> 📖 **상세한 사용법**: [EMERGENCY_LOG_README.md](./EMERGENCY_LOG_README.md)를 참조하세요.


### 기본 Import

```python
from pytrading_toolkit import (
    BaseConfigLoader,
    UpbitConfigLoader,
    BybitConfigLoader,
    TelegramNotifier,
    setup_logger,
    HealthMonitor,
    SystemManager,
    SystemDashboard,
    AutoRecoverySystem
)
```

### 헬스 모니터링 사용

```python
from pytrading_toolkit import HealthMonitor

# 헬스 모니터 초기화
health_monitor = HealthMonitor(telegram_notifier)

# 시스템 상태 확인
status = health_monitor.get_system_status()
print(f"시스템 상태: {status}")

# 헬스 체크 시작
health_monitor.start_monitoring()
```

### 거래소별 설정 사용

```python
# 업비트 설정
from pytrading_toolkit import UpbitConfigLoader

upbit_config = UpbitConfigLoader()
config = upbit_config.load_config()

# 바이비트 설정
from pytrading_toolkit import BybitConfigLoader

bybit_config = BybitConfigLoader()
config = bybit_config.load_config()
```

### 기술지표 사용

#### 기본 지표 (ta 라이브러리)
```python
from pytrading_toolkit.indicators import calculate_indicators

# 기본 지표 계산
candles = [{'open': 100, 'high': 105, 'low': 98, 'close': 102, 'volume': 1000}, ...]
indicators = calculate_indicators(candles, [
    {'type': 'RSI', 'period': 14},
    {'type': 'SMA', 'period': 20}
])
```

#### 기본 지표 사용
```python
from pytrading_toolkit.indicators import (
    calculate_indicators,
    get_market_sentiment,
    calculate_support_resistance,
    calculate_trend_indicators
)

# 기본 지표 계산
indicators = calculate_indicators(candles, [
    {'type': 'RSI', 'period': 14},
    {'type': 'MACD', 'fast': 12, 'slow': 26, 'signal': 9},
    {'type': 'BB', 'period': 20, 'std': 2},
    {'type': 'STOCH', 'k_period': 14, 'd_period': 3}
])

# 지지/저항선 계산
support_resistance = calculate_support_resistance(candles)

# 트렌드 지표 계산
trend_indicators = calculate_trend_indicators(candles)

# 시장 심리 분석
sentiment = get_market_sentiment(indicators)
print(f"시장 심리: {sentiment['overall']}")
```

### 고급 지표 사용 (TA-Lib 추가 기능)

```python
from pytrading_toolkit.indicators import (
    calculate_advanced_indicators_talib,
    get_market_sentiment_talib,
    TALIB_AVAILABLE
)

# TA-Lib 사용 가능 여부 확인
if TALIB_AVAILABLE:
    # 고급 지표 (패턴 인식, 피벗 포인트)
    advanced_indicators = calculate_advanced_indicators_talib(candles)
    
    # 고급 시장 심리 분석
    sentiment = get_market_sentiment_talib(advanced_indicators)
    print(f"고급 시장 심리: {sentiment['overall']}")
```

### 알림 시스템

```python
from pytrading_toolkit import TelegramNotifier

notifier = TelegramNotifier(bot_token, chat_id)
notifier.send_message("시스템 알림")
notifier.send_error("에러 발생", "trading_error")
```

### 로깅 시스템

```python
from pytrading_toolkit import setup_logger

logger = setup_logger('my_app', log_dir='./logs')
logger.info("애플리케이션 시작")
```


## 🔧 설정 파일 구조

### 공통 설정 (BaseConfigLoader)
- 기본 설정 로딩 및 검증
- 캐싱 지원
- 에러 처리

### 거래소별 설정
- **UpbitConfigLoader**: 업비트 전용 설정 및 검증
- **BybitConfigLoader**: 바이비트 전용 설정 및 검증


## 📚 관련 문서

- **[PyPI 배포 가이드](PYPI_DEPLOYMENT_GUIDE.md)** - PyPI에 패키지 배포하는 방법
- **[기여 가이드](CONTRIBUTING.md)** - 상세한 기여 방법 및 개발 가이드라인
- **[긴급 로그 추출 가이드](EMERGENCY_LOG_README.md)** - 장애 대응을 위한 로그 분석 도구 사용법

## 🎯 특징

- **모듈화**: 거래소별로 독립적인 설정 및 로직
- **재사용성**: 공통 기능을 패키지로 분리
- **확장성**: 새로운 거래소 추가 용이
- **유지보수성**: 명확한 구조와 책임 분리
- **실시간성**: 실시간 데이터 처리에 최적화된 성능
- **보안성**: 암호화, 접근 제어, 보안 감사 기능
- **모니터링**: 실시간 시스템 상태 모니터링 및 자동 복구
- **엔터프라이즈급**: 대규모 운영 환경에 적합한 안정성

## 🏦 지원 거래소

### 현재 지원
- **Upbit** (업비트) - 한국 최대 암호화폐 거래소
- **Bybit** (바이비트) - 글로벌 선물 거래소

### 향후 지원 예정
- **Binance** (바이낸스) - 글로벌 최대 거래소

## 🔒 보안 가이드

### API 키 관리
```python
from pytrading_toolkit import APIKeyManager, SecureStorage

# 보안 저장소 초기화
secure_storage = SecureStorage()

# API 키 관리자 초기화
api_manager = APIKeyManager(secure_storage)

# API 키 안전하게 저장
api_manager.store_api_key("upbit", "your_access_key", "your_secret_key")

# API 키 안전하게 조회
access_key = api_manager.get_api_key("upbit", "access")
```

### 환경변수 사용
```bash
# .env 파일에 민감한 정보 저장
UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 접근 제어
```python
from pytrading_toolkit import AccessControlManager

# 접근 제어 관리자 초기화
acm = AccessControlManager()

# 사용자 생성 및 권한 부여
acm.create_user("user", "password123", "user")
acm.assign_permission("user", "system", "read")
acm.assign_permission("user", "system", "write")
```

## 🔄 마이그레이션

기존 코드에서 `sys.path.insert`를 제거하고 직접 import를 사용하세요:

```python
# 기존 (권장하지 않음)
import sys
sys.path.insert(0, '...')
from pytrading_toolkit import ...

# 새로운 방식 (권장)
from pytrading_toolkit import ...
```

## 🔍 문제 해결

### 패키지 설치 문제
```bash
# PyTrading Toolkit 재설치
pip uninstall pytrading-toolkit -y
pip install pytrading-toolkit

# 또는 개발 모드로 재설치
pip install -e .
```

### 의존성 문제
```bash
# 필요한 패키지 설치
pip install pyyaml psutil requests ta python-telegram-bot

# TA-Lib 설치 (고성능 지표를 위해)
pip install TA-Lib
```

### 버전 확인
```bash
# 패키지 버전 확인
pip show pytrading-toolkit

# Python에서 버전 확인
python3 -c "import pytrading_toolkit; print(pytrading_toolkit.get_version())"
```

## 📝 주의사항

### 🎯 **범용 암호화폐 도구**
이 패키지는 **암호화폐 프로젝트 개발**에 특화되어 있습니다:
- 실시간 데이터 처리에 최적화
- 낮은 지연시간과 높은 안정성 중시
- 모듈화된 구조로 다양한 프로젝트에서 재사용 가능

## 🧪 예제 및 테스트

### 📁 예제 파일들

- `examples/basic_usage.py` - 기본 사용법 예제
- `examples/test_config.py` - 설정 관리 테스트
- `run_examples.sh` - 예제 실행 스크립트

### 🚀 예제 실행 방법

```bash
# 1. 예제 실행 스크립트 권한 부여
chmod +x run_examples.sh

# 2. 예제 실행
./run_examples.sh

# 3. 개별 예제 실행
python3 examples/basic_usage.py
python3 examples/test_config.py
```

### 📊 테스트 결과 확인

```bash
# 설정 관리 모듈 테스트
python3 examples/test_config.py

# 결과 예시:
# 🧪 PyTrading Toolkit 설정 관리 모듈 테스트
# 📊 테스트 결과: 4/4 통과
# 🎉 모든 테스트 통과!
```

## 🤝 기여하기

이 프로젝트는 오픈소스이며, 기여를 환영합니다!

> 📖 **상세한 기여 가이드**: [CONTRIBUTING.md](./CONTRIBUTING.md)를 참조하세요.

## 📝 라이선스

> 📄 [LICENSE 파일 보기](./LICENSE)

이 프로젝트는 MIT 라이선스 하에 배포되며, 자유로운 사용과 수정이 가능합니다.

## 📞 지원 및 문의

- **Issues**: [GitHub Issues](https://github.com/your-username/pytrading-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/pytrading-toolkit/discussions)
- **Wiki**: [프로젝트 위키](https://github.com/your-username/pytrading-toolkit/wiki)

---

⭐ **이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
