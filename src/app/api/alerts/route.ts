import { NextResponse } from "next/server";
import prisma from "@/lib/db/prisma";

export const dynamic = "force-dynamic";

/**
 * GET /api/alerts?userId=xxx
 * 사용자 알림 조회
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

    const alerts = await prisma.alert.findMany({
      where: { userId },
      include: {
        golfCourse: {
          select: {
            name: true,
            region: true,
            city: true,
          },
        },
      },
      orderBy: { sentAt: "desc" },
      take: 50,
    });

    return NextResponse.json({
      success: true,
      data: alerts,
    });
  } catch (error) {
    console.error("Alerts fetch error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch alerts" },
      { status: 500 }
    );
  }
}
