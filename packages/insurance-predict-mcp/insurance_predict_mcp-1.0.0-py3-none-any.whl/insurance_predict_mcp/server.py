"""
LightGBM Insurance Premium Prediction MCP Server

이 서버는 보험료 예측 모델을 MCP 프로토콜을 통해 노출합니다.
"""

from fastmcp import FastMCP
import joblib
import numpy as np
from pathlib import Path
from typing import Optional

# FastMCP 서버 생성
mcp = FastMCP("Insurance Premium Predictor 🏥")

# 모델 로드 (서버 시작 시 1회만 수행)
# 패키지 내의 모델 파일 경로 찾기
_package_dir = Path(__file__).parent
_model_path = _package_dir / "models" / "lightgbm.pkl"

print(f"모델을 로드합니다... ({_model_path})")
model = joblib.load(_model_path)
feature_names = model.feature_name_
print(f"모델 로드 완료! (특성 개수: {model.n_features_})")


def _predict_insurance_premium_impl(
    age: float,
    annual_income: float,
    number_of_dependents: float,
    health_score: float,
    previous_claims: float,
    vehicle_age: float,
    credit_score: float,
    insurance_duration: float,
) -> dict:
    """
    보험료를 예측합니다.
    
    Args:
        age: 나이 (세)
        annual_income: 연간 소득 (달러)
        number_of_dependents: 부양 가족 수
        health_score: 건강 점수
        previous_claims: 이전 청구 건수
        vehicle_age: 차량 연식 (년)
        credit_score: 신용 점수
        insurance_duration: 보험 기간 (년)
    
    Returns:
        예측된 보험료와 입력 정보를 포함한 딕셔너리
    """
    # 입력된 기본 특성들
    test_data = {
        'age': age,
        'annual_income': annual_income,
        'number_of_dependents': number_of_dependents,
        'health_score': health_score,
        'previous_claims': previous_claims,
        'vehicle_age': vehicle_age,
        'credit_score': credit_score,
        'insurance_duration': insurance_duration,
    }
    
    # 모든 특성을 포함하는 딕셔너리 생성 (누락된 특성은 0으로 초기화)
    input_dict = {}
    for feature in feature_names:
        if feature in test_data:
            input_dict[feature] = test_data[feature]
        else:
            input_dict[feature] = 0.0
    
    # 특성 순서를 모델이 기대하는 순서대로 정렬하여 numpy 배열 생성
    X = np.array([[input_dict[feature] for feature in feature_names]])
    
    # 예측 수행
    prediction = model.predict(X)[0]
    
    return {
        "predicted_premium": round(float(prediction), 2),
        "input_data": test_data,
        "message": f"예측된 보험료는 ${prediction:,.2f} 입니다."
    }


@mcp.tool()
def predict_insurance_premium(
    age: float,
    annual_income: float,
    number_of_dependents: float,
    health_score: float,
    previous_claims: float,
    vehicle_age: float,
    credit_score: float,
    insurance_duration: float,
) -> dict:
    """
    보험료를 예측합니다.
    
    Args:
        age: 나이 (세)
        annual_income: 연간 소득 (달러)
        number_of_dependents: 부양 가족 수
        health_score: 건강 점수
        previous_claims: 이전 청구 건수
        vehicle_age: 차량 연식 (년)
        credit_score: 신용 점수
        insurance_duration: 보험 기간 (년)
    
    Returns:
        예측된 보험료와 입력 정보를 포함한 딕셔너리
    """
    return _predict_insurance_premium_impl(
        age=age,
        annual_income=annual_income,
        number_of_dependents=number_of_dependents,
        health_score=health_score,
        previous_claims=previous_claims,
        vehicle_age=vehicle_age,
        credit_score=credit_score,
        insurance_duration=insurance_duration
    )


def _get_model_info_impl() -> dict:
    """
    모델의 정보를 반환합니다.
    
    Returns:
        모델 특성 개수와 특성 이름 목록
    """
    return {
        "n_features": model.n_features_,
        "feature_names": feature_names,
        "model_type": str(type(model).__name__),
        "required_input_features": [
            "age", "annual_income", "number_of_dependents", 
            "health_score", "previous_claims", "vehicle_age",
            "credit_score", "insurance_duration"
        ]
    }


@mcp.tool()
def get_model_info() -> dict:
    """
    모델의 정보를 반환합니다.
    
    Returns:
        모델 특성 개수와 특성 이름 목록
    """
    return _get_model_info_impl()


if __name__ == "__main__":
    # MCP 서버 실행
    mcp.run()

