"""시스템 설정 및 상수 정의"""

# 기획사 등급 분류
AGENCY_TIERS = {
    "big4": ["SM", "JYP", "YG", "HYBE"],
    "mid": ["STARSHIP", "PLEDIS", "CUBE", "FNC", "WOOLLIM", "RBW", "IST", "AOMG", "P_NATION"],
    "small": [],  # 그 외 모든 기획사
}

# 유통사 등급 분류
DISTRIBUTOR_TIERS = {
    "major": ["DREAMUS", "YG_PLUS", "KAKAO", "GENIE"],
    "mid": ["WARNER", "UNIVERSAL", "SONY"],
    "indie": [],
}

# 성별 인코딩
GENDER_ENCODING = {"male": 0, "female": 1, "mixed": 2}

# 차트 성적 기반 흥행 분류 임계값
HIT_THRESHOLD_STREAMING = 70  # 상위 30% -> 흥행
HIT_THRESHOLD_ALBUM = 70

# 신인 그룹 생존 기준 (년)
SURVIVAL_PERIOD_YEARS = 3

# 모델 설정
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# 피처 그룹 정의 (연구 1: 차트 성적 예측)
CHART_FEATURE_GROUPS = {
    "artist_capability": [
        "past_streaming_score",
        "past_album_score",
        "gender",
        "member_count",
        "years_active",
        "total_releases",
    ],
    "agency_capability": [
        "agency_tier",
        "agency_artist_count",
        "agency_avg_chart_score",
        "distributor_tier",
    ],
    "media_exposure": [
        "youtube_mv_views",
        "youtube_content_views",
        "news_article_count",
        "music_show_appearances",
        "tv_appearances",
    ],
    "fandom": [
        "fan_vote_score",
        "fan_community_size",
        "social_media_followers",
        "fancafe_members",
    ],
}

# 피처 그룹 정의 (연구 2: 신인 생존 예측)
SURVIVAL_FEATURE_GROUPS = {
    "agency": [
        "agency_tier",
        "agency_debut_history_count",
    ],
    "artist": [
        "gender",
        "member_count",
        "avg_member_age",
        "survival_show_origin",
        "pre_debut_content_count",
        "concept_type",
    ],
    "media": [
        "debut_youtube_views",
        "debut_news_count",
        "debut_music_show_wins",
    ],
    "fandom": [
        "initial_fan_vote",
        "initial_community_size",
        "debut_week_album_sales",
    ],
}
