"""
FastAPI 기반 예측 API 서버

음악 콘텐츠 흥행 예측 시스템의 REST API를 제공합니다.

엔드포인트:
- POST /predict/chart: 차트 성적 예측 (연구 1)
- POST /predict/survival: 신인 그룹 생존 예측 (연구 2)
- GET /model/status: 모델 상태 확인
- POST /model/train: 모델 재학습
- GET /model/report: 평가 보고서 조회
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import pandas as pd

from ..data.models import (
    ChartPredictionInput, ChartPredictionOutput,
    RookieSurvivalInput, RookieSurvivalOutput,
    Gender, AgencyTier, DistributorTier, ConceptType,
)
from ..data.sample_generator import generate_chart_prediction_data, generate_survival_data
from ..models.chart_predictor import ChartPredictor
from ..models.survival_predictor import SurvivalPredictor
from ..models.evaluator import generate_evaluation_report
from ..config import HIT_THRESHOLD_STREAMING, HIT_THRESHOLD_ALBUM

# 글로벌 모델 인스턴스
chart_predictor: ChartPredictor | None = None
survival_predictor: SurvivalPredictor | None = None
last_training_results: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 시 샘플 데이터로 모델 자동 학습"""
    global chart_predictor, survival_predictor, last_training_results
    print("모델 초기 학습을 시작합니다...")
    chart_predictor, survival_predictor, last_training_results = _train_models()
    print("모델 초기 학습 완료!")
    yield


app = FastAPI(
    title="음악 콘텐츠 흥행 예측 시스템",
    description=(
        "박사논문 '한국 대중음악 산업에서의 음악 콘텐츠 흥행 요인 분석'을 기반으로 구축된 "
        "머신러닝 기반 흥행 예측 API.\n\n"
        "- 연구 1: 슈퍼스타 효과 검증 (음원/음반 차트 성적 예측)\n"
        "- 연구 2: 롱테일 효과 분석 (신인 아이돌 그룹 생존 예측)"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def _train_models() -> tuple[ChartPredictor, SurvivalPredictor, dict]:
    """모델 학습 실행"""
    results = {}

    cp = ChartPredictor()
    chart_data = generate_chart_prediction_data(n_samples=500)
    results["chart"] = cp.train(chart_data)

    sp = SurvivalPredictor()
    survival_data = generate_survival_data(n_samples=300)
    results["survival"] = sp.train(survival_data)

    return cp, sp, results


# ─── 성별/등급 매핑 ───

GENDER_MAP = {Gender.MALE: 0, Gender.FEMALE: 1, Gender.MIXED: 2}
AGENCY_TIER_MAP = {AgencyTier.SMALL: 0, AgencyTier.MID: 1, AgencyTier.BIG4: 2}
DISTRIBUTOR_TIER_MAP = {DistributorTier.INDIE: 0, DistributorTier.MID: 1, DistributorTier.MAJOR: 2}
CONCEPT_TYPE_MAP = {
    ConceptType.CUTE: 0, ConceptType.GIRL_CRUSH: 1, ConceptType.ELEGANT: 2,
    ConceptType.HIP_HOP: 3, ConceptType.PERFORMANCE: 4, ConceptType.VOCAL: 5,
    ConceptType.FRESH: 6, ConceptType.DARK: 7,
}


@app.post("/predict/chart", response_model=ChartPredictionOutput)
async def predict_chart(input_data: ChartPredictionInput):
    """
    연구 1: 차트 성적 예측 (슈퍼스타 효과)

    아티스트 역량, 기획사 역량, 미디어 노출, 팬덤 변인을 기반으로
    음원 및 음반 차트 성적을 예측합니다.
    """
    if chart_predictor is None:
        raise HTTPException(status_code=503, detail="모델이 아직 학습되지 않았습니다.")

    features = pd.DataFrame([{
        "past_streaming_score": input_data.artist.past_streaming_score,
        "past_album_score": input_data.artist.past_album_score,
        "gender": GENDER_MAP[input_data.artist.gender],
        "member_count": input_data.artist.member_count,
        "years_active": input_data.artist.years_active,
        "total_releases": input_data.artist.total_releases,
        "agency_tier": AGENCY_TIER_MAP[input_data.agency.agency_tier],
        "agency_artist_count": input_data.agency.agency_artist_count,
        "agency_avg_chart_score": input_data.agency.agency_avg_chart_score,
        "distributor_tier": DISTRIBUTOR_TIER_MAP[input_data.agency.distributor_tier],
        "youtube_mv_views": input_data.media.youtube_mv_views,
        "youtube_content_views": input_data.media.youtube_content_views,
        "news_article_count": input_data.media.news_article_count,
        "music_show_appearances": input_data.media.music_show_appearances,
        "tv_appearances": input_data.media.tv_appearances,
        "fan_vote_score": input_data.fandom.fan_vote_score,
        "fan_community_size": input_data.fandom.fan_community_size,
        "social_media_followers": input_data.fandom.social_media_followers,
        "fancafe_members": input_data.fandom.fancafe_members,
    }])

    prediction = chart_predictor.predict(features)

    return ChartPredictionOutput(
        artist_name=input_data.artist_name,
        release_title=input_data.release_title,
        predicted_streaming_score=round(prediction.get("streaming_score", 0), 2),
        predicted_album_score=round(prediction.get("album_score", 0), 2),
        is_streaming_hit=prediction.get("is_streaming_hit", False),
        is_album_hit=prediction.get("is_album_hit", False),
        hit_probability=round(prediction.get("streaming_hit_probability", 0), 4),
        top_contributing_features=prediction.get("feature_importance", []),
    )


@app.post("/predict/survival", response_model=RookieSurvivalOutput)
async def predict_survival(input_data: RookieSurvivalInput):
    """
    연구 2: 신인 그룹 생존 예측 (롱테일 효과)

    데뷔 시점의 기획사, 아티스트, 미디어, 팬덤 변인을 기반으로
    3년 후 생존 여부를 예측합니다.
    """
    if survival_predictor is None:
        raise HTTPException(status_code=503, detail="모델이 아직 학습되지 않았습니다.")

    features = pd.DataFrame([{
        "gender": GENDER_MAP[input_data.gender],
        "member_count": input_data.member_count,
        "avg_member_age": input_data.avg_member_age,
        "agency_tier": AGENCY_TIER_MAP[input_data.agency_tier],
        "agency_debut_history_count": input_data.agency_debut_history_count,
        "survival_show_origin": int(input_data.survival_show_origin),
        "pre_debut_content_count": input_data.pre_debut_content_count,
        "concept_type": CONCEPT_TYPE_MAP[input_data.concept_type],
        "debut_youtube_views": input_data.debut_youtube_views,
        "debut_news_count": input_data.debut_news_count,
        "debut_music_show_wins": input_data.debut_music_show_wins,
        "initial_fan_vote": input_data.initial_fan_vote,
        "initial_community_size": input_data.initial_community_size,
        "debut_week_album_sales": input_data.debut_week_album_sales,
    }])

    prediction = survival_predictor.predict(features)

    return RookieSurvivalOutput(
        group_name=input_data.group_name,
        survival_probability=round(prediction.get("survival_probability", 0), 4),
        will_survive=prediction.get("will_survive", False),
        risk_factors=prediction.get("risk_factors", []),
        protective_factors=prediction.get("protective_factors", []),
    )


@app.get("/model/status")
async def model_status():
    """모델 상태 확인"""
    return {
        "chart_predictor": {
            "loaded": chart_predictor is not None,
            "best_streaming_reg": chart_predictor.best_streaming_reg_model if chart_predictor else None,
            "best_streaming_clf": chart_predictor.best_streaming_clf_model if chart_predictor else None,
            "best_album_reg": chart_predictor.best_album_reg_model if chart_predictor else None,
            "best_album_clf": chart_predictor.best_album_clf_model if chart_predictor else None,
        },
        "survival_predictor": {
            "loaded": survival_predictor is not None,
            "best_model": survival_predictor.best_model_name if survival_predictor else None,
        },
    }


@app.post("/model/train")
async def retrain_models(chart_samples: int = 500, survival_samples: int = 300):
    """모델 재학습 (샘플 데이터 기반)"""
    global chart_predictor, survival_predictor, last_training_results
    chart_predictor, survival_predictor, last_training_results = _train_models()
    return {"status": "success", "results": last_training_results}


@app.get("/model/report")
async def get_report():
    """평가 보고서 조회"""
    report = generate_evaluation_report(
        chart_results=last_training_results.get("chart"),
        survival_results=last_training_results.get("survival"),
    )
    return {"report": report}
