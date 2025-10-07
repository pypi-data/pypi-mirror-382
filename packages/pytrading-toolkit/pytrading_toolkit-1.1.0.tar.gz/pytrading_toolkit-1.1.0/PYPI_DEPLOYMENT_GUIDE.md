# 📦 PyPI 배포 가이드

PyPI(Python Package Index)에 패키지를 배포하는 완전한 가이드입니다.

## 📋 목차

1. [사전 준비](#사전-준비)
2. [패키지 구조 설정](#패키지-구조-설정)
3. [설정 파일 작성](#설정-파일-작성)
4. [패키지 빌드](#패키지-빌드)
5. [PyPI 업로드](#pypi-업로드)
6. [배포 후 확인](#배포-후-확인)
7. [버전 업데이트](#버전-업데이트)
8. [문제 해결](#문제-해결)

## 🚀 사전 준비

### 1. PyPI 계정 생성

1. **PyPI 웹사이트 접속**: https://pypi.org/account/register/
2. **계정 생성**: 사용자명, 이메일, 패스워드 입력
3. **이메일 인증**: 등록한 이메일에서 인증 링크 클릭

### 2. API 토큰 생성

**중요**: PyPI는 2023년부터 패스워드 인증을 중단하고 API 토큰만 사용합니다.

1. **토큰 페이지 접속**: https://pypi.org/manage/account/token/
2. **로그인**: PyPI 계정으로 로그인
3. **토큰 생성**:
   - "Add API token" 클릭
   - 토큰 이름 입력 (예: "my-package-upload")
   - "Create token" 클릭
   - 생성된 토큰 복사 (pypi-로 시작하는 긴 문자열)

### 3. 개발 도구 설치

```bash
pip install --upgrade pip setuptools wheel twine
```

## 📁 패키지 구조 설정

### 기본 디렉토리 구조

```
my-package/
├── setup.py              # 패키지 설정 파일
├── pyproject.toml        # 현대적 설정 파일 (선택사항)
├── MANIFEST.in           # 포함할 파일 목록
├── README.md             # 패키지 설명서
├── LICENSE               # 라이선스 파일
├── requirements.txt      # 의존성 목록
├── my_package/           # 실제 패키지 코드
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/                # 테스트 파일들
│   ├── __init__.py
│   └── test_module1.py
└── examples/             # 사용 예제 (선택사항)
    └── basic_usage.py
```

## ⚙️ 설정 파일 작성

### 1. setup.py 작성

```python
#!/usr/bin/env python3
"""
패키지 설정 파일
"""

from setuptools import setup, find_packages
import os

# README 파일 읽기
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# requirements.txt 읽기
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="my-package",                    # 패키지명 (PyPI에서 고유해야 함)
    version="1.0.0",                      # 버전 (Semantic Versioning 권장)
    author="Your Name",                   # 작성자 이름
    author_email="your.email@example.com", # 작성자 이메일
    description="패키지에 대한 간단한 설명",  # 짧은 설명
    long_description=read_readme(),       # 상세 설명 (README.md 내용)
    long_description_content_type="text/markdown", # README 형식
    url="https://pypi.org/project/my-package/", # 프로젝트 URL
    project_urls={                        # 관련 URL들
        "Bug Reports": "https://pypi.org/project/my-package/#issues",
        "Source": "https://pypi.org/project/my-package/",
        "Documentation": "https://pypi.org/project/my-package/",
    },
    packages=find_packages(),             # 자동으로 패키지 찾기
    classifiers=[                         # 패키지 분류
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",              # 지원하는 Python 버전
    install_requires=read_requirements(), # 의존성 패키지들
    extras_require={                      # 선택적 의존성
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={                        # 콘솔 스크립트 (선택사항)
        "console_scripts": [
            "my-command=my_package.cli:main",
        ],
    },
    include_package_data=True,            # 패키지 데이터 포함
    zip_safe=False,                       # zip 안전성
    keywords="python package example",    # 검색 키워드
)
```

### 2. MANIFEST.in 작성

```ini
include README.md
include LICENSE
include requirements.txt
include pyproject.toml
recursive-include my_package *.py
recursive-include my_package *.yaml
recursive-include my_package *.json
recursive-include examples *.py
recursive-include examples *.md
recursive-include tests *.py
recursive-include tests *.json
global-exclude *.pyc
global-exclude __pycache__
global-exclude *.egg-info
global-exclude .git*
global-exclude .DS_Store
```

### 3. requirements.txt 작성

```txt
# 핵심 의존성
requests>=2.28.0
pyyaml>=6.0
numpy>=1.21.0
pandas>=1.3.0

# 선택적 의존성
# matplotlib>=3.5.0
# plotly>=5.0.0
```

## 🔨 패키지 빌드

### 1. 빌드 전 정리

```bash
# 이전 빌드 파일들 정리
rm -rf dist/ build/ *.egg-info/
```

### 2. 패키지 빌드

```bash
# source distribution과 wheel 생성
python setup.py sdist bdist_wheel
```

### 3. 빌드 결과 확인

```bash
# 생성된 파일들 확인
ls -la dist/

# 패키지 검증
twine check dist/*
```

**예상 결과:**
```
dist/
├── my-package-1.0.0-py3-none-any.whl    # wheel 파일
└── my-package-1.0.0.tar.gz              # source distribution
```

## 📤 PyPI 업로드

### 1. TestPyPI에 먼저 테스트 (권장)

```bash
# TestPyPI 업로드
twine upload --repository testpypi dist/* --username __token__ --password <API_TOKEN>

# TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ my-package
```

### 2. 실제 PyPI에 업로드

```bash
# PyPI 업로드
twine upload dist/* --username __token__ --password <API_TOKEN>
```

**API 토큰 사용법:**
- `--username __token__` (고정)
- `--password <API_TOKEN>` (생성한 토큰)

### 3. 업로드 확인

```bash
# PyPI에서 설치 테스트
pip install my-package

# 패키지 정보 확인
pip show my-package
```

## ✅ 배포 후 확인

### 1. PyPI 패키지 페이지 확인

- **패키지 페이지**: https://pypi.org/project/my-package/
- **다운로드 수**: 패키지 페이지에서 확인
- **메타데이터**: 설명, 의존성, 분류 등 확인

### 2. 설치 및 사용 테스트

```bash
# 새 환경에서 테스트
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate   # Windows

# 패키지 설치
pip install my-package

# 패키지 사용 테스트
python -c "import my_package; print('설치 성공!')"
```

### 3. 검색 가능 여부 확인

- **PyPI 검색**: https://pypi.org/search/?q=my-package
- **pip 검색**: `pip search my-package` (deprecated)

## 🔄 버전 업데이트

### 1. 버전 번호 수정

**setup.py에서:**
```python
version="1.0.1",  # 1.0.0 → 1.0.1
```

### 2. CHANGELOG.md 업데이트

```markdown
## [1.0.1] - 2024-01-15

### 🐛 버그 수정
- 특정 버그 설명

### 🔧 개선사항
- 특정 개선사항 설명
```

### 3. 새 버전 배포

```bash
# 새 버전 빌드
rm -rf dist/ build/ *.egg-info/
python setup.py sdist bdist_wheel

# 업로드
twine upload dist/* --username __token__ --password <API_TOKEN>
```

## 🚨 문제 해결

### 1. 403 Forbidden 오류

**문제**: `HTTPError: 403 Forbidden`

**원인**: 패스워드 인증 사용 (더 이상 지원하지 않음)

**해결**: API 토큰 사용
```bash
twine upload dist/* --username __token__ --password <API_TOKEN>
```

### 2. 패키지명 중복 오류

**문제**: `HTTPError: 400 Bad Request - Package already exists`

**원인**: 동일한 패키지명이 이미 존재

**해결**: 
1. 다른 패키지명 사용
2. 기존 패키지의 새 버전으로 업로드

### 3. 의존성 오류

**문제**: `HTTPError: 400 Bad Request - Invalid distribution`

**원인**: requirements.txt에 잘못된 의존성

**해결**: requirements.txt 수정 후 재빌드

### 4. 빌드 오류

**문제**: `error: package directory 'my_package' does not exist`

**원인**: 패키지 디렉토리 구조 문제

**해결**: 
1. `__init__.py` 파일 확인
2. `find_packages()` 결과 확인

## 📚 추가 리소스

### 공식 문서
- **PyPI 사용자 가이드**: https://packaging.python.org/tutorials/packaging-projects/
- **setuptools 문서**: https://setuptools.pypa.io/
- **twine 문서**: https://twine.readthedocs.io/

### 유용한 도구
- **패키지 검증**: `twine check dist/*`
- **의존성 확인**: `pipdeptree`
- **패키지 분석**: `pip-audit`

### 버전 관리
- **Semantic Versioning**: https://semver.org/
- **Python 버전 지원**: https://devguide.python.org/versions/

## 🎯 체크리스트

배포 전 확인사항:

- [ ] PyPI 계정 생성 및 API 토큰 발급
- [ ] 패키지명이 PyPI에서 사용 가능한지 확인
- [ ] setup.py 정보가 정확한지 확인
- [ ] README.md가 완성되었는지 확인
- [ ] LICENSE 파일이 있는지 확인
- [ ] requirements.txt가 정확한지 확인
- [ ] 패키지 빌드가 성공하는지 확인
- [ ] twine check가 통과하는지 확인
- [ ] TestPyPI에서 테스트 완료
- [ ] 실제 PyPI에서 설치 테스트 완료

---

**🎉 축하합니다! 이제 전 세계 누구나 `pip install my-package`로 패키지를 설치할 수 있습니다!**
