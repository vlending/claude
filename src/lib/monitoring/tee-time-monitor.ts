import prisma from "@/lib/db/prisma";
import { SlotStatus } from "@/types";

export interface MonitoringResult {
  golfCourseId: string;
  golfCourseName: string;
  newAvailableSlots: number;
  cancelledSlots: number;
  totalChecked: number;
  timestamp: Date;
}

/**
 * 골프장 티타임 모니터링 핵심 로직
 *
 * 합법적인 방식으로 작동:
 * 1. 공개된 예약 정보만 확인
 * 2. 적절한 간격으로 체크 (최소 10초)
 * 3. 취소 티타임 발견 시 알림만 전송
 * 4. 자동 예약은 절대 수행하지 않음
 */
export class TeeTimeMonitor {
  private checkInterval: number;
  private isMonitoring: boolean = false;

  constructor(checkInterval: number = 30000) {
    // 최소 10초 간격
    this.checkInterval = Math.max(checkInterval, 10000);
  }

  /**
   * 특정 골프장의 티타임 상태를 확인
   * 실제로는 각 골프장의 예약 사이트를 크롤링하거나 API를 호출
   */
  async checkGolfCourseAvailability(golfCourseId: string): Promise<MonitoringResult> {
    const golfCourse = await prisma.golfCourse.findUnique({
      where: { id: golfCourseId },
    });

    if (!golfCourse) {
      throw new Error(`Golf course not found: ${golfCourseId}`);
    }

    // 실제 구현에서는 여기서 웹 크롤링이나 API 호출을 수행
    // 현재는 시뮬레이션
    const slots = await this.simulateFetchSlots(golfCourseId);

    let newAvailableSlots = 0;
    let cancelledSlots = 0;
    let totalChecked = 0;

    for (const slot of slots) {
      totalChecked++;

      const existingSlot = await prisma.teeTimeSlot.findUnique({
        where: {
          golfCourseId_date_time: {
            golfCourseId: slot.golfCourseId,
            date: slot.date,
            time: slot.time,
          },
        },
      });

      if (existingSlot) {
        // 기존 슬롯이 BOOKED → AVAILABLE로 변경된 경우 (취소 감지)
        if (existingSlot.status === "BOOKED" && slot.status === "AVAILABLE") {
          cancelledSlots++;

          await prisma.teeTimeSlot.update({
            where: { id: existingSlot.id },
            data: {
              status: "AVAILABLE",
              wasCancelled: true,
              cancelledAt: new Date(),
              lastChecked: new Date(),
            },
          });

          // 취소 티타임 알림 생성
          await this.createCancellationAlerts(golfCourse.id, slot.date, slot.time);
        } else {
          // 상태 업데이트
          await prisma.teeTimeSlot.update({
            where: { id: existingSlot.id },
            data: {
              status: slot.status,
              lastChecked: new Date(),
            },
          });
        }
      } else if (slot.status === "AVAILABLE") {
        // 새로운 예약 가능 슬롯 발견
        newAvailableSlots++;

        await prisma.teeTimeSlot.create({
          data: {
            golfCourseId: slot.golfCourseId,
            date: slot.date,
            time: slot.time,
            price: slot.price,
            status: slot.status,
            lastChecked: new Date(),
            wasCancelled: false,
          },
        });
      }
    }

    return {
      golfCourseId: golfCourse.id,
      golfCourseName: golfCourse.name,
      newAvailableSlots,
      cancelledSlots,
      totalChecked,
      timestamp: new Date(),
    };
  }

  /**
   * 취소 티타임 알림 생성
   * 프리미엄 사용자에게 우선 알림
   */
  private async createCancellationAlerts(
    golfCourseId: string,
    date: Date,
    time: string
  ): Promise<void> {
    const golfCourse = await prisma.golfCourse.findUnique({
      where: { id: golfCourseId },
    });

    if (!golfCourse) return;

    // 해당 골프장을 즐겨찾기한 사용자들 찾기
    const favorites = await prisma.favoriteGolfCourse.findMany({
      where: { golfCourseId },
      include: { user: true },
    });

    // 프리미엄 사용자 우선
    const premiumUsers = favorites
      .filter((fav: any) => fav.user.subscriptionTier === "PREMIUM")
      .map((fav: any) => fav.user);

    const freeUsers = favorites
      .filter((fav: any) => fav.user.subscriptionTier === "FREE")
      .map((fav: any) => fav.user);

    const dateStr = date.toLocaleDateString("ko-KR");

    // 프리미엄 사용자에게 즉시 알림
    for (const user of premiumUsers) {
      if (!user.notificationsEnabled) continue;

      await prisma.alert.create({
        data: {
          userId: user.id,
          type: "CANCELLATION",
          golfCourseId,
          title: `🔥 취소 티타임 발견!`,
          message: `${golfCourse.name}에서 ${dateStr} ${time} 티타임이 취소되었습니다. 지금 바로 예약하세요!`,
          actionUrl: golfCourse.bookingUrl,
          isRead: false,
        },
      });
    }

    // 무료 사용자에게는 지연 알림 (30분 후)
    // 실제 구현에서는 job queue 사용
    setTimeout(async () => {
      for (const user of freeUsers) {
        if (!user.notificationsEnabled) continue;

        await prisma.alert.create({
          data: {
            userId: user.id,
            type: "CANCELLATION",
            golfCourseId,
            title: `취소 티타임 알림`,
            message: `${golfCourse.name}에서 ${dateStr} ${time} 티타임이 취소되었습니다.`,
            actionUrl: golfCourse.bookingUrl,
            isRead: false,
          },
        });
      }
    }, 30 * 60 * 1000); // 30분 지연
  }

  /**
   * 실제 구현에서는 웹 크롤링이나 API 호출
   * 현재는 시뮬레이션 데이터 반환
   */
  private async simulateFetchSlots(golfCourseId: string) {
    // 실제 구현 예시:
    // 1. Puppeteer/Playwright로 예약 사이트 접속
    // 2. 로그인 (필요시)
    // 3. 예약 가능한 티타임 목록 파싱
    // 4. 데이터 반환

    // 현재는 DB에서 기존 슬롯 가져오기
    const slots = await prisma.teeTimeSlot.findMany({
      where: {
        golfCourseId,
        date: {
          gte: new Date(),
        },
      },
      take: 50,
    });

    // 일부 슬롯의 상태를 랜덤하게 변경 (시뮬레이션)
    return slots.map((slot: any) => ({
      ...slot,
      status: Math.random() > 0.9 ? "AVAILABLE" : slot.status,
    }));
  }

  /**
   * 모니터링 시작
   */
  async startMonitoring(golfCourseIds: string[]): Promise<void> {
    if (this.isMonitoring) {
      console.log("⚠️  Monitoring already running");
      return;
    }

    this.isMonitoring = true;
    console.log(`🚀 Starting tee time monitoring for ${golfCourseIds.length} golf courses`);

    const monitorLoop = async () => {
      if (!this.isMonitoring) return;

      for (const courseId of golfCourseIds) {
        try {
          const result = await this.checkGolfCourseAvailability(courseId);
          console.log(
            `✅ ${result.golfCourseName}: ${result.cancelledSlots} cancelled, ${result.newAvailableSlots} new slots`
          );
        } catch (error) {
          console.error(`❌ Error monitoring ${courseId}:`, error);
        }

        // 골프장 간 간격을 두어 서버 부하 방지
        await this.sleep(2000);
      }

      // 다음 체크까지 대기
      setTimeout(monitorLoop, this.checkInterval);
    };

    monitorLoop();
  }

  /**
   * 모니터링 중지
   */
  stopMonitoring(): void {
    this.isMonitoring = false;
    console.log("🛑 Stopping tee time monitoring");
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// 싱글톤 인스턴스
export const teeTimeMonitor = new TeeTimeMonitor(30000); // 30초 간격
