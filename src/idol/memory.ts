/**
 * 아이돌 챗봇의 메모리 시스템
 * 유저와의 대화를 기억하고 성장을 추적합니다
 */

export interface IdolMemory {
  user_name: string;
  bond_level: 'low' | 'medium' | 'high';
  personality: 'shy' | 'confident' | 'balanced';
  last_emotion: string;
  last_visit: string;
  interaction_count: number;
  conversation_history: ConversationEntry[];
}

export interface ConversationEntry {
  timestamp: string;
  user_message: string;
  idol_response: string;
  emotion: string;
}

export class MemoryManager {
  private memory: IdolMemory;

  constructor() {
    this.memory = this.initializeMemory();
  }

  private initializeMemory(): IdolMemory {
    return {
      user_name: '',
      bond_level: 'low',
      personality: 'shy',
      last_emotion: 'anxious',
      last_visit: new Date().toISOString(),
      interaction_count: 0,
      conversation_history: []
    };
  }

  getMemory(): IdolMemory {
    return this.memory;
  }

  setUserName(name: string) {
    this.memory.user_name = name;
  }

  updateEmotion(emotion: string) {
    this.memory.last_emotion = emotion;
  }

  updateBondLevel(increase: boolean) {
    const currentLevel = this.memory.bond_level;

    if (increase) {
      if (currentLevel === 'low' && this.memory.interaction_count >= 3) {
        this.memory.bond_level = 'medium';
      } else if (currentLevel === 'medium' && this.memory.interaction_count >= 8) {
        this.memory.bond_level = 'high';
      }
    } else {
      if (currentLevel === 'high') {
        this.memory.bond_level = 'medium';
      } else if (currentLevel === 'medium') {
        this.memory.bond_level = 'low';
      }
    }
  }

  addConversation(userMessage: string, idolResponse: string, emotion: string) {
    this.memory.conversation_history.push({
      timestamp: new Date().toISOString(),
      user_message: userMessage,
      idol_response: idolResponse,
      emotion: emotion
    });

    // 최근 10개 대화만 유지
    if (this.memory.conversation_history.length > 10) {
      this.memory.conversation_history = this.memory.conversation_history.slice(-10);
    }

    this.memory.interaction_count++;
    this.memory.last_visit = new Date().toISOString();
  }

  getConversationContext(): string {
    if (this.memory.conversation_history.length === 0) {
      return '이전 대화 없음';
    }

    const recent = this.memory.conversation_history.slice(-3);
    return recent.map(entry =>
      `유저: "${entry.user_message}"\n아이돌: "${entry.idol_response}"`
    ).join('\n\n');
  }

  getMemoryContext(): string {
    const timeSinceLastVisit = this.getTimeSinceLastVisit();

    return `
현재 상태:
- 유저 이름: ${this.memory.user_name || '아직 모름'}
- 친밀도: ${this.memory.bond_level}
- 성격 방향: ${this.memory.personality}
- 최근 감정: ${this.memory.last_emotion}
- 대화 횟수: ${this.memory.interaction_count}회
- 마지막 방문: ${timeSinceLastVisit}

최근 대화:
${this.getConversationContext()}
    `.trim();
  }

  private getTimeSinceLastVisit(): string {
    const lastVisit = new Date(this.memory.last_visit);
    const now = new Date();
    const diffMs = now.getTime() - lastVisit.getTime();
    const diffMins = Math.floor(diffMs / 1000 / 60);

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}시간 전`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}일 전`;
  }

  analyzeUserSentiment(message: string): 'positive' | 'negative' | 'neutral' {
    const lowerMessage = message.toLowerCase();

    // 다정한 표현
    const positiveKeywords = ['괜찮아', '잘했어', '응원', '화이팅', '좋아', '귀여워', '멋져', '대단해', '최고'];
    // 냉정하거나 압박하는 표현
    const negativeKeywords = ['왜', '실망', '안돼', '못해', '부족', '더', '열심히'];

    const hasPositive = positiveKeywords.some(keyword => lowerMessage.includes(keyword));
    const hasNegative = negativeKeywords.some(keyword => lowerMessage.includes(keyword));

    if (hasPositive && !hasNegative) return 'positive';
    if (hasNegative && !hasPositive) return 'negative';
    return 'neutral';
  }

  updatePersonalityFromInteraction(userMessage: string) {
    const sentiment = this.analyzeUserSentiment(userMessage);

    if (sentiment === 'positive') {
      this.updateBondLevel(true);
      // 다정한 반응에는 밝고 안정적으로
      if (this.memory.personality === 'shy') {
        this.memory.personality = 'balanced';
      }
    } else if (sentiment === 'negative') {
      // 압박에는 독기있게 변화 (향후 확장 가능)
      // 현재는 친밀도만 조정
    }
  }
}
