import { Candidate } from '../types';

export default function ResultPanel({ candidates, finalMvpId, pickedId, earned }: { candidates: Candidate[]; finalMvpId: string; pickedId: string | null; earned: number }) {
  const finalMvp = candidates.find((c) => c.id === finalMvpId);
  return <section className="space-y-3 rounded-2xl bg-white p-4">
    <h2 className="text-lg font-bold">투표 결과</h2>
    {candidates.map((c) => <div key={c.id}><div className="mb-1 flex justify-between text-sm"><span>{c.name}</span><span>{c.voteShare}%</span></div><div className="h-2 rounded bg-slate-200"><div className="h-full rounded bg-blue-500" style={{ width: `${c.voteShare}%` }} /></div></div>)}
    <p className="rounded-xl bg-amber-50 p-2 text-sm">최종 Fan MVP: <b>{finalMvp?.name}</b></p>
    <p className="text-sm">내 선택: <b>{candidates.find((c) => c.id === pickedId)?.name ?? '미선택'}</b> · {pickedId === finalMvpId ? '적중!' : '아쉽게 빗나감'}</p>
    <p className="text-sm font-semibold text-blue-700">획득 포인트: +{earned}</p>
  </section>;
}
