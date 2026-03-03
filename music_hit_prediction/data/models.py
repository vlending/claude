"""
데이터 모델 정의

논문의 독립변수/종속변수를 Pydantic 모델로 정의합니다.
- 연구 1: 차트 성적 예측을 위한 피처
- 연구 2: 신인 그룹 생존 예측을 위한 피처
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"


class AgencyTier(str, Enum):
    BIG4 = "big4"
    MID = "mid"
    SMALL = "small"


class DistributorTier(str, Enum):
    MAJOR = "major"
    MID = "mid"
    INDIE = "indie"


class ConceptType(str, Enum):
    CUTE = "cute"
    GIRL_CRUSH = "girl_crush"
    ELEGANT = "elegant"
    HIP_HOP = "hip_hop"
    PERFORMANCE = "performance"
    VOCAL = "vocal"
    FRESH = "fresh"
    DARK = "dark"


# ─── 연구 1: 차트 성적 예측 입력 ───


class ArtistCapability(BaseModel):
    """아티스트 역량 변인"""
    past_streaming_score: float = Field(0.0, description="과거 음원 성적 (0-100 정규화)")
    past_album_score: float = Field(0.0, description="과거 음반 성적 (0-100 정규화)")
    gender: Gender = Field(description="성별 (male/female/mixed)")
    member_count: int = Field(1, ge=1, description="멤버 수")
    years_active: int = Field(0, ge=0, description="활동 연차")
    total_releases: int = Field(0, ge=0, description="총 발매 작품 수")


class AgencyCapability(BaseModel):
    """기획사/유통사 역량 변인"""
    agency_tier: AgencyTier = Field(description="기획사 등급")
    agency_artist_count: int = Field(1, ge=1, description="기획사 소속 아티스트 수")
    agency_avg_chart_score: float = Field(0.0, description="기획사 소속 아티스트 평균 차트 성적")
    distributor_tier: DistributorTier = Field(description="유통사 등급")


class MediaExposure(BaseModel):
    """미디어 노출 변인"""
    youtube_mv_views: int = Field(0, ge=0, description="뮤직비디오 유튜브 조회수")
    youtube_content_views: int = Field(0, ge=0, description="유튜브 콘텐츠(비하인드 등) 조회수")
    news_article_count: int = Field(0, ge=0, description="기사 노출 수")
    music_show_appearances: int = Field(0, ge=0, description="음악 방송 출연 횟수")
    tv_appearances: int = Field(0, ge=0, description="TV 예능/드라마 출연 횟수")


class FandomMetrics(BaseModel):
    """팬덤 변인"""
    fan_vote_score: float = Field(0.0, ge=0, description="팬덤 플랫폼 투표 점수 (뮤빗 등)")
    fan_community_size: int = Field(0, ge=0, description="팬 커뮤니티 규모")
    social_media_followers: int = Field(0, ge=0, description="소셜미디어 팔로워 수")
    fancafe_members: int = Field(0, ge=0, description="팬카페 회원 수")


class ChartPredictionInput(BaseModel):
    """연구 1: 차트 성적 예측 전체 입력"""
    artist_name: str = Field(description="아티스트명")
    release_title: str = Field(description="발매 작품명")
    artist: ArtistCapability
    agency: AgencyCapability
    media: MediaExposure
    fandom: FandomMetrics


class ChartPredictionOutput(BaseModel):
    """연구 1: 차트 성적 예측 결과"""
    artist_name: str
    release_title: str
    predicted_streaming_score: float = Field(description="예측 음원 성적 (0-100)")
    predicted_album_score: float = Field(description="예측 음반 성적 (0-100)")
    is_streaming_hit: bool = Field(description="음원 흥행 여부")
    is_album_hit: bool = Field(description="음반 흥행 여부")
    hit_probability: float = Field(description="흥행 확률 (0-1)")
    top_contributing_features: list[dict] = Field(description="주요 기여 피처 목록")


# ─── 연구 2: 신인 그룹 생존 예측 입력 ───


class RookieSurvivalInput(BaseModel):
    """연구 2: 신인 그룹 생존 예측 입력"""
    group_name: str = Field(description="그룹명")
    debut_year: int = Field(description="데뷔 연도")
    gender: Gender = Field(description="성별")
    member_count: int = Field(ge=1, description="멤버 수")
    avg_member_age: float = Field(description="멤버 평균 나이")
    agency_tier: AgencyTier = Field(description="기획사 등급")
    agency_debut_history_count: int = Field(0, ge=0, description="기획사 과거 데뷔 그룹 수")
    survival_show_origin: bool = Field(False, description="서바이벌 프로그램 출신 여부")
    pre_debut_content_count: int = Field(0, ge=0, description="데뷔 전 공개 콘텐츠 수")
    concept_type: ConceptType = Field(description="콘셉트 유형")
    debut_youtube_views: int = Field(0, ge=0, description="데뷔곡 유튜브 조회수")
    debut_news_count: int = Field(0, ge=0, description="데뷔 시 기사 수")
    debut_music_show_wins: int = Field(0, ge=0, description="데뷔 후 음악방송 1위 횟수")
    initial_fan_vote: float = Field(0.0, ge=0, description="초기 팬 투표 점수")
    initial_community_size: int = Field(0, ge=0, description="초기 팬 커뮤니티 규모")
    debut_week_album_sales: int = Field(0, ge=0, description="데뷔 첫 주 음반 판매량")


class RookieSurvivalOutput(BaseModel):
    """연구 2: 신인 그룹 생존 예측 결과"""
    group_name: str
    survival_probability: float = Field(description="3년 생존 확률 (0-1)")
    will_survive: bool = Field(description="생존 예측 여부")
    risk_factors: list[dict] = Field(description="위험 요인 목록")
    protective_factors: list[dict] = Field(description="보호 요인 목록")
