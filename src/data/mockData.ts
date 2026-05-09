import { Game, UserProfile } from '../types';

export const initialUser: UserProfile = {
  nickname: 'FanCaptain',
  supportTeam: 'LG Twins',
  tickets: 1,
  points: 420,
  gamesParticipated: 8,
  hits: 5,
  streak: 1,
  bestStreak: 3
};

export const games: Game[] = [
  { id: 'g1', awayTeam: 'LG Twins', homeTeam: 'Doosan Bears', awayScore: 5, homeScore: 3, stadium: '잠실', status: '결과발표', finalMvpId: 'c3', candidates: [
      { id: 'c1', name: '오스틴', team: 'LG', position: '1B', statLine: '5타수 2안타 1홈런', reason: '역전 홈런', seedSupportRate: 35, voteShare: 30 },
      { id: 'c2', name: '양의지', team: '두산', position: 'C', statLine: '4타수 2안타 2타점', reason: '추격 적시타', seedSupportRate: 42, voteShare: 28 },
      { id: 'c3', name: '임찬규', team: 'LG', position: 'P', statLine: '6이닝 1실점 7K', reason: '위기관리 호투', seedSupportRate: 23, voteShare: 42 }
    ] },
  { id: 'g2', awayTeam: 'KIA Tigers', homeTeam: 'Samsung Lions', awayScore: 8, homeScore: 4, stadium: '대구', status: '투표중', finalMvpId: 'c4', candidates: [
      { id: 'c4', name: '김도영', team: 'KIA', position: '3B', statLine: '4타수 3안타 1홈런 3타점', reason: '결승 홈런', seedSupportRate: 28, voteShare: 49 },
      { id: 'c5', name: '구자욱', team: '삼성', position: 'OF', statLine: '4타수 2안타 2타점', reason: '클러치 타점', seedSupportRate: 38, voteShare: 26 },
      { id: 'c6', name: '네일', team: 'KIA', position: 'P', statLine: '7이닝 2실점 8K', reason: '선발 지배', seedSupportRate: 34, voteShare: 25 }
    ] },
  { id: 'g3', awayTeam: 'Hanwha Eagles', homeTeam: 'Lotte Giants', awayScore: 2, homeScore: 2, stadium: '사직', status: '진행중', finalMvpId: 'c7', candidates: [
      { id: 'c7', name: '류현진', team: '한화', position: 'P', statLine: '현재 5이닝 1실점 6K', reason: '선발 호투', seedSupportRate: 45, voteShare: 0 },
      { id: 'c8', name: '노시환', team: '한화', position: '3B', statLine: '3타수 1안타 1타점', reason: '선취 타점', seedSupportRate: 22, voteShare: 0 },
      { id: 'c9', name: '전준우', team: '롯데', position: 'OF', statLine: '3타수 2안타', reason: '테이블 세팅', seedSupportRate: 33, voteShare: 0 }
    ] },
  { id: 'g4', awayTeam: 'SSG Landers', homeTeam: 'NC Dinos', awayScore: 0, homeScore: 0, stadium: '창원', status: '예정', finalMvpId: 'c10', candidates: [] },
  { id: 'g5', awayTeam: 'Kiwoom Heroes', homeTeam: 'KT Wiz', awayScore: 0, homeScore: 0, stadium: '수원', status: '예정', finalMvpId: 'c11', candidates: [] }
];

export const leaderboardSeed = [
  ['Slugger77', 71, 1740, 'Diamond', 'KIA Tigers'],
  ['BlueStorm', 69, 1650, 'Platinum', 'Samsung Lions'],
  ['JamsilKing', 67, 1520, 'Platinum', 'LG Twins'],
  ['BearClutch', 63, 1400, 'Gold', 'Doosan Bears'],
  ['MVPHunter', 61, 1330, 'Gold', 'Hanwha Eagles'],
  ['FanCaptain', 62, 520, 'Silver', 'LG Twins'],
  ['LotteWave', 59, 990, 'Silver', 'Lotte Giants'],
  ['WizPower', 58, 910, 'Silver', 'KT Wiz'],
  ['HeroClock', 56, 850, 'Bronze', 'Kiwoom Heroes'],
  ['DinoFocus', 54, 790, 'Bronze', 'NC Dinos']
];
