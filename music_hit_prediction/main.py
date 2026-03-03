"""
음악 콘텐츠 흥행 예측 시스템 - CLI 엔트리포인트

사용법:
    # 전체 학습 및 평가
    python -m music_hit_prediction.main train

    # 차트 성적 예측 데모
    python -m music_hit_prediction.main demo-chart

    # 신인 그룹 생존 예측 데모
    python -m music_hit_prediction.main demo-survival

    # API 서버 실행
    python -m music_hit_prediction.main serve

    # 모델 저장/로드
    python -m music_hit_prediction.main train --save-path ./saved_models
"""

import argparse
import json
import sys

import numpy as np
import pandas as pd

from .data.sample_generator import generate_chart_prediction_data, generate_survival_data
from .models.chart_predictor import ChartPredictor
from .models.survival_predictor import SurvivalPredictor
from .models.evaluator import generate_evaluation_report


def train(args):
    """모델 학습 및 평가"""
    print("=" * 70)
    print("  음악 콘텐츠 흥행 예측 시스템 - 모델 학습")
    print("=" * 70)

    # 데이터 생성
    print(f"\n[1/4] 학습 데이터 생성 중... (차트: {args.chart_samples}개, 생존: {args.survival_samples}개)")
    chart_data = generate_chart_prediction_data(n_samples=args.chart_samples)
    survival_data = generate_survival_data(n_samples=args.survival_samples)
    print(f"  차트 데이터: {chart_data.shape}")
    print(f"  생존 데이터: {survival_data.shape}")

    # 연구 1: 차트 예측 학습
    print("\n[2/4] 연구 1: 차트 성적 예측 모델 학습 중 (슈퍼스타 효과)...")
    chart_predictor = ChartPredictor()
    chart_results = chart_predictor.train(chart_data)
    print("  완료!")

    # 연구 2: 생존 예측 학습
    print("\n[3/4] 연구 2: 신인 그룹 생존 예측 모델 학습 중 (롱테일 효과)...")
    survival_predictor = SurvivalPredictor()
    survival_results = survival_predictor.train(survival_data)
    print("  완료!")

    # 평가 보고서
    print("\n[4/4] 평가 보고서 생성 중...")
    report = generate_evaluation_report(chart_results, survival_results)
    print(report)

    # 모델 저장
    if args.save_path:
        print(f"\n모델 저장 중: {args.save_path}")
        chart_predictor.save(args.save_path)
        survival_predictor.save(args.save_path)
        print("  저장 완료!")

    return chart_predictor, survival_predictor


def demo_chart(args):
    """차트 성적 예측 데모"""
    print("=" * 70)
    print("  연구 1: 차트 성적 예측 데모 (슈퍼스타 효과)")
    print("=" * 70)

    # 학습
    chart_data = generate_chart_prediction_data(n_samples=500)
    predictor = ChartPredictor()
    predictor.train(chart_data)

    # 데모 케이스들
    demo_cases = [
        {
            "name": "빅4 기획사 인기 아이돌 컴백",
            "features": {
                "past_streaming_score": 85.0,
                "past_album_score": 90.0,
                "gender": 1,  # female
                "member_count": 5,
                "years_active": 5,
                "total_releases": 12,
                "agency_tier": 2,  # big4
                "agency_artist_count": 25,
                "agency_avg_chart_score": 75.0,
                "distributor_tier": 2,  # major
                "youtube_mv_views": 150_000_000,
                "youtube_content_views": 30_000_000,
                "news_article_count": 350,
                "music_show_appearances": 12,
                "tv_appearances": 15,
                "fan_vote_score": 85.0,
                "fan_community_size": 500_000,
                "social_media_followers": 15_000_000,
                "fancafe_members": 200_000,
            },
        },
        {
            "name": "중견 기획사 신인 보이그룹 데뷔",
            "features": {
                "past_streaming_score": 10.0,
                "past_album_score": 5.0,
                "gender": 0,  # male
                "member_count": 7,
                "years_active": 0,
                "total_releases": 1,
                "agency_tier": 1,  # mid
                "agency_artist_count": 8,
                "agency_avg_chart_score": 35.0,
                "distributor_tier": 1,  # mid
                "youtube_mv_views": 5_000_000,
                "youtube_content_views": 1_000_000,
                "news_article_count": 50,
                "music_show_appearances": 5,
                "tv_appearances": 2,
                "fan_vote_score": 25.0,
                "fan_community_size": 30_000,
                "social_media_followers": 200_000,
                "fancafe_members": 15_000,
            },
        },
        {
            "name": "소형 기획사 솔로 아티스트",
            "features": {
                "past_streaming_score": 5.0,
                "past_album_score": 2.0,
                "gender": 0,  # male
                "member_count": 1,
                "years_active": 1,
                "total_releases": 2,
                "agency_tier": 0,  # small
                "agency_artist_count": 2,
                "agency_avg_chart_score": 8.0,
                "distributor_tier": 0,  # indie
                "youtube_mv_views": 200_000,
                "youtube_content_views": 50_000,
                "news_article_count": 5,
                "music_show_appearances": 1,
                "tv_appearances": 0,
                "fan_vote_score": 3.0,
                "fan_community_size": 2_000,
                "social_media_followers": 10_000,
                "fancafe_members": 500,
            },
        },
    ]

    for case in demo_cases:
        print(f"\n{'─' * 50}")
        print(f"  케이스: {case['name']}")
        print(f"{'─' * 50}")

        features_df = pd.DataFrame([case["features"]])
        result = predictor.predict(features_df)

        print(f"  음원 예측 점수: {result.get('streaming_score', 'N/A'):.2f} / 100")
        print(f"  음원 흥행 여부: {'흥행' if result.get('is_streaming_hit') else '비흥행'}")
        if result.get("streaming_hit_probability") is not None:
            print(f"  음원 흥행 확률: {result['streaming_hit_probability']:.2%}")
        print(f"  음반 예측 점수: {result.get('album_score', 'N/A'):.2f} / 100")
        print(f"  음반 흥행 여부: {'흥행' if result.get('is_album_hit') else '비흥행'}")

        if result.get("feature_importance"):
            print("\n  주요 영향 피처 (슈퍼스타 효과 검증):")
            for fi in result["feature_importance"][:5]:
                print(f"    - {fi['feature']} ({fi['group']}): {fi['importance']:.4f}")


def demo_survival(args):
    """신인 그룹 생존 예측 데모"""
    print("=" * 70)
    print("  연구 2: 신인 그룹 생존 예측 데모 (롱테일 효과)")
    print("=" * 70)

    # 학습
    survival_data = generate_survival_data(n_samples=300)
    predictor = SurvivalPredictor()
    results = predictor.train(survival_data)

    # 기획사 등급별 생존율 출력
    if "survival_by_agency_tier" in results:
        print("\n  기획사 등급별 생존율:")
        for tier, data in results["survival_by_agency_tier"].items():
            bar = "█" * int(data["survival_rate"] * 30)
            print(f"    {tier:>5}: {bar} {data['survival_rate']*100:.1f}% "
                  f"({data['survived']}/{data['count']})")

    # 데모 케이스들
    demo_cases = [
        {
            "name": "빅4 기획사 서바이벌 출신 걸그룹",
            "features": {
                "gender": 1, "member_count": 5, "avg_member_age": 19.5,
                "agency_tier": 2, "agency_debut_history_count": 12,
                "survival_show_origin": 1, "pre_debut_content_count": 35,
                "concept_type": 1, "debut_youtube_views": 50_000_000,
                "debut_news_count": 120, "debut_music_show_wins": 2,
                "initial_fan_vote": 65.0, "initial_community_size": 80_000,
                "debut_week_album_sales": 150_000,
            },
        },
        {
            "name": "중견 기획사 보이그룹",
            "features": {
                "gender": 0, "member_count": 8, "avg_member_age": 20.2,
                "agency_tier": 1, "agency_debut_history_count": 4,
                "survival_show_origin": 0, "pre_debut_content_count": 15,
                "concept_type": 4, "debut_youtube_views": 3_000_000,
                "debut_news_count": 30, "debut_music_show_wins": 0,
                "initial_fan_vote": 18.0, "initial_community_size": 12_000,
                "debut_week_album_sales": 25_000,
            },
        },
        {
            "name": "소형 기획사 신인 걸그룹",
            "features": {
                "gender": 1, "member_count": 6, "avg_member_age": 18.8,
                "agency_tier": 0, "agency_debut_history_count": 0,
                "survival_show_origin": 0, "pre_debut_content_count": 5,
                "concept_type": 0, "debut_youtube_views": 300_000,
                "debut_news_count": 8, "debut_music_show_wins": 0,
                "initial_fan_vote": 5.0, "initial_community_size": 1_500,
                "debut_week_album_sales": 3_000,
            },
        },
    ]

    for case in demo_cases:
        print(f"\n{'─' * 50}")
        print(f"  케이스: {case['name']}")
        print(f"{'─' * 50}")

        features_df = pd.DataFrame([case["features"]])
        result = predictor.predict(features_df)

        survive_text = "생존" if result["will_survive"] else "해체 위험"
        prob = result.get("survival_probability")
        print(f"  3년 생존 예측: {survive_text}")
        if prob is not None:
            print(f"  생존 확률: {prob:.2%}")

        if result.get("protective_factors"):
            print("  보호 요인:")
            for pf in result["protective_factors"]:
                print(f"    + [{pf['impact']}] {pf['factor']}: {pf['description']}")

        if result.get("risk_factors"):
            print("  위험 요인:")
            for rf in result["risk_factors"]:
                print(f"    - [{rf['impact']}] {rf['factor']}: {rf['description']}")


def serve(args):
    """API 서버 실행"""
    import uvicorn
    print("음악 콘텐츠 흥행 예측 API 서버를 시작합니다...")
    print(f"  주소: http://{args.host}:{args.port}")
    print(f"  API 문서: http://{args.host}:{args.port}/docs")
    uvicorn.run(
        "music_hit_prediction.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def main():
    parser = argparse.ArgumentParser(
        description="음악 콘텐츠 흥행 예측 시스템 (박사논문 기반)")

    subparsers = parser.add_subparsers(dest="command", help="실행 명령")

    # train 명령
    train_parser = subparsers.add_parser("train", help="모델 학습 및 평가")
    train_parser.add_argument("--chart-samples", type=int, default=500,
                              help="차트 학습 데이터 수 (기본: 500)")
    train_parser.add_argument("--survival-samples", type=int, default=300,
                              help="생존 학습 데이터 수 (기본: 300)")
    train_parser.add_argument("--save-path", type=str, default=None,
                              help="모델 저장 경로")

    # demo-chart 명령
    subparsers.add_parser("demo-chart", help="차트 성적 예측 데모")

    # demo-survival 명령
    subparsers.add_parser("demo-survival", help="신인 그룹 생존 예측 데모")

    # serve 명령
    serve_parser = subparsers.add_parser("serve", help="API 서버 실행")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "train": train,
        "demo-chart": demo_chart,
        "demo-survival": demo_survival,
        "serve": serve,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
