"""
데이터 전처리 파이프라인

논문의 변인 구조에 맞게 원시 데이터를 모델 입력 형태로 변환합니다.
- 수치형 변수: StandardScaler 정규화
- 범주형 변수: One-Hot 인코딩
- 로그 변환: 조회수, 팔로워 수 등 우편향 분포 변수
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from typing import Tuple

from ..config import (
    CHART_FEATURE_GROUPS,
    SURVIVAL_FEATURE_GROUPS,
    HIT_THRESHOLD_STREAMING,
    HIT_THRESHOLD_ALBUM,
)


# 로그 변환 대상 피처
LOG_TRANSFORM_FEATURES = [
    "youtube_mv_views",
    "youtube_content_views",
    "fan_community_size",
    "social_media_followers",
    "fancafe_members",
    "debut_youtube_views",
    "initial_community_size",
    "debut_week_album_sales",
]


def _get_all_features(feature_groups: dict) -> list[str]:
    """피처 그룹에서 전체 피처 목록 추출"""
    features = []
    for group in feature_groups.values():
        features.extend(group)
    return features


def apply_log_transform(df: pd.DataFrame) -> pd.DataFrame:
    """우편향 분포 변수에 log1p 변환 적용"""
    df = df.copy()
    for col in LOG_TRANSFORM_FEATURES:
        if col in df.columns:
            df[col] = np.log1p(df[col].astype(float))
    return df


def create_chart_preprocessor(df: pd.DataFrame) -> Tuple[ColumnTransformer, list[str]]:
    """
    연구 1: 차트 성적 예측용 전처리기 생성

    Returns:
        (전처리기, 피처 목록)
    """
    all_features = _get_all_features(CHART_FEATURE_GROUPS)
    available_features = [f for f in all_features if f in df.columns]

    categorical_features = ["gender", "agency_tier", "distributor_tier"]
    categorical_available = [f for f in categorical_features if f in available_features]
    numerical_features = [f for f in available_features if f not in categorical_features]

    transformers = []
    if numerical_features:
        transformers.append(("num", StandardScaler(), numerical_features))
    if categorical_available:
        transformers.append(
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="infrequent_if_exist"),
             categorical_available)
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor, available_features


def create_survival_preprocessor(df: pd.DataFrame) -> Tuple[ColumnTransformer, list[str]]:
    """
    연구 2: 신인 생존 예측용 전처리기 생성

    Returns:
        (전처리기, 피처 목록)
    """
    all_features = _get_all_features(SURVIVAL_FEATURE_GROUPS)
    available_features = [f for f in all_features if f in df.columns]

    categorical_features = ["gender", "agency_tier", "concept_type"]
    categorical_available = [f for f in categorical_features if f in available_features]
    numerical_features = [f for f in available_features if f not in categorical_features]

    transformers = []
    if numerical_features:
        transformers.append(("num", StandardScaler(), numerical_features))
    if categorical_available:
        transformers.append(
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="infrequent_if_exist"),
             categorical_available)
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor, available_features


def prepare_chart_data(
    df: pd.DataFrame,
    target: str = "streaming_score",
    as_classification: bool = False,
) -> Tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    연구 1: 차트 데이터 준비

    Args:
        df: 원시 데이터프레임
        target: 종속변수 ("streaming_score" 또는 "album_score")
        as_classification: True이면 흥행/비흥행 이진 분류로 변환

    Returns:
        (피처 데이터프레임, 타겟 시리즈, 피처 이름 목록)
    """
    all_features = _get_all_features(CHART_FEATURE_GROUPS)
    available_features = [f for f in all_features if f in df.columns]

    X = df[available_features].copy()
    X = apply_log_transform(X)

    if as_classification:
        threshold = (HIT_THRESHOLD_STREAMING if target == "streaming_score"
                     else HIT_THRESHOLD_ALBUM)
        y = (df[target] >= np.percentile(df[target], threshold)).astype(int)
    else:
        y = df[target].copy()

    return X, y, available_features


def prepare_survival_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    연구 2: 생존 데이터 준비

    Returns:
        (피처 데이터프레임, 타겟 시리즈, 피처 이름 목록)
    """
    all_features = _get_all_features(SURVIVAL_FEATURE_GROUPS)
    available_features = [f for f in all_features if f in df.columns]

    X = df[available_features].copy()
    X = apply_log_transform(X)
    y = df["survived_3_years"].copy()

    return X, y, available_features
