# 기여 가이드 (Contributing Guide)

PyTrading Toolkit에 기여해주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법을 안내합니다.

## 🚀 빠른 시작

### 1. 저장소 포크 (Fork)
1. GitHub에서 이 저장소를 포크하세요
2. 로컬에 클론하세요:
   ```bash
   git clone https://github.com/your-username/pytrading-toolkit.git
   cd pytrading-toolkit
   ```

### 2. 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -e .
pip install -r requirements.txt
```

### 3. 브랜치 생성
```bash
git checkout -b feature/your-feature-name
```

## 📝 개발 가이드라인

### 코드 스타일
- **PEP 8** 준수
- **Black** 포맷터 사용 권장
- **Type hints** 사용 권장
- **Docstring** 작성 (Google 스타일)

### 코드 예시
```python
def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    RSI(Relative Strength Index) 계산
    
    Args:
        prices: 가격 데이터 리스트
        period: RSI 계산 기간 (기본값: 14)
        
    Returns:
        RSI 값 리스트
        
    Raises:
        ValueError: prices가 비어있거나 period가 0 이하일 때
    """
    if not prices or period <= 0:
        raise ValueError("Invalid input parameters")
    
    # RSI 계산 로직
    return rsi_values
```

### 테스트 작성
- 새로운 기능에 대한 **단위 테스트** 작성
- **통합 테스트** 작성 (필요시)
- 테스트 실행:
  ```bash
  python -m pytest tests/
  ```

### 문서화
- **README.md** 업데이트 (필요시)
- **docstring** 작성
- **타입 힌트** 추가

## 🔄 기여 프로세스

### 1. 이슈 생성
- 버그 리포트나 기능 요청은 먼저 **Issues**에서 논의
- 기존 이슈가 있는지 확인

### 2. 코드 작성
- 기능 브랜치에서 작업
- 작은 단위로 커밋
- 명확한 커밋 메시지 작성

### 3. 테스트
- 모든 테스트 통과 확인
- 코드 품질 검사

### 4. Pull Request 생성
- **제목**: 명확하고 간결하게
- **설명**: 변경사항과 이유 설명
- **관련 이슈**: `Closes #123` 형태로 연결

### PR 템플릿
```markdown
## 변경사항
- [ ] 버그 수정
- [ ] 새로운 기능
- [ ] 문서 업데이트
- [ ] 테스트 추가

## 설명
변경사항에 대한 자세한 설명

## 테스트
- [ ] 기존 테스트 통과
- [ ] 새로운 테스트 추가
- [ ] 수동 테스트 완료

## 관련 이슈
Closes #123
```

## 🏗️ 프로젝트 구조

```
pytrading-toolkit/
├── pytrading_toolkit/     # 메인 패키지
│   ├── config/            # 설정 관리
│   ├── indicators/        # 기술지표
│   ├── notifications/     # 알림 시스템
│   ├── logging/           # 로깅 시스템
│   ├── health/            # 헬스체크
│   ├── utils/             # 유틸리티
│   ├── trading/           # 거래 도구
│   ├── security/          # 보안 모듈
│   └── core/              # 통합 시스템
├── examples/              # 사용 예제
├── tests/                 # 테스트 파일
└── docs/                  # 문서
```

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트
python -m pytest

# 특정 모듈 테스트
python -m pytest tests/test_indicators.py

# 커버리지 포함
python -m pytest --cov=pytrading_toolkit
```

### 테스트 작성 가이드
```python
import pytest
from pytrading_toolkit.indicators import manager

class TestRSI:
    def test_calculate_rsi_basic(self):
        """기본 RSI 계산 테스트"""
        prices = [100, 102, 101, 103, 105, 104, 106]
        rsi = manager.calculate_rsi(prices, period=5)
        assert len(rsi) == len(prices)
        assert all(0 <= val <= 100 for val in rsi)
    
    def test_calculate_rsi_invalid_input(self):
        """잘못된 입력에 대한 테스트"""
        with pytest.raises(ValueError):
            manager.calculate_rsi([], period=14)
        
        with pytest.raises(ValueError):
            manager.calculate_rsi([100, 102], period=0)
```

## 📋 체크리스트

### PR 제출 전 확인사항
- [ ] 코드가 PEP 8 스타일을 따름
- [ ] 모든 테스트가 통과함
- [ ] 새로운 기능에 대한 테스트가 있음
- [ ] 문서가 업데이트됨
- [ ] 커밋 메시지가 명확함
- [ ] PR 설명이 충분함

### 코드 리뷰 기준
- **기능성**: 요구사항을 만족하는가?
- **성능**: 효율적인가?
- **가독성**: 이해하기 쉬운가?
- **유지보수성**: 수정하기 쉬운가?
- **보안**: 안전한가?

## 🐛 버그 리포트

버그를 발견하셨나요? 다음 정보를 포함해서 이슈를 생성해주세요:

- **환경**: OS, Python 버전, 패키지 버전
- **재현 단계**: 버그를 재현하는 방법
- **예상 결과**: 기대했던 결과
- **실제 결과**: 실제로 발생한 결과
- **로그**: 관련 에러 로그 (있는 경우)

## 💡 기능 요청

새로운 기능을 제안하고 싶으신가요?

- **사용 사례**: 왜 이 기능이 필요한가?
- **구현 아이디어**: 어떻게 구현할 수 있을까?
- **대안**: 다른 해결 방법이 있는가?

## 📞 문의

- **Issues**: [GitHub Issues](https://github.com/your-username/pytrading-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/pytrading-toolkit/discussions)

## 📄 라이선스

이 프로젝트에 기여하시면 MIT 라이선스 하에 기여하신 코드가 배포됩니다.

---

감사합니다! 🎉
