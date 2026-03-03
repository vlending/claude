"""
연구 1: 차트 성적 예측 모델 (슈퍼스타 효과 검증)

논문의 연구 1에 기반하여 음원/음반 차트 성적을 예측합니다.
- 회귀 모델: 정확한 성적 점수 예측 (0-100)
- 분류 모델: 흥행/비흥행 이진 분류

모델:
- SVM (Support Vector Machine)
- Decision Tree
- Random Forest
- Gradient Boosting
- Ridge/Logistic Regression (기준 모델)

슈퍼스타 효과 검증을 위해 피처 중요도 분석을 수행합니다.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR, SVC
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
)
from sklearn.linear_model import Ridge, LogisticRegression
from typing import Optional

from ..config import RANDOM_STATE, TEST_SIZE, CV_FOLDS, CHART_FEATURE_GROUPS
from ..data.preprocessor import (
    create_chart_preprocessor,
    prepare_chart_data,
)


# 사용 가능한 모델 정의
REGRESSION_MODELS = {
    "ridge": lambda: Ridge(alpha=1.0),
    "svr": lambda: SVR(kernel="rbf", C=1.0),
    "decision_tree": lambda: DecisionTreeRegressor(
        max_depth=10, random_state=RANDOM_STATE),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=-1),
    "gradient_boosting": lambda: GradientBoostingRegressor(
        n_estimators=100, max_depth=5, learning_rate=0.1, random_state=RANDOM_STATE),
}

CLASSIFICATION_MODELS = {
    "logistic": lambda: LogisticRegression(
        max_iter=1000, random_state=RANDOM_STATE),
    "svc": lambda: SVC(kernel="rbf", C=1.0, probability=True, random_state=RANDOM_STATE),
    "decision_tree": lambda: DecisionTreeClassifier(
        max_depth=10, random_state=RANDOM_STATE),
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=-1),
    "gradient_boosting": lambda: GradientBoostingClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1, random_state=RANDOM_STATE),
}


class ChartPredictor:
    """
    차트 성적 예측기

    음원 성적과 음반 성적을 각각 예측하며,
    회귀(점수 예측)와 분류(흥행 여부) 두 가지 모드를 지원합니다.
    """

    def __init__(self):
        self.streaming_regression_models: dict[str, Pipeline] = {}
        self.streaming_classification_models: dict[str, Pipeline] = {}
        self.album_regression_models: dict[str, Pipeline] = {}
        self.album_classification_models: dict[str, Pipeline] = {}
        self.best_streaming_reg_model: Optional[str] = None
        self.best_streaming_clf_model: Optional[str] = None
        self.best_album_reg_model: Optional[str] = None
        self.best_album_clf_model: Optional[str] = None
        self.feature_names: list[str] = []
        self._preprocessor = None

    def train(self, df: pd.DataFrame) -> dict:
        """
        전체 학습 파이프라인 실행

        Args:
            df: 학습 데이터프레임

        Returns:
            학습 결과 딕셔너리 (모델별 성능)
        """
        results = {}

        # 음원 성적 예측 (회귀)
        results["streaming_regression"] = self._train_regression(
            df, target="streaming_score", store="streaming")

        # 음원 성적 예측 (분류)
        results["streaming_classification"] = self._train_classification(
            df, target="streaming_score", store="streaming")

        # 음반 성적 예측 (회귀)
        results["album_regression"] = self._train_regression(
            df, target="album_score", store="album")

        # 음반 성적 예측 (분류)
        results["album_classification"] = self._train_classification(
            df, target="album_score", store="album")

        return results

    def _train_regression(self, df: pd.DataFrame, target: str, store: str) -> dict:
        """회귀 모델 학습"""
        X, y, feature_names = prepare_chart_data(df, target=target, as_classification=False)
        self.feature_names = feature_names
        preprocessor, _ = create_chart_preprocessor(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

        model_store = (self.streaming_regression_models if store == "streaming"
                       else self.album_regression_models)
        results = {}
        best_score = -np.inf
        best_name = None

        for name, model_fn in REGRESSION_MODELS.items():
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model_fn()),
            ])
            pipeline.fit(X_train, y_train)
            model_store[name] = pipeline

            # 교차 검증 (R² 점수)
            cv_scores = cross_val_score(
                pipeline, X_train, y_train, cv=CV_FOLDS, scoring="r2")
            test_score = pipeline.score(X_test, y_test)

            results[name] = {
                "cv_r2_mean": round(float(cv_scores.mean()), 4),
                "cv_r2_std": round(float(cv_scores.std()), 4),
                "test_r2": round(float(test_score), 4),
            }

            if cv_scores.mean() > best_score:
                best_score = cv_scores.mean()
                best_name = name

        if store == "streaming":
            self.best_streaming_reg_model = best_name
        else:
            self.best_album_reg_model = best_name

        results["best_model"] = best_name
        return results

    def _train_classification(self, df: pd.DataFrame, target: str, store: str) -> dict:
        """분류 모델 학습"""
        X, y, _ = prepare_chart_data(df, target=target, as_classification=True)
        preprocessor, _ = create_chart_preprocessor(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

        model_store = (self.streaming_classification_models if store == "streaming"
                       else self.album_classification_models)
        results = {}
        best_score = -np.inf
        best_name = None

        for name, model_fn in CLASSIFICATION_MODELS.items():
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model_fn()),
            ])
            pipeline.fit(X_train, y_train)
            model_store[name] = pipeline

            cv_scores = cross_val_score(
                pipeline, X_train, y_train, cv=CV_FOLDS, scoring="f1")
            test_score = pipeline.score(X_test, y_test)

            results[name] = {
                "cv_f1_mean": round(float(cv_scores.mean()), 4),
                "cv_f1_std": round(float(cv_scores.std()), 4),
                "test_accuracy": round(float(test_score), 4),
            }

            if cv_scores.mean() > best_score:
                best_score = cv_scores.mean()
                best_name = name

        if store == "streaming":
            self.best_streaming_clf_model = best_name
        else:
            self.best_album_clf_model = best_name

        results["best_model"] = best_name
        return results

    def predict(self, input_features: pd.DataFrame) -> dict:
        """
        새로운 데이터에 대한 예측 수행

        Args:
            input_features: 입력 피처 데이터프레임 (1행)

        Returns:
            예측 결과 딕셔너리
        """
        from ..data.preprocessor import apply_log_transform
        X = apply_log_transform(input_features)

        result = {}

        # 음원 성적 예측
        if self.best_streaming_reg_model and self.best_streaming_reg_model in self.streaming_regression_models:
            reg_model = self.streaming_regression_models[self.best_streaming_reg_model]
            result["streaming_score"] = float(np.clip(reg_model.predict(X)[0], 0, 100))

        if self.best_streaming_clf_model and self.best_streaming_clf_model in self.streaming_classification_models:
            clf_model = self.streaming_classification_models[self.best_streaming_clf_model]
            result["is_streaming_hit"] = bool(clf_model.predict(X)[0])
            if hasattr(clf_model, "predict_proba"):
                try:
                    result["streaming_hit_probability"] = float(
                        clf_model.predict_proba(X)[0][1])
                except Exception:
                    pass

        # 음반 성적 예측
        if self.best_album_reg_model and self.best_album_reg_model in self.album_regression_models:
            reg_model = self.album_regression_models[self.best_album_reg_model]
            result["album_score"] = float(np.clip(reg_model.predict(X)[0], 0, 100))

        if self.best_album_clf_model and self.best_album_clf_model in self.album_classification_models:
            clf_model = self.album_classification_models[self.best_album_clf_model]
            result["is_album_hit"] = bool(clf_model.predict(X)[0])
            if hasattr(clf_model, "predict_proba"):
                try:
                    result["album_hit_probability"] = float(
                        clf_model.predict_proba(X)[0][1])
                except Exception:
                    pass

        # 피처 중요도 분석 (슈퍼스타 효과 검증)
        result["feature_importance"] = self._get_feature_importance()

        return result

    def _get_feature_importance(self) -> list[dict]:
        """
        피처 중요도 추출 (슈퍼스타 효과 검증용)

        트리 기반 모델의 feature_importances_ 사용
        """
        importances = []

        # streaming regression에서 가장 좋은 트리 기반 모델 찾기
        for model_name in ["gradient_boosting", "random_forest", "decision_tree"]:
            if model_name in self.streaming_regression_models:
                pipeline = self.streaming_regression_models[model_name]
                model = pipeline.named_steps["model"]
                if hasattr(model, "feature_importances_"):
                    preprocessor = pipeline.named_steps["preprocessor"]
                    try:
                        feature_names = preprocessor.get_feature_names_out()
                    except Exception:
                        feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]

                    for fname, imp in zip(feature_names, model.feature_importances_):
                        # 피처 그룹 매핑
                        group = self._get_feature_group(str(fname))
                        importances.append({
                            "feature": str(fname),
                            "importance": round(float(imp), 4),
                            "group": group,
                        })

                    importances.sort(key=lambda x: x["importance"], reverse=True)
                    return importances[:10]

        return importances

    @staticmethod
    def _get_feature_group(feature_name: str) -> str:
        """피처가 속한 그룹명 반환"""
        for group_name, features in CHART_FEATURE_GROUPS.items():
            for f in features:
                if f in feature_name:
                    return group_name
        return "unknown"

    def save(self, path: str) -> None:
        """모델 저장"""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, save_path / "chart_predictor.joblib")

    @classmethod
    def load(cls, path: str) -> "ChartPredictor":
        """모델 로드"""
        return joblib.load(Path(path) / "chart_predictor.joblib")
