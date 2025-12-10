import { NextResponse } from "next/server";
import prisma from "@/lib/db/prisma";

export const dynamic = "force-dynamic";

/**
 * GET /api/golf-courses
 * 골프장 목록 조회
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const region = searchParams.get("region");
    const minPrice = searchParams.get("minPrice");
    const maxPrice = searchParams.get("maxPrice");
    const difficulty = searchParams.get("difficulty");

    const where: any = {
      isActive: true,
    };

    if (region) {
      where.region = region;
    }

    if (minPrice || maxPrice) {
      where.OR = [
        {
          weekdayPrice: {
            gte: minPrice ? parseInt(minPrice) : undefined,
            lte: maxPrice ? parseInt(maxPrice) : undefined,
          },
        },
        {
          weekendPrice: {
            gte: minPrice ? parseInt(minPrice) : undefined,
            lte: maxPrice ? parseInt(maxPrice) : undefined,
          },
        },
      ];
    }

    if (difficulty) {
      where.difficulty = parseInt(difficulty);
    }

    const golfCourses = await prisma.golfCourse.findMany({
      where,
      orderBy: [{ rating: "desc" }, { reviewCount: "desc" }],
    });

    return NextResponse.json({
      success: true,
      data: golfCourses,
      count: golfCourses.length,
    });
  } catch (error) {
    console.error("Golf courses fetch error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch golf courses" },
      { status: 500 }
    );
  }
}
