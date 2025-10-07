#!/bin/bash

# 장애 발생 시 로그 추출 스크립트
# 트레이딩 시스템에서 문제가 발생했을 때 관련 로그만 빠르게 추출

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="logs"
OUTPUT_DIR="emergency_logs"
HOURS_BACK=6
ERROR_TYPES="ERROR CRITICAL EXCEPTION"
INCLUDE_CONTEXT=true

# 도움말 함수
show_help() {
    echo -e "${BLUE}🚨 장애 로그 추출 도구${NC}"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -h, --help              이 도움말을 표시합니다"
    echo "  -l, --log-dir DIR       로그 디렉토리 경로 (기본값: logs)"
    echo "  -o, --output-dir DIR    출력 디렉토리 경로 (기본값: emergency_logs)"
    echo "  -t, --hours HOURS       분석할 시간 범위 (기본값: 6시간)"
    echo "  -e, --error-types TYPES 에러 타입들 (기본값: ERROR CRITICAL EXCEPTION)"
    echo "  -c, --no-context        에러 로그에서 컨텍스트 제외"
    echo "  -q, --quick             빠른 모드 (최근 2시간만 분석)"
    echo "  -f, --full              전체 모드 (최근 24시간 분석)"
    echo ""
    echo "예시:"
    echo "  $0                    # 기본 설정으로 최근 6시간 분석"
    echo "  $0 -q                 # 빠른 모드 (최근 2시간)"
    echo "  $0 -f                 # 전체 모드 (최근 24시간)"
    echo "  $0 -t 12             # 최근 12시간 분석"
    echo "  $0 -l /var/log/trader # 특정 로그 디렉토리 분석"
    echo ""
}

# 빠른 모드 설정
quick_mode() {
    HOURS_BACK=2
    echo -e "${YELLOW}⚡ 빠른 모드: 최근 2시간 로그 분석${NC}"
}

# 전체 모드 설정
full_mode() {
    HOURS_BACK=24
    echo -e "${BLUE}📊 전체 모드: 최근 24시간 로그 분석${NC}"
}

# 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -l|--log-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -t|--hours)
            HOURS_BACK="$2"
            shift 2
            ;;
        -e|--error-types)
            ERROR_TYPES="$2"
            shift 2
            ;;
        -c|--no-context)
            INCLUDE_CONTEXT=false
            shift
            ;;
        -q|--quick)
            quick_mode
            shift
            ;;
        -f|--full)
            full_mode
            shift
            ;;
        *)
            echo -e "${RED}❌ 알 수 없는 옵션: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Python 스크립트 경로 확인
PYTHON_SCRIPT="$SCRIPT_DIR/emergency_log_extractor.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}❌ Python 스크립트를 찾을 수 없습니다: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 로그 디렉토리 확인
if [[ ! -d "$LOG_DIR" ]]; then
    echo -e "${RED}❌ 로그 디렉토리를 찾을 수 없습니다: $LOG_DIR${NC}"
    echo -e "${YELLOW}💡 현재 디렉토리에서 logs 폴더를 찾아보겠습니다...${NC}"
    
    # 현재 디렉토리에서 logs 폴더 찾기
    if [[ -d "logs" ]]; then
        LOG_DIR="logs"
        echo -e "${GREEN}✅ logs 폴더를 찾았습니다: $LOG_DIR${NC}"
    else
        echo -e "${RED}❌ logs 폴더를 찾을 수 없습니다.${NC}"
        echo -e "${YELLOW}💡 사용 가능한 로그 디렉토리를 확인해보세요:${NC}"
        find . -name "*.log" -type f 2>/dev/null | head -10 | sed 's/^/  /'
        exit 1
    fi
fi

# Python 실행 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

# 로그 파일 존재 확인
LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l)

if [[ $LOG_COUNT -eq 0 ]]; then
    echo -e "${RED}❌ 로그 파일을 찾을 수 없습니다: $LOG_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 로그 파일 ${LOG_COUNT}개 발견${NC}"

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 컨텍스트 옵션 설정
CONTEXT_OPTION=""
if [[ "$INCLUDE_CONTEXT" == "true" ]]; then
    CONTEXT_OPTION="--include-context"
fi

# Python 스크립트 실행
echo -e "${BLUE}🚀 장애 로그 분석 시작...${NC}"
echo -e "${BLUE}📁 로그 디렉토리: $LOG_DIR${NC}"
echo -e "${BLUE}📁 출력 디렉토리: $OUTPUT_DIR${NC}"
echo -e "${BLUE}⏰ 분석 범위: 최근 ${HOURS_BACK}시간${NC}"
echo -e "${BLUE}🔍 에러 타입: $ERROR_TYPES${NC}"
echo ""

python3 "$PYTHON_SCRIPT" \
    --log-dir "$LOG_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --hours "$HOURS_BACK" \
    --error-types $ERROR_TYPES \
    $CONTEXT_OPTION

# 실행 결과 확인
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎯 로그 분석이 완료되었습니다!${NC}"
    echo -e "${GREEN}📁 결과 파일 위치: $OUTPUT_DIR${NC}"
    
    # 생성된 파일 목록 표시
    if [[ -d "$OUTPUT_DIR" ]]; then
        echo ""
        echo -e "${BLUE}📄 생성된 파일들:${NC}"
        ls -la "$OUTPUT_DIR"/*.log "$OUTPUT_DIR"/*.txt 2>/dev/null | while read line; do
            echo "  $line"
        done
    fi
    
    # 요약 파일 내용 표시 (있다면)
    SUMMARY_FILE=$(find "$OUTPUT_DIR" -name "*summary*.txt" -type f 2>/dev/null | head -1)
    if [[ -n "$SUMMARY_FILE" ]]; then
        echo ""
        echo -e "${BLUE}📋 요약 리포트:${NC}"
        cat "$SUMMARY_FILE"
    fi
    
else
    echo -e "${RED}❌ 로그 분석에 실패했습니다.${NC}"
    exit 1
fi
