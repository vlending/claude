import { NextResponse } from "next/server";
import { recommendationAI } from "@/lib/ai/recommendation";

export const dynamic = "force-dynamic";

/**
 * GET /api/recommendations?userId=xxx
 * 사용자 맞춤 골프장 추천
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (!userId) {
      return NextResponse.json(
        { success: false, error: "userId is required" },
        { status: 400 }
      );
    }

    const result = await recommendationAI.getRecommendations(userId);

    return NextResponse.json({
      success: true,
      data: result,
    });
  } catch (error) {
    console.error("Recommendations error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to generate recommendations" },
      { status: 500 }
    );
  }
}
