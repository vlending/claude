"""
모델 평가 모듈

분류 및 회귀 모델의 성능을 종합적으로 평가합니다.
- 분류: Accuracy, Precision, Recall, F1-Score, AUC-ROC
- 회귀: R², MAE, RMSE
- 피처 그룹별 기여도 분석 (슈퍼스타/롱테일 효과 검증)
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score,
)
from sklearn.model_selection import train_test_split
from typing import Optional

from ..config import RANDOM_STATE, TEST_SIZE


def evaluate_classifier(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    model_name: str = "model",
) -> dict:
    """
    분류 모델 평가

    Args:
        pipeline: 학습된 sklearn Pipeline
        X: 피처 데이터
        y: 타겟 데이터
        model_name: 모델 이름 (결과 표시용)

    Returns:
        평가 결과 딕셔너리
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)

    y_pred = pipeline.predict(X_test)

    result = {
        "model": model_name,
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
    }

    # AUC-ROC (확률 예측 가능 시)
    try:
        y_proba = pipeline.predict_proba(X_test)[:, 1]
        result["auc_roc"] = round(float(roc_auc_score(y_test, y_proba)), 4)
    except Exception:
        result["auc_roc"] = None

    # 혼동 행렬
    cm = confusion_matrix(y_test, y_pred)
    result["confusion_matrix"] = {
        "true_negative": int(cm[0][0]),
        "false_positive": int(cm[0][1]),
        "false_negative": int(cm[1][0]),
        "true_positive": int(cm[1][1]),
    }

    return result


def evaluate_regressor(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    model_name: str = "model",
) -> dict:
    """
    회귀 모델 평가

    Args:
        pipeline: 학습된 sklearn Pipeline
        X: 피처 데이터
        y: 타겟 데이터
        model_name: 모델 이름

    Returns:
        평가 결과 딕셔너리
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

    y_pred = pipeline.predict(X_test)

    result = {
        "model": model_name,
        "r2": round(float(r2_score(y_test, y_pred)), 4),
        "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
    }

    return result


def analyze_feature_group_importance(
    feature_importances: list[dict],
    feature_groups: dict,
) -> dict:
    """
    피처 그룹별 중요도 집계 (슈퍼스타/롱테일 효과 분석)

    논문의 독립변수 그룹(아티스트 역량, 기획사 역량, 미디어 노출, 팬덤)별로
    피처 중요도를 집계하여 어떤 요인 그룹이 흥행에 가장 큰 영향을 미치는지 분석합니다.

    Args:
        feature_importances: 개별 피처 중요도 목록
        feature_groups: 피처 그룹 정의 (config에서 가져옴)

    Returns:
        그룹별 중요도 딕셔너리
    """
    group_scores = {group: 0.0 for group in feature_groups}
    group_counts = {group: 0 for group in feature_groups}

    for fi in feature_importances:
        for group_name, features in feature_groups.items():
            for f in features:
                if f in fi["feature"]:
                    group_scores[group_name] += fi["importance"]
                    group_counts[group_name] += 1
                    break

    total = sum(group_scores.values())
    result = {}
    for group in feature_groups:
        score = group_scores[group]
        result[group] = {
            "total_importance": round(score, 4),
            "percentage": round(score / total * 100, 2) if total > 0 else 0,
            "feature_count": group_counts[group],
        }

    return result


def generate_evaluation_report(
    chart_results: Optional[dict] = None,
    survival_results: Optional[dict] = None,
) -> str:
    """
    종합 평가 보고서 생성

    Args:
        chart_results: 차트 예측 모델 학습 결과
        survival_results: 생존 예측 모델 학습 결과

    Returns:
        포맷팅된 보고서 문자열
    """
    lines = []
    lines.append("=" * 70)
    lines.append("  음악 콘텐츠 흥행 예측 시스템 - 모델 평가 보고서")
    lines.append("=" * 70)

    if chart_results:
        lines.append("\n[연구 1] 슈퍼스타 효과 검증 - 차트 성적 예측")
        lines.append("-" * 50)

        for task_name, task_key in [
            ("음원 성적 회귀", "streaming_regression"),
            ("음원 성적 분류", "streaming_classification"),
            ("음반 성적 회귀", "album_regression"),
            ("음반 성적 분류", "album_classification"),
        ]:
            if task_key in chart_results:
                task = chart_results[task_key]
                best = task.get("best_model", "N/A")
                lines.append(f"\n  {task_name} (최적 모델: {best})")

                for model_name, metrics in task.items():
                    if model_name == "best_model":
                        continue
                    if isinstance(metrics, dict):
                        marker = " *" if model_name == best else "  "
                        metric_str = ", ".join(
                            f"{k}: {v}" for k, v in metrics.items())
                        lines.append(f"  {marker} {model_name}: {metric_str}")

    if survival_results:
        lines.append("\n\n[연구 2] 롱테일 효과 분석 - 신인 그룹 생존 예측")
        lines.append("-" * 50)

        best = survival_results.get("best_model", "N/A")
        lines.append(f"  최적 모델: {best}")

        for model_name, metrics in survival_results.items():
            if model_name in ("best_model", "survival_by_agency_tier"):
                continue
            if isinstance(metrics, dict):
                marker = " *" if model_name == best else "  "
                metric_str = ", ".join(
                    f"{k}: {v}" for k, v in metrics.items())
                lines.append(f"  {marker} {model_name}: {metric_str}")

        # 기획사 등급별 생존율
        if "survival_by_agency_tier" in survival_results:
            lines.append("\n  기획사 등급별 생존율 (롱테일 효과 지표):")
            for tier, data in survival_results["survival_by_agency_tier"].items():
                lines.append(
                    f"    {tier}: {data['survival_rate']*100:.1f}% "
                    f"({data['survived']}/{data['count']})")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
