import { Candidate } from '../types';

export default function CandidateCard({ c, selected, onClick }: { c: Candidate; selected: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-full rounded-xl border p-3 text-left ${selected ? 'border-blue-600 bg-blue-50' : 'border-slate-200 bg-white'}`}>
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-full bg-slate-200 text-sm font-bold">{c.name[0]}</div>
        <div>
          <p className="font-semibold">{c.name} <span className="text-xs text-slate-500">({c.team} · {c.position})</span></p>
          <p className="text-xs">{c.statLine}</p>
          <p className="text-xs text-slate-500">선정 사유: {c.reason}</p>
        </div>
      </div>
    </button>
  );
}
