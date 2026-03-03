"""
연구 2: 신인 아이돌 그룹 생존 예측 모델 (롱테일 효과 분석)

논문의 연구 2에 기반하여 2018~2020년 데뷔 아이돌 그룹의
3년 후 생존 여부를 예측합니다.

슈퍼스타 효과를 배제한 상태에서 신인 그룹의 생존에 영향을 미치는
요인을 탐색하여 롱테일 효과를 간접적으로 분석합니다.

모델:
- Logistic Regression
- SVM (SVC)
- Decision Tree
- Random Forest
- Gradient Boosting
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from typing import Optional

from ..config import RANDOM_STATE, TEST_SIZE, CV_FOLDS, SURVIVAL_FEATURE_GROUPS
from ..data.preprocessor import create_survival_preprocessor, prepare_survival_data


SURVIVAL_MODELS = {
    "logistic": lambda: LogisticRegression(
        max_iter=1000, random_state=RANDOM_STATE),
    "svc": lambda: SVC(
        kernel="rbf", C=1.0, probability=True, random_state=RANDOM_STATE),
    "decision_tree": lambda: DecisionTreeClassifier(
        max_depth=8, random_state=RANDOM_STATE),
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=100, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1),
    "gradient_boosting": lambda: GradientBoostingClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1, random_state=RANDOM_STATE),
}


class SurvivalPredictor:
    """
    신인 아이돌 그룹 생존 예측기

    데뷔 시점의 다양한 변인을 기반으로 3년 후 생존 여부를 예측합니다.
    롱테일 효과 분석을 위해 기획사 등급별 예측 성능과
    생존에 기여하는 핵심 요인을 분석합니다.
    """

    def __init__(self):
        self.models: dict[str, Pipeline] = {}
        self.best_model_name: Optional[str] = None
        self.feature_names: list[str] = []

    def train(self, df: pd.DataFrame) -> dict:
        """
        전체 학습 파이프라인 실행

        Args:
            df: 학습 데이터프레임

        Returns:
            학습 결과 딕셔너리
        """
        X, y, feature_names = prepare_survival_data(df)
        self.feature_names = feature_names
        preprocessor, _ = create_survival_preprocessor(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)

        results = {}
        best_score = -np.inf

        for name, model_fn in SURVIVAL_MODELS.items():
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model_fn()),
            ])
            pipeline.fit(X_train, y_train)
            self.models[name] = pipeline

            # 교차 검증 (F1, AUC-ROC)
            f1_scores = cross_val_score(
                pipeline, X_train, y_train, cv=CV_FOLDS, scoring="f1")
            auc_scores = cross_val_score(
                pipeline, X_train, y_train, cv=CV_FOLDS, scoring="roc_auc")
            test_accuracy = pipeline.score(X_test, y_test)

            results[name] = {
                "cv_f1_mean": round(float(f1_scores.mean()), 4),
                "cv_f1_std": round(float(f1_scores.std()), 4),
                "cv_auc_mean": round(float(auc_scores.mean()), 4),
                "cv_auc_std": round(float(auc_scores.std()), 4),
                "test_accuracy": round(float(test_accuracy), 4),
            }

            if f1_scores.mean() > best_score:
                best_score = f1_scores.mean()
                self.best_model_name = name

        results["best_model"] = self.best_model_name

        # 기획사 등급별 생존율 분석 (롱테일 효과)
        results["survival_by_agency_tier"] = self._analyze_survival_by_agency(df)

        return results

    def predict(self, input_features: pd.DataFrame) -> dict:
        """
        새로운 데이터에 대한 생존 예측

        Args:
            input_features: 입력 피처 데이터프레임 (1행)

        Returns:
            예측 결과 딕셔너리
        """
        from ..data.preprocessor import apply_log_transform

        if not self.best_model_name or self.best_model_name not in self.models:
            raise ValueError("모델이 학습되지 않았습니다. train()을 먼저 실행하세요.")

        X = apply_log_transform(input_features)
        pipeline = self.models[self.best_model_name]

        prediction = int(pipeline.predict(X)[0])
        proba = None
        try:
            proba = float(pipeline.predict_proba(X)[0][1])
        except Exception:
            pass

        result = {
            "will_survive": bool(prediction),
            "survival_probability": proba,
        }

        # 위험/보호 요인 분석
        risk_factors, protective_factors = self._analyze_factors(input_features)
        result["risk_factors"] = risk_factors
        result["protective_factors"] = protective_factors

        # 피처 중요도
        result["feature_importance"] = self._get_feature_importance()

        return result

    def _analyze_factors(self, input_features: pd.DataFrame) -> tuple[list[dict], list[dict]]:
        """입력 데이터에서 위험 요인과 보호 요인 분석"""
        risk_factors = []
        protective_factors = []

        row = input_features.iloc[0]

        # 기획사 등급
        agency_tier = row.get("agency_tier", 0)
        if agency_tier == 0:
            risk_factors.append({"factor": "소형 기획사", "impact": "high",
                                 "description": "중소 기획사 소속으로 자원 지원이 제한적"})
        elif agency_tier == 2:
            protective_factors.append({"factor": "대형 기획사", "impact": "high",
                                       "description": "빅4 기획사의 체계적 지원과 마케팅 역량"})

        # 서바이벌 프로그램
        if row.get("survival_show_origin", 0):
            protective_factors.append({"factor": "서바이벌 프로그램 출신", "impact": "medium",
                                       "description": "데뷔 전 인지도와 팬덤 확보"})

        # 초기 팬덤
        fan_vote = row.get("initial_fan_vote", 0)
        if fan_vote > 30:
            protective_factors.append({"factor": "높은 초기 팬 투표", "impact": "medium",
                                       "description": f"팬 투표 점수 {fan_vote:.1f}로 안정적 팬덤"})
        elif fan_vote < 10:
            risk_factors.append({"factor": "낮은 초기 팬덤", "impact": "high",
                                 "description": f"팬 투표 점수 {fan_vote:.1f}로 팬덤 기반 약함"})

        # 데뷔 음반 판매량
        sales = row.get("debut_week_album_sales", 0)
        if sales > 50000:
            protective_factors.append({"factor": "높은 초동 판매량", "impact": "medium",
                                       "description": f"첫 주 {sales:,}장으로 시장 관심 확보"})
        elif sales < 5000:
            risk_factors.append({"factor": "낮은 초동 판매량", "impact": "medium",
                                 "description": f"첫 주 {sales:,}장으로 시장 반응 미미"})

        # 음악방송 1위
        wins = row.get("debut_music_show_wins", 0)
        if wins > 0:
            protective_factors.append({"factor": "음악방송 1위", "impact": "high",
                                       "description": f"데뷔 후 {wins}회 1위로 대중 인지도 확보"})

        # 데뷔 전 콘텐츠
        pre_content = row.get("pre_debut_content_count", 0)
        if pre_content > 20:
            protective_factors.append({"factor": "충분한 프리데뷔 콘텐츠", "impact": "low",
                                       "description": f"{pre_content}개 콘텐츠로 데뷔 전 관심 확보"})

        return risk_factors, protective_factors

    def _get_feature_importance(self) -> list[dict]:
        """피처 중요도 추출"""
        importances = []

        for model_name in ["gradient_boosting", "random_forest", "decision_tree"]:
            if model_name in self.models:
                pipeline = self.models[model_name]
                model = pipeline.named_steps["model"]
                if hasattr(model, "feature_importances_"):
                    preprocessor = pipeline.named_steps["preprocessor"]
                    try:
                        feature_names = preprocessor.get_feature_names_out()
                    except Exception:
                        feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]

                    for fname, imp in zip(feature_names, model.feature_importances_):
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
        for group_name, features in SURVIVAL_FEATURE_GROUPS.items():
            for f in features:
                if f in feature_name:
                    return group_name
        return "unknown"

    @staticmethod
    def _analyze_survival_by_agency(df: pd.DataFrame) -> dict:
        """기획사 등급별 생존율 분석 (롱테일 효과 검증)"""
        tier_labels = {0: "small", 1: "mid", 2: "big4"}
        result = {}
        for tier_val, tier_name in tier_labels.items():
            tier_data = df[df["agency_tier"] == tier_val]
            if len(tier_data) > 0:
                survival_rate = tier_data["survived_3_years"].mean()
                result[tier_name] = {
                    "count": int(len(tier_data)),
                    "survival_rate": round(float(survival_rate), 4),
                    "survived": int(tier_data["survived_3_years"].sum()),
                }
        return result

    def save(self, path: str) -> None:
        """모델 저장"""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, save_path / "survival_predictor.joblib")

    @classmethod
    def load(cls, path: str) -> "SurvivalPredictor":
        """모델 로드"""
        return joblib.load(Path(path) / "survival_predictor.joblib")
