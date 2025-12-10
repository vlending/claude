import { NextResponse } from "next/server";
import { teeTimeMonitor } from "@/lib/monitoring/tee-time-monitor";
import prisma from "@/lib/db/prisma";

export const dynamic = "force-dynamic";

/**
 * GET /api/monitoring
 * 모니터링 상태 확인
 */
export async function GET() {
  try {
    const activeMonitoringCount = await prisma.golfCourse.count({
      where: { isActive: true },
    });

    const recentSlots = await prisma.teeTimeSlot.findMany({
      where: {
        lastChecked: {
          gte: new Date(Date.now() - 5 * 60 * 1000), // 최근 5분
        },
      },
      take: 10,
      orderBy: { lastChecked: "desc" },
      include: {
        golfCourse: {
          select: {
            name: true,
          },
        },
      },
    });

    return NextResponse.json({
      success: true,
      data: {
        activeGolfCourses: activeMonitoringCount,
        recentChecks: recentSlots.length,
        lastChecked: recentSlots[0]?.lastChecked || null,
      },
    });
  } catch (error) {
    console.error("Monitoring status error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch monitoring status" },
      { status: 500 }
    );
  }
}

/**
 * POST /api/monitoring/check
 * 특정 골프장 수동 체크
 */
export async function POST(request: Request) {
  try {
    const { golfCourseId } = await request.json();

    if (!golfCourseId) {
      return NextResponse.json(
        { success: false, error: "golfCourseId is required" },
        { status: 400 }
      );
    }

    const result = await teeTimeMonitor.checkGolfCourseAvailability(golfCourseId);

    return NextResponse.json({
      success: true,
      data: result,
    });
  } catch (error) {
    console.error("Manual check error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to check golf course" },
      { status: 500 }
    );
  }
}
