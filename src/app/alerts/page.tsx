"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Alert {
  id: string;
  type: "OPENING_SOON" | "CANCELLATION" | "RECOMMENDATION";
  title: string;
  message: string;
  actionUrl?: string;
  isRead: boolean;
  sentAt: string;
  golfCourse?: {
    name: string;
    region: string;
    city: string;
  };
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [isLoading, setIsLoading] = useState(true);

  // Demo user ID (실제로는 인증된 사용자 ID 사용)
  const userId = "demo-user-id";

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`/api/alerts?userId=${userId}`);
      const data = await response.json();
      if (data.success) {
        setAlerts(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch alerts:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = async (alertId: string) => {
    try {
      const response = await fetch(`/api/alerts/${alertId}/read`, {
        method: "POST",
      });

      if (response.ok) {
        setAlerts(
          alerts.map((alert) =>
            alert.id === alertId ? { ...alert, isRead: true } : alert
          )
        );
      }
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch(`/api/alerts/mark-all-read?userId=${userId}`, {
        method: "POST",
      });

      if (response.ok) {
        setAlerts(alerts.map((alert) => ({ ...alert, isRead: true })));
      }
    } catch (error) {
      console.error("Failed to mark all as read:", error);
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "CANCELLATION":
        return "🔥";
      case "OPENING_SOON":
        return "⏰";
      case "RECOMMENDATION":
        return "🎯";
      default:
        return "🔔";
    }
  };

  const getAlertBadgeVariant = (type: string) => {
    switch (type) {
      case "CANCELLATION":
        return "destructive";
      case "OPENING_SOON":
        return "default";
      case "RECOMMENDATION":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case "CANCELLATION":
        return "취소 티타임";
      case "OPENING_SOON":
        return "오픈 예정";
      case "RECOMMENDATION":
        return "추천";
      default:
        return "알림";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return "방금 전";
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;
    return date.toLocaleDateString("ko-KR");
  };

  const filteredAlerts = filter === "unread" ? alerts.filter((a) => !a.isRead) : alerts;
  const unreadCount = alerts.filter((a) => !a.isRead).length;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-xl">알림을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">알림</h1>
            <p className="text-muted-foreground">
              읽지 않은 알림 {unreadCount}개
            </p>
          </div>
          {unreadCount > 0 && (
            <Button variant="outline" onClick={markAllAsRead}>
              모두 읽음 표시
            </Button>
          )}
        </div>

        {/* 필터 */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            onClick={() => setFilter("all")}
            size="sm"
          >
            전체 ({alerts.length})
          </Button>
          <Button
            variant={filter === "unread" ? "default" : "outline"}
            onClick={() => setFilter("unread")}
            size="sm"
          >
            읽지 않음 ({unreadCount})
          </Button>
        </div>

        {/* 알림 목록 */}
        <div className="space-y-4">
          {filteredAlerts.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">
                  {filter === "unread" ? "읽지 않은 알림이 없습니다." : "알림이 없습니다."}
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredAlerts.map((alert) => (
              <Card
                key={alert.id}
                className={`cursor-pointer transition-all ${
                  !alert.isRead
                    ? "border-l-4 border-l-green-500 bg-green-50/50"
                    : "hover:bg-muted/50"
                }`}
                onClick={() => {
                  if (!alert.isRead) {
                    markAsRead(alert.id);
                  }
                  if (alert.actionUrl) {
                    window.open(alert.actionUrl, "_blank");
                  }
                }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="text-3xl">{getAlertIcon(alert.type)}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <CardTitle className="text-lg">{alert.title}</CardTitle>
                          <Badge variant={getAlertBadgeVariant(alert.type) as any}>
                            {getAlertTypeLabel(alert.type)}
                          </Badge>
                          {!alert.isRead && (
                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                              New
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-sm">
                          {formatDate(alert.sentAt)}
                          {alert.golfCourse && (
                            <span className="ml-2">
                              · {alert.golfCourse.name} ({alert.golfCourse.region})
                            </span>
                          )}
                        </CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{alert.message}</p>
                  {alert.actionUrl && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-4"
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(alert.actionUrl, "_blank");
                      }}
                    >
                      예약 페이지로 이동 →
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* 프리미엄 업그레이드 배너 */}
        <Card className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              💎 프리미엄으로 업그레이드
            </CardTitle>
            <CardDescription>
              취소 티타임을 가장 먼저 받아보세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 mb-4 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>실시간 취소 티타임 알림 (무료 회원보다 30분 빠름)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>무제한 AI 추천</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>다중 골프장 동시 모니터링 (최대 5개)</span>
              </li>
            </ul>
            <Button className="bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600">
              월 9,900원으로 업그레이드
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
