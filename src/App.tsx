import { useMemo, useState } from 'react';
import GameCard from './components/GameCard';
import Leaderboard from './components/Leaderboard';
import ProposalSummary from './components/ProposalSummary';
import ResultPanel from './components/ResultPanel';
import UserRankCard from './components/UserRankCard';
import VotePanel from './components/VotePanel';
import { games, initialUser, leaderboardSeed } from './data/mockData';

const tiers = [{ n: 'Rookie', p: 0 }, { n: 'Bronze', p: 300 }, { n: 'Silver', p: 600 }, { n: 'Gold', p: 1000 }, { n: 'Platinum', p: 1500 }, { n: 'Diamond', p: 2000 }, { n: 'Legend', p: 3000 }];

const getTier = (points: number) => tiers.slice().reverse().find((t) => points >= t.p)!;

export default function App() {
  const [user, setUser] = useState(initialUser);
  const [selectedGameId, setSelectedGameId] = useState(games[1].id);
  const [picked, setPicked] = useState<Record<string, string>>({});
  const [revealed, setRevealed] = useState<Record<string, boolean>>({});
  const game = games.find((g) => g.id === selectedGameId)!;

  const myPick = picked[game.id] ?? null;
  const voted = Boolean(myPick);
  const earned = useMemo(() => {
    if (!myPick || !revealed[game.id]) return 0;
    if (myPick !== game.finalMvpId) return 0;
    const seed = game.candidates.find((c) => c.id === myPick)?.seedSupportRate ?? 100;
    return 100 + (seed < 30 ? 50 : 0);
  }, [game, myPick, revealed]);

  const handleVote = () => {
    if (!myPick || user.tickets < 1) return;
    setUser((u) => ({ ...u, tickets: u.tickets - 1, gamesParticipated: u.gamesParticipated + 1 }));
  };

  const reveal = () => {
    if (!myPick || revealed[game.id]) return;
    const hit = myPick === game.finalMvpId;
    const seed = game.candidates.find((c) => c.id === myPick)?.seedSupportRate ?? 100;
    const point = hit ? 100 + (seed < 30 ? 50 : 0) : 0;
    setUser((u) => ({ ...u, points: u.points + point, hits: u.hits + (hit ? 1 : 0), streak: hit ? u.streak + 1 : 0, bestStreak: hit ? Math.max(u.bestStreak, u.streak + 1) : u.bestStreak }));
    setRevealed((r) => ({ ...r, [game.id]: true }));
  };

  const tier = getTier(user.points);
  const nextTier = tiers.find((t) => t.p > user.points);
  const rate = Math.round((user.hits / Math.max(1, user.gamesParticipated)) * 100);

  return <main className="mx-auto max-w-md space-y-4 p-4">
    <h1 className="text-2xl font-extrabold">KBO Fan MVP</h1>
    <section className="space-y-2">{games.map((g) => <GameCard key={g.id} game={g} isActive={g.id === game.id} onSelect={() => setSelectedGameId(g.id)} />)}</section>
    {game.candidates.length > 0 && <VotePanel game={game} selectedId={myPick} tickets={user.tickets} voted={voted} onSelect={(id) => setPicked((p) => (p[game.id] ? p : { ...p, [game.id]: id }))} onVote={handleVote} onAd={() => setUser((u) => ({ ...u, tickets: u.tickets + 3 }))} />}
    {voted && <button onClick={reveal} className="w-full rounded-xl bg-slate-900 p-3 font-semibold text-white">결과 공개</button>}
    {revealed[game.id] && <ResultPanel candidates={game.candidates} finalMvpId={game.finalMvpId} pickedId={myPick} earned={earned} />}
    <UserRankCard points={user.points} rate={rate} games={user.gamesParticipated} hits={user.hits} streak={user.streak} rank={6} tier={tier.n} next={nextTier ? nextTier.p - user.points : 0} />
    <Leaderboard rows={leaderboardSeed.map((r) => (r[0] === user.nickname ? [r[0], rate, user.points, getTier(user.points).n, r[4]] as [string, number, number, string, string] : r as [string, number, number, string, string]))} />
    <ProposalSummary />
  </main>;
}
