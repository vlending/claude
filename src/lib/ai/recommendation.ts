import Anthropic from "@anthropic-ai/sdk";
import prisma from "@/lib/db/prisma";
import { GolfCourse } from "@/types";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || "",
});

interface UserPreferences {
  address?: string;
  latitude?: number;
  longitude?: number;
  averageScore?: number;
  skillLevel?: string;
  preferredDays: string[];
  preferredTimes: string[];
  budgetMin?: number;
  budgetMax?: number;
}

interface RecommendationResult {
  recommendations: Array<{
    golfCourse: GolfCourse;
    score: number;
    reasons: string[];
  }>;
  aiInsights: string;
}

/**
 * 사용자 프로필 기반 골프장 추천 AI
 */
export class GolfCourseRecommendationAI {
  /**
   * 거리 계산 (Haversine formula)
   */
  private calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const R = 6371; // Earth's radius in km
    const dLat = this.deg2rad(lat2 - lat1);
    const dLon = this.deg2rad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.deg2rad(lat1)) *
        Math.cos(this.deg2rad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private deg2rad(deg: number): number {
    return deg * (Math.PI / 180);
  }

  /**
   * 기본 필터링 및 점수 계산
   */
  private async scoreGolfCourses(
    courses: any[],
    preferences: UserPreferences
  ): Promise<Array<{ course: any; score: number; reasons: string[] }>> {
    const scored = courses.map((course) => {
      let score = 0;
      const reasons: string[] = [];

      // 거리 점수 (최대 30점)
      if (preferences.latitude && preferences.longitude) {
        const distance = this.calculateDistance(
          preferences.latitude,
          preferences.longitude,
          course.latitude,
          course.longitude
        );

        if (distance < 20) {
          score += 30;
          reasons.push(`거주지에서 ${distance.toFixed(1)}km로 매우 가까움`);
        } else if (distance < 40) {
          score += 20;
          reasons.push(`거주지에서 ${distance.toFixed(1)}km로 적당한 거리`);
        } else if (distance < 60) {
          score += 10;
          reasons.push(`거주지에서 ${distance.toFixed(1)}km`);
        }
      }

      // 가격 점수 (최대 25점)
      const avgPrice = (course.weekdayPrice + course.weekendPrice) / 2;
      if (preferences.budgetMin && preferences.budgetMax) {
        if (avgPrice >= preferences.budgetMin && avgPrice <= preferences.budgetMax) {
          score += 25;
          reasons.push("예산 범위에 완벽하게 부합");
        } else if (avgPrice < preferences.budgetMax * 1.1) {
          score += 15;
          reasons.push("예산에 근접");
        }
      }

      // 난이도 점수 (최대 20점)
      if (preferences.skillLevel) {
        const skillMapping: Record<string, number[]> = {
          BEGINNER: [1, 2, 3],
          INTERMEDIATE: [2, 3, 4],
          ADVANCED: [3, 4, 5],
          PROFESSIONAL: [4, 5],
        };

        const suitableDifficulties = skillMapping[preferences.skillLevel] || [3];
        if (suitableDifficulties.includes(course.difficulty)) {
          score += 20;
          reasons.push(`${preferences.skillLevel} 실력에 적합한 난이도`);
        } else if (
          suitableDifficulties.includes(course.difficulty - 1) ||
          suitableDifficulties.includes(course.difficulty + 1)
        ) {
          score += 10;
          reasons.push("적당한 도전 과제");
        }
      }

      // 평점 점수 (최대 15점)
      if (course.rating) {
        score += (course.rating / 5) * 15;
        reasons.push(`평점 ${course.rating}/5.0 (리뷰 ${course.reviewCount}개)`);
      }

      // 시설 점수 (최대 10점)
      if (course.facilities && course.facilities.length > 0) {
        score += Math.min(course.facilities.length * 2, 10);
        if (course.facilities.length >= 4) {
          reasons.push("다양한 부대시설 보유");
        }
      }

      return { course, score, reasons };
    });

    return scored.sort((a, b) => b.score - a.score);
  }

  /**
   * Claude AI를 사용한 추천 인사이트 생성
   */
  private async generateAIInsights(
    topCourses: any[],
    preferences: UserPreferences
  ): Promise<string> {
    const coursesInfo = topCourses
      .slice(0, 5)
      .map(
        (item, idx) =>
          `${idx + 1}. ${item.course.name} (${item.course.region} ${item.course.city})
   - 난이도: ${item.course.difficulty}/5
   - 평일 ${item.course.weekdayPrice.toLocaleString()}원, 주말 ${item.course.weekendPrice.toLocaleString()}원
   - 평점: ${item.course.rating}/5.0
   - 홀: ${item.course.holes}홀, Par ${item.course.par}
   - 시설: ${item.course.facilities.join(", ")}
   - 추천 이유: ${item.reasons.join(", ")}`
      )
      .join("\n\n");

    const userInfo = `
사용자 프로필:
- 위치: ${preferences.address || "미설정"}
- 평균 스코어: ${preferences.averageScore || "미설정"}
- 실력: ${preferences.skillLevel || "미설정"}
- 예산: ${preferences.budgetMin?.toLocaleString() || "제한없음"} ~ ${preferences.budgetMax?.toLocaleString() || "제한없음"}원
- 선호 요일: ${preferences.preferredDays.length > 0 ? preferences.preferredDays.join(", ") : "미설정"}
- 선호 시간: ${preferences.preferredTimes.length > 0 ? preferences.preferredTimes.join(", ") : "미설정"}
`;

    try {
      const message = await anthropic.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 1024,
        messages: [
          {
            role: "user",
            content: `당신은 수도권 골프장 전문가입니다. 다음 사용자에게 가장 적합한 골프장을 추천하고, 핵심 인사이트를 3-4문장으로 요약해주세요.

${userInfo}

추천 골프장 TOP 5:
${coursesInfo}

요청사항:
1. 사용자의 실력과 예산을 고려한 핵심 추천 이유
2. 각 골프장의 특징과 장단점
3. 예약 팁이나 유의사항

친근하고 전문적인 톤으로 3-4문장으로 답변해주세요.`,
          },
        ],
      });

      const textContent = message.content.find((block) => block.type === "text");
      return textContent?.type === "text" ? textContent.text : "추천 분석을 생성하지 못했습니다.";
    } catch (error) {
      console.error("AI insights generation error:", error);
      return "현재 AI 분석을 사용할 수 없습니다. 기본 추천 결과를 확인해주세요.";
    }
  }

  /**
   * 사용자 맞춤 골프장 추천
   */
  async getRecommendations(userId: string): Promise<RecommendationResult> {
    // 사용자 프로필 가져오기
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) {
      throw new Error("User not found");
    }

    // 활성 골프장 가져오기
    const courses = await prisma.golfCourse.findMany({
      where: { isActive: true },
    });

    // 점수 계산
    const scoredCourses = await this.scoreGolfCourses(courses, {
      address: user.address || undefined,
      latitude: user.latitude || undefined,
      longitude: user.longitude || undefined,
      averageScore: user.averageScore || undefined,
      skillLevel: user.skillLevel || undefined,
      preferredDays: user.preferredDays,
      preferredTimes: user.preferredTimes,
      budgetMin: user.budgetMin || undefined,
      budgetMax: user.budgetMax || undefined,
    });

    // AI 인사이트 생성
    const aiInsights = await this.generateAIInsights(scoredCourses, {
      address: user.address || undefined,
      latitude: user.latitude || undefined,
      longitude: user.longitude || undefined,
      averageScore: user.averageScore || undefined,
      skillLevel: user.skillLevel || undefined,
      preferredDays: user.preferredDays,
      preferredTimes: user.preferredTimes,
      budgetMin: user.budgetMin || undefined,
      budgetMax: user.budgetMax || undefined,
    });

    return {
      recommendations: scoredCourses.slice(0, 10).map((item) => ({
        golfCourse: item.course as GolfCourse,
        score: item.score,
        reasons: item.reasons,
      })),
      aiInsights,
    };
  }
}

export const recommendationAI = new GolfCourseRecommendationAI();
