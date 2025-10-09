# Insurance Premium Prediction - FastMCP Server

LightGBM 기반 보험료 예측 모델을 [FastMCP](https://gofastmcp.com) 프레임워크를 통해 MCP (Model Context Protocol) 서버로 제공합니다.

## 🚀 FastMCP란?

FastMCP는 MCP 서버와 클라이언트를 빠르고 간단하게 구축할 수 있는 Python 프레임워크입니다. MCP는 "AI를 위한 USB-C 포트"로 불리며, LLM이 데이터와 기능에 표준화된 방식으로 접근할 수 있게 해줍니다.

## 📦 설치

```bash
# 가상환경 생성
uv venv

# 의존성 설치
uv pip install -r requirements.txt
uv pip install fastmcp
```

## 🏥 MCP 서버

### 제공하는 도구 (Tools)

#### 1. `predict_insurance_premium`
보험료를 예측합니다.

**입력 파라미터:**
- `age`: 나이 (세)
- `annual_income`: 연간 소득 (달러)
- `number_of_dependents`: 부양 가족 수
- `health_score`: 건강 점수
- `previous_claims`: 이전 청구 건수
- `vehicle_age`: 차량 연식 (년)
- `credit_score`: 신용 점수
- `insurance_duration`: 보험 기간 (년)

**출력:**
```json
{
  "predicted_premium": 5.64,
  "input_data": { ... },
  "message": "예측된 보험료는 $5.64 입니다."
}
```

#### 2. `get_model_info`
모델의 정보를 반환합니다.

**출력:**
- 모델 특성 개수 (69개)
- 특성 이름 목록
- 모델 타입 (LGBMRegressor)
- 필수 입력 특성 (8개)

## 🧪 테스트 방법

### 1. 간단한 테스트 (Python 스크립트)

```bash
python test_mcp_simple.py
```

이 테스트는 MCP 서버의 함수를 직접 호출하여:
- 모델 정보 조회
- 기본 보험료 예측
- 다양한 시나리오 테스트

### 2. MCP CLI를 사용한 테스트

```bash
# MCP 서버를 stdio 모드로 실행
python serve_mcp.py

# 또는 FastMCP CLI 사용
fastmcp dev serve_mcp.py
```

## 📊 테스트 결과 예시

```
🏥 Insurance Premium Predictor 🏥

📋 등록된 도구:
  1. predict_insurance_premium - 보험료 예측
  2. get_model_info - 모델 정보 조회

💰 테스트 케이스:
  • 나이: 35세
  • 연소득: $42,000
  • 부양가족: 2명
  • 건강 점수: 25.5
  • 이전 청구: 1건
  • 차량 연식: 5년
  • 신용 점수: 700
  • 보험 기간: 3년

📊 예측 결과:
  ✅ 예측된 보험료: $5.64
```

## 🔧 모델 특성

- **모델 타입**: LightGBM Regressor
- **총 특성 수**: 69개
- **필수 입력 특성**: 8개
- **자동 특성 생성**: 나머지 61개 특성은 0으로 자동 초기화

## 📚 참고 자료

- [FastMCP 공식 문서](https://gofastmcp.com)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [LightGBM](https://lightgbm.readthedocs.io/)

## ✅ 테스트 완료 내용

- ✅ 모델 로드 및 정보 조회
- ✅ 보험료 예측 기능
- ✅ 다양한 시나리오 테스트 (저위험, 중위험, 고위험)
- ✅ FastMCP 프레임워크 통합
- ✅ MCP 도구 등록 및 실행

## 🎯 활용 방안

이 MCP 서버는 다음과 같은 AI 어시스턴트와 통합할 수 있습니다:
- Claude Desktop
- ChatGPT
- 기타 MCP 호환 LLM 애플리케이션

AI 어시스턴트가 이 서버에 연결하면, 자연어로 보험료 예측을 요청하고 결과를 받을 수 있습니다.

