import { NextResponse } from "next/server";
import prisma from "@/lib/db/prisma";

export const dynamic = "force-dynamic";

/**
 * GET /api/golf-courses/:id
 * 특정 골프장 상세 정보 조회
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params;
    const golfCourse = await prisma.golfCourse.findUnique({
      where: { id: params.id },
    });

    if (!golfCourse) {
      return NextResponse.json(
        { success: false, error: "Golf course not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: golfCourse,
    });
  } catch (error) {
    console.error("Golf course fetch error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch golf course" },
      { status: 500 }
    );
  }
}
