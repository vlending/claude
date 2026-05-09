interface Props { points: number; rate: number; games: number; hits: number; streak: number; rank: number; tier: string; next: number }

export default function UserRankCard({ points, rate, games, hits, streak, rank, tier, next }: Props) {
  return <section className="rounded-2xl bg-white p-4">
    <h2 className="text-lg font-bold">내 랭킹</h2>
    <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
      <p>시즌 적중률: <b>{rate}%</b></p><p>참여 경기: <b>{games}</b></p>
      <p>적중 경기: <b>{hits}</b></p><p>연속 적중: <b>{streak}</b></p>
      <p>누적 포인트: <b>{points}</b></p><p>개인 순위: <b>{rank}위</b></p>
    </div>
    <p className="mt-2 rounded-lg bg-violet-50 p-2 text-sm">현재 티어 <b>{tier}</b> · 다음 티어까지 {next}pt</p>
  </section>;
}
