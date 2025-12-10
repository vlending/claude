"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface GolfCourse {
  id: string;
  name: string;
  region: string;
  city: string;
  address: string;
  latitude: number;
  longitude: number;
  holes: number;
  par: number;
  difficulty: number;
  weekdayPrice: number;
  weekendPrice: number;
  bookingUrl: string;
  bookingOpenTime: string;
  bookingOpenDays: number;
  rating: number;
  reviewCount: number;
  facilities: string[];
}

export default function GolfCourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [course, setCourse] = useState<GolfCourse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchGolfCourse(params.id as string);
    }
  }, [params.id]);

  const fetchGolfCourse = async (id: string) => {
    try {
      const response = await fetch(`/api/golf-courses/${id}`);
      const data = await response.json();
      if (data.success) {
        setCourse(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch golf course:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyLabel = (difficulty: number) => {
    const labels = ["", "쉬움", "보통", "다소 어려움", "어려움", "매우 어려움"];
    return labels[difficulty] || "보통";
  };

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty <= 2) return "bg-green-100 text-green-800";
    if (difficulty === 3) return "bg-blue-100 text-blue-800";
    if (difficulty === 4) return "bg-orange-100 text-orange-800";
    return "bg-red-100 text-red-800";
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-xl">골프장 정보를 불러오는 중...</div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">골프장을 찾을 수 없습니다.</p>
          <Button onClick={() => router.push("/golf-courses")}>목록으로 돌아가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <Button variant="outline" onClick={() => router.back()} className="mb-6">
          ← 뒤로 가기
        </Button>

        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold mb-2">{course.name}</h1>
              <p className="text-lg text-muted-foreground">
                {course.region} · {course.city}
              </p>
            </div>
            <Badge className={`${getDifficultyColor(course.difficulty)} text-sm px-3 py-1`}>
              {getDifficultyLabel(course.difficulty)}
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <span className="text-2xl font-bold">{course.rating}</span>
              <span className="text-muted-foreground">/ 5.0</span>
            </div>
            <span className="text-muted-foreground">({course.reviewCount}개 리뷰)</span>
          </div>
        </div>

        {/* 기본 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>코스 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">홀 수</span>
                <span className="font-semibold">{course.holes}홀</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">파</span>
                <span className="font-semibold">Par {course.par}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">난이도</span>
                <span className="font-semibold">{getDifficultyLabel(course.difficulty)}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>가격 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">평일</span>
                <span className="font-semibold text-lg">
                  {course.weekdayPrice.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">주말</span>
                <span className="font-semibold text-lg">
                  {course.weekendPrice.toLocaleString()}원
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 시설 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>시설 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {course.facilities.map((facility) => (
                <Badge key={facility} variant="secondary" className="px-3 py-1">
                  {facility}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 예약 정보 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>예약 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">예약 오픈 시간</span>
              <span className="font-semibold">{course.bookingOpenTime}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">예약 가능 기간</span>
              <span className="font-semibold">{course.bookingOpenDays}일 전부터</span>
            </div>
            <div className="pt-4">
              <Button
                className="w-full bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600"
                onClick={() => window.open(course.bookingUrl, "_blank")}
              >
                예약 사이트로 이동
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 위치 정보 */}
        <Card>
          <CardHeader>
            <CardTitle>위치</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">{course.address}</p>
            <div className="bg-muted h-64 rounded-lg flex items-center justify-center">
              <p className="text-muted-foreground">
                지도 표시 (위도: {course.latitude.toFixed(4)}, 경도: {course.longitude.toFixed(4)})
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
