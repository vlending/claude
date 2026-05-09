import { Game } from '../types';

export default function GameCard({ game, onSelect, isActive }: { game: Game; onSelect: () => void; isActive: boolean }) {
  return (
    <button onClick={onSelect} className={`w-full rounded-2xl border p-4 text-left ${isActive ? 'border-blue-600 bg-blue-50' : 'border-slate-200 bg-white'}`}>
      <div className="mb-2 flex items-center justify-between text-xs"><span>{game.status}</span><span>{game.stadium}</span></div>
      <p className="font-semibold">{game.awayTeam} {game.awayScore} : {game.homeScore} {game.homeTeam}</p>
      <p className="mt-1 text-xs text-slate-500">{game.status === '투표중' ? 'Fan MVP 투표 가능' : '상세 보기'}</p>
    </button>
  );
}
