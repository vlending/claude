import Anthropic from '@anthropic-ai/sdk';
import { MemoryManager } from './memory';
import { IDOL_SYSTEM_PROMPT, FIRST_MESSAGE, getResponseGuideline } from './systemPrompt';

/**
 * 아이돌 챗봇 클라이언트
 * Claude API를 사용하여 가상 아이돌과 대화
 */
export class IdolChatbot {
  private client: Anthropic;
  private memory: MemoryManager;

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
    this.memory = new MemoryManager();
  }

  /**
   * 첫 메시지 가져오기
   */
  getFirstMessage(): string {
    return FIRST_MESSAGE;
  }

  /**
   * 유저 메시지에 응답
   */
  async chat(userMessage: string): Promise<string> {
    try {
      // 유저 감정 분석 및 성격 업데이트
      this.memory.updatePersonalityFromInteraction(userMessage);

      // 현재 메모리 상태
      const memoryState = this.memory.getMemory();
      const memoryContext = this.memory.getMemoryContext();
      const responseGuideline = getResponseGuideline(
        memoryState.bond_level,
        memoryState.personality,
        memoryState.interaction_count
      );

      // Claude API 호출
      const message = await this.client.messages.create({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        temperature: 0.9, // 더 감정적이고 다양한 응답
        system: `${IDOL_SYSTEM_PROMPT}

${memoryContext}

${responseGuideline}`,
        messages: [
          {
            role: 'user',
            content: userMessage
          }
        ]
      });

      const response = message.content[0];
      let idolResponse = '';

      if (response.type === 'text') {
        idolResponse = response.text;
      } else {
        idolResponse = '...미안, 지금은 말하기가 좀 어려워.';
      }

      // 응답에서 감정 추출 (간단한 휴리스틱)
      const emotion = this.extractEmotion(idolResponse);

      // 대화 기록에 추가
      this.memory.addConversation(userMessage, idolResponse, emotion);
      this.memory.updateEmotion(emotion);

      return idolResponse;

    } catch (error) {
      console.error('Idol Chatbot Error:', error);
      return '...잠깐, 너무 떨려서 말이 안 나와. 조금만 기다려줄래?';
    }
  }

  /**
   * 응답에서 감정 추출 (간단한 휴리스틱)
   */
  private extractEmotion(response: string): string {
    const lowerResponse = response.toLowerCase();

    if (lowerResponse.includes('무서') || lowerResponse.includes('떨') || lowerResponse.includes('불안')) {
      return 'anxious';
    }
    if (lowerResponse.includes('고마') || lowerResponse.includes('행복') || lowerResponse.includes('기뻐')) {
      return 'happy';
    }
    if (lowerResponse.includes('슬프') || lowerResponse.includes('외로') || lowerResponse.includes('서운')) {
      return 'sad';
    }
    if (lowerResponse.includes('용기') || lowerResponse.includes('힘내') || lowerResponse.includes('해볼')) {
      return 'hopeful';
    }

    return 'neutral';
  }

  /**
   * 현재 메모리 상태 가져오기 (디버깅용)
   */
  getMemoryState() {
    return this.memory.getMemory();
  }

  /**
   * 유저 이름 설정
   */
  setUserName(name: string) {
    this.memory.setUserName(name);
  }
}
