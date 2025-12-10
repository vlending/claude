import { NextResponse } from "next/server";
import prisma from "@/lib/db/prisma";

export const dynamic = "force-dynamic";

/**
 * GET /api/tee-times
 * 티타임 슬롯 조회
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const golfCourseId = searchParams.get("golfCourseId");
    const date = searchParams.get("date");
    const status = searchParams.get("status");

    const where: any = {};

    if (golfCourseId) {
      where.golfCourseId = golfCourseId;
    }

    if (date) {
      const targetDate = new Date(date);
      const nextDate = new Date(targetDate);
      nextDate.setDate(nextDate.getDate() + 1);

      where.date = {
        gte: targetDate,
        lt: nextDate,
      };
    } else {
      // 기본적으로 오늘 이후만 표시
      where.date = {
        gte: new Date(),
      };
    }

    if (status) {
      where.status = status;
    }

    const teeTimeSlots = await prisma.teeTimeSlot.findMany({
      where,
      include: {
        golfCourse: {
          select: {
            name: true,
            region: true,
            city: true,
          },
        },
      },
      orderBy: [{ date: "asc" }, { time: "asc" }],
      take: 100,
    });

    return NextResponse.json({
      success: true,
      data: teeTimeSlots,
      count: teeTimeSlots.length,
    });
  } catch (error) {
    console.error("Tee times fetch error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch tee times" },
      { status: 500 }
    );
  }
}
