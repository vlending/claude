export type GameStatus = '예정' | '진행중' | '종료' | '투표중' | '결과발표';

export interface Candidate {
  id: string;
  name: string;
  team: string;
  position: string;
  statLine: string;
  reason: string;
  seedSupportRate: number;
  voteShare: number;
}

export interface Game {
  id: string;
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  stadium: string;
  status: GameStatus;
  candidates: Candidate[];
  finalMvpId: string;
}

export interface UserProfile {
  nickname: string;
  supportTeam: string;
  tickets: number;
  points: number;
  gamesParticipated: number;
  hits: number;
  streak: number;
  bestStreak: number;
}
