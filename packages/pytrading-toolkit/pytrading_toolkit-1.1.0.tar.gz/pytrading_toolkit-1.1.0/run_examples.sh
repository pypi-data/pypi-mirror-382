#!/bin/bash

# PyTrading Toolkit 예제 실행 스크립트
# 이 스크립트는 pytrading-toolkit의 다양한 예제들을 실행합니다.

set -e

echo "🚀 PyTrading Toolkit 예제 실행"
echo "================================"

# 현재 디렉토리 확인
if [ ! -f "setup.py" ]; then
    echo "❌ pytrading-toolkit 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다."
    exit 1
fi

echo "🐍 Python 버전: $(python3 --version)"

# 패키지 설치 확인
echo "📦 패키지 설치 확인 중..."
if python3 -c "import pytrading_toolkit" 2>/dev/null; then
    echo "✅ pytrading-toolkit 패키지가 설치되어 있습니다."
else
    echo "⚠️  pytrading-toolkit 패키지가 설치되지 않았습니다."
    echo "💡 개발 모드로 설치합니다..."
    pip install -e .
fi

# 예제 디렉토리 확인
if [ ! -d "examples" ]; then
    echo "❌ examples 디렉토리를 찾을 수 없습니다."
    exit 1
fi

echo ""
echo "📚 사용 가능한 예제들:"
echo "1. basic_usage.py - 기본 사용법"
echo "2. test_config.py - 설정 관리 테스트"
echo "3. talib_example.py - TA-Lib 고성능 지표 예제"
echo "4. all - 모든 예제 실행"

read -p "실행할 예제를 선택하세요 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🔧 기본 사용법 예제 실행"
        echo "================================"
        python3 examples/basic_usage.py
        ;;
    2)
        echo ""
        echo "🧪 설정 관리 테스트 실행"
        echo "================================"
        python3 examples/test_config.py
        ;;
    3)
        echo ""
        echo "⚡ TA-Lib 고성능 지표 예제 실행"
        echo "================================"
        python3 examples/talib_example.py
        ;;
    4)
        echo ""
        echo "🚀 모든 예제 실행"
        echo "================================"
        
        echo ""
        echo "1️⃣ 기본 사용법 예제"
        echo "================================"
        python3 examples/basic_usage.py
        
        echo ""
        echo "2️⃣ 설정 관리 테스트"
        echo "================================"
        python3 examples/test_config.py
        
        echo ""
        echo "3️⃣ TA-Lib 고성능 지표 예제"
        echo "================================"
        python3 examples/talib_example.py
        
        echo ""
        echo "🎉 모든 예제 실행 완료!"
        ;;
    *)
        echo "❌ 잘못된 선택입니다. 1, 2, 3, 또는 4를 입력하세요."
        exit 1
        ;;
esac

echo ""
echo "✅ 예제 실행 완료!"
echo "💡 더 자세한 내용은 README.md와 INSTALL_GUIDE.md를 참조하세요."
