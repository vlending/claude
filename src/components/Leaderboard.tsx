export default function Leaderboard({ rows }: { rows: [string, number, number, string, string][] }) {
  return <section className="rounded-2xl bg-white p-4"><h2 className="mb-2 text-lg font-bold">전체 랭킹 TOP 10</h2>
    <div className="space-y-2">{rows.map((r, i) => <div key={r[0]} className="rounded-xl border p-2 text-sm"><p><b>{i + 1}위 {r[0]}</b> · {r[3]}</p><p>적중률 {r[1]}% · {r[2]}pt · 응원팀 {r[4]}</p></div>)}</div></section>;
}
