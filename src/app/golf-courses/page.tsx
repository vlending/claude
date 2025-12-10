"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface GolfCourse {
  id: string;
  name: string;
  region: string;
  city: string;
  address: string;
  holes: number;
  par: number;
  difficulty: number;
  weekdayPrice: number;
  weekendPrice: number;
  rating: number;
  reviewCount: number;
  facilities: string[];
}

export default function GolfCoursesPage() {
  const [courses, setCourses] = useState<GolfCourse[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<GolfCourse[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRegion, setSelectedRegion] = useState<string>("전체");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchGolfCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [searchQuery, selectedRegion, courses]);

  const fetchGolfCourses = async () => {
    try {
      const response = await fetch("/api/golf-courses");
      const data = await response.json();
      if (data.success) {
        setCourses(data.data);
        setFilteredCourses(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch golf courses:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterCourses = () => {
    let filtered = courses;

    if (selectedRegion !== "전체") {
      filtered = filtered.filter((course) => course.region === selectedRegion);
    }

    if (searchQuery) {
      filtered = filtered.filter(
        (course) =>
          course.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          course.city.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredCourses(filtered);
  };

  const regions = ["전체", "경기북부", "경기남부", "경기동부", "경기서부", "인천"];

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
        <div className="text-center">
          <div className="text-xl">골프장 정보를 불러오는 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">수도권 골프장</h1>
          <p className="text-muted-foreground">총 {filteredCourses.length}개 골프장</p>
        </div>

        {/* 검색 및 필터 */}
        <div className="mb-8 space-y-4">
          <Input
            type="search"
            placeholder="골프장 이름 또는 지역 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />

          <div className="flex gap-2 flex-wrap">
            {regions.map((region) => (
              <Button
                key={region}
                variant={selectedRegion === region ? "default" : "outline"}
                onClick={() => setSelectedRegion(region)}
                size="sm"
              >
                {region}
              </Button>
            ))}
          </div>
        </div>

        {/* 골프장 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <Link key={course.id} href={`/golf-courses/${course.id}`}>
              <Card className="hover:shadow-lg transition-shadow h-full cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <CardTitle className="text-xl">{course.name}</CardTitle>
                    <Badge variant="secondary">{course.region}</Badge>
                  </div>
                  <CardDescription>
                    {course.city} · {course.holes}홀 · Par {course.par}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">난이도</span>
                      <Badge className={getDifficultyColor(course.difficulty)}>
                        {getDifficultyLabel(course.difficulty)}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">평점</span>
                      <div className="flex items-center gap-1">
                        <span className="font-semibold">{course.rating}</span>
                        <span className="text-sm text-muted-foreground">
                          ({course.reviewCount})
                        </span>
                      </div>
                    </div>

                    <div className="pt-3 border-t">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-muted-foreground">평일</span>
                        <span className="font-semibold">
                          {course.weekdayPrice.toLocaleString()}원
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">주말</span>
                        <span className="font-semibold">
                          {course.weekendPrice.toLocaleString()}원
                        </span>
                      </div>
                    </div>

                    {course.facilities.length > 0 && (
                      <div className="pt-3 border-t">
                        <div className="flex flex-wrap gap-1">
                          {course.facilities.slice(0, 3).map((facility) => (
                            <Badge key={facility} variant="outline" className="text-xs">
                              {facility}
                            </Badge>
                          ))}
                          {course.facilities.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{course.facilities.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {filteredCourses.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">검색 결과가 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}
