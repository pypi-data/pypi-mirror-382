#!/bin/bash

# PyTrading Toolkit 로컬 설치 스크립트
# setup.py를 사용한 개발 모드 설치

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 PyTrading Toolkit 로컬 설치 시작${NC}"
echo -e "${BLUE}======================================${NC}"

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "설치 디렉토리: $SCRIPT_DIR"

# setup.py 파일 존재 확인
if [ ! -f "$SCRIPT_DIR/setup.py" ]; then
    echo -e "${RED}❌ setup.py 파일이 없습니다: $SCRIPT_DIR/setup.py${NC}"
    exit 1
fi

# 가상환경 확인
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 활성화되지 않았습니다.${NC}"
    echo -e "${YELLOW}💡 다음 명령으로 가상환경을 활성화하세요:${NC}"
    echo "source ../.venv/bin/activate"
    read -p "계속하시겠습니까? (y/n): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}설치를 중단합니다.${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✅ 가상환경 활성화됨: $VIRTUAL_ENV${NC}"
fi

# Python과 pip 확인
echo -e "${BLUE}🐍 Python 환경 확인${NC}"
echo "Python 경로: $(which python)"
echo "Python 버전: $(python --version)"
echo "pip 경로: $(which pip)"
echo "pip 버전: $(pip --version)"

# 현재 설치된 pytrading-toolkit 확인
echo -e "${BLUE}📦 기존 설치 확인${NC}"
if pip show pytrading-toolkit >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  pytrading-toolkit이 이미 설치되어 있습니다.${NC}"
    echo -e "${YELLOW}기존 설치를 제거하고 새로 설치합니다.${NC}"
    pip uninstall pytrading-toolkit -y
else
    echo -e "${GREEN}✅ 기존 설치 없음, 새로 설치합니다.${NC}"
fi

# 의존성 먼저 설치
echo -e "${BLUE}📋 의존성 설치${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt가 없습니다. 건너뜁니다.${NC}"
fi

# 개발 모드로 설치 (editable install)
echo -e "${BLUE}🔧 개발 모드 설치 (editable)${NC}"
cd "$SCRIPT_DIR"
pip install -e .

# 설치 확인
echo -e "${BLUE}✅ 설치 확인${NC}"
if python -c "import pytrading_toolkit; print(f'PyTrading Toolkit v{pytrading_toolkit.get_version()} 설치 성공!')" 2>/dev/null; then
    echo -e "${GREEN}🎉 설치가 성공적으로 완료되었습니다!${NC}"
else
    echo -e "${RED}❌ 설치에 실패했습니다.${NC}"
    exit 1
fi

# 사용법 안내
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}📚 사용법:${NC}"
echo ""
echo "Python에서 다음과 같이 사용하세요:"
echo ""
echo -e "${YELLOW}# 기본 import${NC}"
echo "from pytrading_toolkit import BaseConfigLoader, TelegramNotifier"
echo "from pytrading_toolkit.indicators import calculate_indicators"
echo "from pytrading_toolkit.utils import get_kst_now"
echo ""
echo -e "${YELLOW}# 또는 개별 모듈 import${NC}"
echo "from pytrading_toolkit.config import BaseConfigLoader"
echo "from pytrading_toolkit.notifications import TelegramNotifier"
echo ""
echo -e "${YELLOW}# 패키지 정보 확인${NC}"
echo "import pytrading_toolkit"
echo "print(pytrading_toolkit.get_info())"
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✨ 이제 어디서든 'import pytrading_toolkit'로 사용할 수 있습니다!${NC}"
