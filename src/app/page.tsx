export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full">
        <h1 className="text-6xl font-bold text-center mb-8 bg-gradient-to-r from-green-600 to-emerald-500 bg-clip-text text-transparent">
          AI 골프 부킹 어시스턴트
        </h1>

        <p className="text-xl text-center text-gray-600 mb-12">
          수도권 골프장 예약 성공 확률을 극적으로 올려주는 AI 기반 서비스
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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

        <div className="mt-16 text-center">
          <button className="bg-gradient-to-r from-green-600 to-emerald-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-green-700 hover:to-emerald-600 transition-all shadow-lg">
            시작하기
          </button>
        </div>

        <div className="mt-12 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>⚖️ 합법적인 서비스:</strong> 자동 예약이 아닌, 예약 성공을 돕는 알림 서비스입니다.
            모든 예약은 사용자가 직접 클릭해야 합니다.
          </p>
        </div>
      </div>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="p-6 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow bg-white">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
