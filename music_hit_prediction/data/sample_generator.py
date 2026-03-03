"""
샘플 데이터 생성기

논문의 변인 구조를 반영한 가상의 학습 데이터를 생성합니다.
실제 데이터(써클차트, 뮤빗, 유튜브 등)를 대체하여 시스템 검증에 사용됩니다.

슈퍼스타 효과와 롱테일 효과를 반영한 현실적인 분포를 생성합니다:
- 슈퍼스타 효과: 소수의 빅4 기획사 아티스트가 높은 성적 집중
- 롱테일 효과: 다수의 중소 기획사 아티스트가 긴 꼬리 분포 형성
"""

import numpy as np
import pandas as pd
from ..config import RANDOM_STATE


def generate_chart_prediction_data(n_samples: int = 500) -> pd.DataFrame:
    """
    연구 1: 차트 성적 예측용 데이터 생성

    슈퍼스타 효과를 반영하여 소수의 아티스트에 성적이 집중되는 분포를 모사합니다.
    """
    rng = np.random.default_rng(RANDOM_STATE)

    # 기획사 등급 (big4: 15%, mid: 30%, small: 55%)
    agency_tier = rng.choice([2, 1, 0], size=n_samples, p=[0.15, 0.30, 0.55])

    # 유통사 등급
    distributor_tier = np.where(
        agency_tier == 2,
        rng.choice([2, 1], size=n_samples, p=[0.8, 0.2]),
        np.where(
            agency_tier == 1,
            rng.choice([2, 1, 0], size=n_samples, p=[0.3, 0.5, 0.2]),
            rng.choice([1, 0], size=n_samples, p=[0.3, 0.7]),
        ),
    )

    # 성별 (0: male, 1: female, 2: mixed)
    gender = rng.choice([0, 1, 2], size=n_samples, p=[0.45, 0.40, 0.15])

    # 멤버 수
    member_count = np.where(
        gender == 2,
        rng.integers(1, 3, size=n_samples),
        rng.choice([1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], size=n_samples,
                   p=[0.1, 0.1, 0.15, 0.15, 0.15, 0.1, 0.08, 0.07, 0.04, 0.03, 0.03]),
    )

    # 활동 연차
    years_active = rng.integers(0, 20, size=n_samples)

    # 총 발매 작품 수
    total_releases = (years_active * rng.integers(1, 4, size=n_samples) +
                      rng.integers(0, 3, size=n_samples))

    # 기획사 소속 아티스트 수
    agency_artist_count = np.where(
        agency_tier == 2, rng.integers(10, 50, size=n_samples),
        np.where(agency_tier == 1, rng.integers(3, 15, size=n_samples),
                 rng.integers(1, 5, size=n_samples)))

    # 기획사 평균 차트 성적
    agency_avg_chart = np.where(
        agency_tier == 2, rng.uniform(50, 90, size=n_samples),
        np.where(agency_tier == 1, rng.uniform(20, 60, size=n_samples),
                 rng.uniform(0, 30, size=n_samples)))

    # 과거 음원 성적 (슈퍼스타 효과: 기획사 등급 + 과거 경험 반영)
    base_streaming = (agency_tier * 15 + years_active * 1.5 +
                      rng.normal(0, 10, size=n_samples))
    past_streaming = np.clip(base_streaming, 0, 100)

    # 과거 음반 성적
    base_album = (agency_tier * 18 + years_active * 1.2 +
                  member_count * 0.5 + rng.normal(0, 12, size=n_samples))
    past_album = np.clip(base_album, 0, 100)

    # 유튜브 MV 조회수 (log-normal 분포 + 기획사 효과)
    mv_log_base = 4 + agency_tier * 1.5 + past_streaming * 0.02
    youtube_mv_views = np.exp(mv_log_base + rng.normal(0, 0.8, size=n_samples)).astype(int)

    # 유튜브 콘텐츠 조회수
    content_log_base = 3.5 + agency_tier * 1.2 + past_album * 0.015
    youtube_content_views = np.exp(content_log_base + rng.normal(0, 0.7, size=n_samples)).astype(int)

    # 기사 노출 수
    news_base = agency_tier * 30 + years_active * 2 + rng.exponential(10, size=n_samples)
    news_article_count = np.clip(news_base, 0, 500).astype(int)

    # 음악방송 출연 횟수
    music_show = np.where(
        agency_tier == 2, rng.integers(3, 15, size=n_samples),
        np.where(agency_tier == 1, rng.integers(1, 10, size=n_samples),
                 rng.integers(0, 5, size=n_samples)))

    # TV 출연 횟수
    tv_appearances = np.where(
        agency_tier == 2, rng.integers(0, 20, size=n_samples),
        np.where(agency_tier == 1, rng.integers(0, 8, size=n_samples),
                 rng.integers(0, 3, size=n_samples)))

    # 팬 투표 점수 (power-law 분포: 슈퍼스타 효과)
    fan_vote_base = (agency_tier * 20 + past_album * 0.3 +
                     member_count * 0.8 + rng.exponential(8, size=n_samples))
    fan_vote_score = np.clip(fan_vote_base, 0, 100)

    # 팬 커뮤니티 규모
    community_base = np.exp(
        6 + agency_tier * 1.0 + years_active * 0.1 + rng.normal(0, 1, size=n_samples))
    fan_community_size = community_base.astype(int)

    # 소셜미디어 팔로워
    social_base = np.exp(
        7 + agency_tier * 1.5 + years_active * 0.15 + rng.normal(0, 1.2, size=n_samples))
    social_media_followers = social_base.astype(int)

    # 팬카페 회원
    fancafe_base = np.exp(
        5 + agency_tier * 0.8 + years_active * 0.12 + rng.normal(0, 0.9, size=n_samples))
    fancafe_members = fancafe_base.astype(int)

    # ─── 종속변수 생성 ───
    # 음원 성적 (슈퍼스타 효과 반영)
    streaming_score = (
        past_streaming * 0.25 +
        agency_tier * 8 +
        np.log1p(youtube_mv_views) * 2.0 +
        np.log1p(news_article_count) * 1.5 +
        fan_vote_score * 0.15 +
        np.log1p(social_media_followers) * 1.0 +
        music_show * 0.5 +
        rng.normal(0, 5, size=n_samples)
    )
    streaming_score = np.clip(
        (streaming_score - streaming_score.min()) /
        (streaming_score.max() - streaming_score.min()) * 100,
        0, 100,
    )

    # 음반 성적 (팬덤 효과가 더 강함)
    album_score = (
        past_album * 0.20 +
        agency_tier * 10 +
        fan_vote_score * 0.30 +
        np.log1p(fan_community_size) * 2.5 +
        np.log1p(fancafe_members) * 1.5 +
        member_count * 0.3 +
        rng.normal(0, 6, size=n_samples)
    )
    album_score = np.clip(
        (album_score - album_score.min()) /
        (album_score.max() - album_score.min()) * 100,
        0, 100,
    )

    df = pd.DataFrame({
        "past_streaming_score": np.round(past_streaming, 2),
        "past_album_score": np.round(past_album, 2),
        "gender": gender,
        "member_count": member_count,
        "years_active": years_active,
        "total_releases": total_releases,
        "agency_tier": agency_tier,
        "agency_artist_count": agency_artist_count,
        "agency_avg_chart_score": np.round(agency_avg_chart, 2),
        "distributor_tier": distributor_tier,
        "youtube_mv_views": youtube_mv_views,
        "youtube_content_views": youtube_content_views,
        "news_article_count": news_article_count,
        "music_show_appearances": music_show,
        "tv_appearances": tv_appearances,
        "fan_vote_score": np.round(fan_vote_score, 2),
        "fan_community_size": fan_community_size,
        "social_media_followers": social_media_followers,
        "fancafe_members": fancafe_members,
        "streaming_score": np.round(streaming_score, 2),
        "album_score": np.round(album_score, 2),
    })

    return df


def generate_survival_data(n_samples: int = 300) -> pd.DataFrame:
    """
    연구 2: 신인 아이돌 그룹 생존 예측용 데이터 생성

    2018~2020년 데뷔 그룹을 모사하며, 3년 후 생존 여부를 포함합니다.
    롱테일 효과를 반영하여 중소 기획사 그룹의 다양한 생존 패턴을 생성합니다.
    """
    rng = np.random.default_rng(RANDOM_STATE + 1)

    # 기획사 등급 (신인 그룹: big4 10%, mid 25%, small 65%)
    agency_tier = rng.choice([2, 1, 0], size=n_samples, p=[0.10, 0.25, 0.65])

    # 기획사 과거 데뷔 그룹 수
    agency_debut_history = np.where(
        agency_tier == 2, rng.integers(5, 20, size=n_samples),
        np.where(agency_tier == 1, rng.integers(2, 8, size=n_samples),
                 rng.integers(0, 3, size=n_samples)))

    # 성별
    gender = rng.choice([0, 1], size=n_samples, p=[0.55, 0.45])

    # 멤버 수
    member_count = rng.choice(
        [4, 5, 6, 7, 8, 9, 10, 11, 12],
        size=n_samples,
        p=[0.08, 0.15, 0.15, 0.18, 0.12, 0.1, 0.1, 0.07, 0.05],
    )

    # 평균 나이
    avg_age = rng.uniform(16, 25, size=n_samples)

    # 서바이벌 프로그램 출신
    survival_show = rng.choice([0, 1], size=n_samples, p=[0.75, 0.25])

    # 데뷔 전 콘텐츠 수
    pre_debut_content = np.where(
        agency_tier >= 1, rng.integers(5, 50, size=n_samples),
        rng.integers(0, 15, size=n_samples))

    # 콘셉트 유형 (0-7)
    concept_type = rng.integers(0, 8, size=n_samples)

    # 데뷔곡 유튜브 조회수
    debut_yt_base = 4 + agency_tier * 1.5 + survival_show * 1.0
    debut_youtube_views = np.exp(
        debut_yt_base + rng.normal(0, 0.8, size=n_samples)).astype(int)

    # 데뷔 시 기사 수
    debut_news = np.where(
        agency_tier == 2, rng.integers(30, 150, size=n_samples),
        np.where(agency_tier == 1, rng.integers(10, 60, size=n_samples),
                 rng.integers(0, 20, size=n_samples)))
    debut_news += survival_show * rng.integers(10, 40, size=n_samples)

    # 음악방송 1위 횟수 (데뷔 첫 해)
    debut_wins = np.where(
        agency_tier == 2, rng.choice([0, 1, 2, 3], size=n_samples, p=[0.2, 0.3, 0.3, 0.2]),
        np.where(agency_tier == 1,
                 rng.choice([0, 1, 2], size=n_samples, p=[0.5, 0.35, 0.15]),
                 rng.choice([0, 1], size=n_samples, p=[0.9, 0.1])))

    # 초기 팬 투표
    fan_vote_base = (agency_tier * 15 + survival_show * 20 +
                     rng.exponential(8, size=n_samples))
    initial_fan_vote = np.clip(fan_vote_base, 0, 100)

    # 초기 커뮤니티 규모
    community_base = np.exp(
        5 + agency_tier * 1.2 + survival_show * 0.8 + rng.normal(0, 1, size=n_samples))
    initial_community_size = community_base.astype(int)

    # 데뷔 첫 주 음반 판매량
    album_base = np.exp(
        6 + agency_tier * 1.5 + initial_fan_vote * 0.02 + rng.normal(0, 1, size=n_samples))
    debut_week_sales = album_base.astype(int)

    # ─── 종속변수: 3년 생존 여부 ───
    survival_logit = (
        agency_tier * 1.2 +
        survival_show * 0.8 +
        np.log1p(debut_youtube_views) * 0.15 +
        np.log1p(initial_community_size) * 0.25 +
        np.log1p(debut_week_sales) * 0.2 +
        debut_wins * 0.5 +
        np.log1p(debut_news) * 0.1 +
        pre_debut_content * 0.01 -
        3.5 +
        rng.normal(0, 0.8, size=n_samples)
    )
    survival_prob = 1 / (1 + np.exp(-survival_logit))
    survived = (rng.random(size=n_samples) < survival_prob).astype(int)

    df = pd.DataFrame({
        "gender": gender,
        "member_count": member_count,
        "avg_member_age": np.round(avg_age, 1),
        "agency_tier": agency_tier,
        "agency_debut_history_count": agency_debut_history,
        "survival_show_origin": survival_show,
        "pre_debut_content_count": pre_debut_content,
        "concept_type": concept_type,
        "debut_youtube_views": debut_youtube_views,
        "debut_news_count": debut_news,
        "debut_music_show_wins": debut_wins,
        "initial_fan_vote": np.round(initial_fan_vote, 2),
        "initial_community_size": initial_community_size,
        "debut_week_album_sales": debut_week_sales,
        "survived_3_years": survived,
    })

    return df
