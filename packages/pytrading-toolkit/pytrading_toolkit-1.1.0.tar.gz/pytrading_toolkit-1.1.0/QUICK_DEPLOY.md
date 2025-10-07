# ⚡ PyPI 빠른 배포 가이드

PyPI에 패키지를 빠르게 배포하는 핵심 단계만 정리한 가이드입니다.

## 🚀 5분 배포 가이드

### 1. 사전 준비 (1분)
```bash
# 개발 도구 설치
pip install --upgrade pip setuptools wheel twine

# PyPI 계정 생성 및 API 토큰 발급
# https://pypi.org/manage/account/token/
```

### 2. 패키지 설정 (2분)
```bash
# setup.py 작성 (패키지명, 버전, 작성자 정보)
# MANIFEST.in 작성 (포함할 파일들)
# requirements.txt 작성 (의존성)
```

### 3. 빌드 및 업로드 (2분)
```bash
# 패키지 빌드
rm -rf dist/ build/ *.egg-info/
python setup.py sdist bdist_wheel

# 검증
twine check dist/*

# 업로드
twine upload dist/* --username __token__ --password <API_TOKEN>
```

## 📋 필수 체크리스트

- [ ] PyPI 계정 생성
- [ ] API 토큰 발급
- [ ] setup.py 정보 수정
- [ ] 패키지명 중복 확인
- [ ] 빌드 성공 확인
- [ ] 업로드 성공 확인

## 🔗 상세 가이드

더 자세한 내용은 [PYPI_DEPLOYMENT_GUIDE.md](PYPI_DEPLOYMENT_GUIDE.md)를 참조하세요.

## 🎯 결과

성공하면 전 세계 누구나 `pip install your-package`로 설치할 수 있습니다!
