export default function ProposalSummary() {
  const items = [
    'KBO Fan MVP는 매일 경기 종료 후 팬이 직접 MVP를 선정하는 공식 팬 참여형 서비스입니다.',
    '광고 기반 투표권 구조를 통해 신규 디지털 매출을 창출합니다.',
    '승률 기반 랭킹으로 팬의 재방문과 시즌 참여를 유도합니다.',
    '공식 기록 MVP와 별도로 Fan Pick MVP로 운영하여 논란을 줄입니다.'
  ];
  return <section className="rounded-2xl bg-white p-4"><h2 className="mb-2 text-lg font-bold">서비스 제안 요약</h2><ul className="list-disc space-y-1 pl-4 text-sm">{items.map((t) => <li key={t}>{t}</li>)}</ul></section>;
}
