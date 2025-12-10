import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 md:p-24">
      <div className="max-w-6xl w-full">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="secondary">
            합법적인 예약 도우미 서비스
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-green-600 to-emerald-500 bg-clip-text text-transparent">
            AI 골프 부킹 어시스턴트
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            수도권 골프장 예약 성공 확률을 극적으로 올려주는 AI 기반 서비스
          </p>
          <Button size="lg" className="bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600">
            무료로 시작하기
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          <FeatureCard
            icon="🎯"
            title="개인 맞춤 추천"
            description="거주지, 선호, 스코어 기반 최적의 티타임 추천"
          />
          <FeatureCard
            icon="⏰"
            title="오픈 시간 알림"
            description="예약 오픈 시간 자동 모니터링 및 알림"
          />
          <FeatureCard
            icon="🔔"
            title="취소 티타임 감지"
            description="실시간 취소 티타임 발견 및 즉시 푸시 알림"
          />
          <FeatureCard
            icon="📊"
            title="성공 확률 예측"
            description="AI 기반 예약 성공 확률 분석"
          />
          <FeatureCard
            icon="🏌️"
            title="수도권 골프장"
            description="경기도, 서울, 인천 주요 골프장 지원"
          />
          <FeatureCard
            icon="💎"
            title="프리미엄 기능"
            description="무제한 추천, 실시간 알림, 성공률 AI"
          />
        </div>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardHeader>
            <CardTitle className="text-yellow-900">⚖️ 합법적인 서비스</CardTitle>
            <CardDescription className="text-yellow-800">
              자동 예약이 아닌, 예약 성공을 돕는 알림 서비스입니다.
              모든 예약은 사용자가 직접 클릭해야 합니다.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="text-4xl mb-2">{icon}</div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}
