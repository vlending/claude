import { Game } from '../types';
import CandidateCard from './CandidateCard';

interface Props { game: Game; selectedId: string | null; onSelect: (id: string) => void; onVote: () => void; onAd: () => void; tickets: number; voted: boolean }

export default function VotePanel({ game, selectedId, onSelect, onVote, onAd, tickets, voted }: Props) {
  return <section className="space-y-3 rounded-2xl bg-white p-4">
    <h2 className="text-lg font-bold">MVP 후보</h2>
    <p className="text-sm">보유 투표권: <b>{tickets}</b>장</p>
    {game.candidates.map((c) => <CandidateCard key={c.id} c={c} selected={selectedId === c.id} onClick={() => onSelect(c.id)} />)}
    {tickets === 0 && !voted && <button onClick={onAd} className="w-full rounded-xl bg-emerald-600 p-3 font-semibold text-white">광고 보고 투표권 받기 (+3)</button>}
    <button disabled={voted || !selectedId || tickets < 1} onClick={onVote} className="w-full rounded-xl bg-blue-600 p-3 font-semibold text-white disabled:bg-slate-300">{voted ? '이미 투표 완료' : '투표하기'}</button>
  </section>;
}
