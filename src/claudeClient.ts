import Anthropic from '@anthropic-ai/sdk';
import { DocumentLoader } from './documentLoader';

export class ClaudeClient {
  private client: Anthropic;
  private documentLoader: DocumentLoader;

  constructor(apiKey: string, documentLoader: DocumentLoader) {
    this.client = new Anthropic({ apiKey });
    this.documentLoader = documentLoader;
  }

  async answerQuestion(question: string): Promise<string> {
    try {
      // 문서에서 관련 컨텍스트 가져오기
      const context = this.documentLoader.getDocumentsAsContext();

      // Claude API에 질문
      const message = await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2048,
        temperature: 0.7,
        system: `당신은 주식회사 블렌딩의 사내 Q&A 챗봇입니다.
아래 제공된 회사 문서(사내 사규, 신입사원 매뉴얼 등)를 기반으로 직원들의 질문에 친절하고 정확하게 답변해주세요.

**답변 가이드라인:**
1. 문서에 있는 정보를 기반으로 답변하세요
2. 한국어로 친절하게 답변하세요
3. 관련 정보가 문서에 없다면 솔직하게 말씀해주세요
4. 필요한 경우 담당 부서 연락처를 안내해주세요
5. 답변은 간결하고 명확하게 작성하세요
6. 이모지를 적절히 사용하여 친근감을 표현하세요

**회사 문서:**

${context}`,
        messages: [
          {
            role: 'user',
            content: question
          }
        ]
      });

      const response = message.content[0];
      if (response.type === 'text') {
        return response.text;
      }

      return '죄송합니다. 답변을 생성하는 중 오류가 발생했습니다.';
    } catch (error) {
      console.error('Claude API Error:', error);
      throw new Error('답변을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
  }

  async getGreeting(): Promise<string> {
    return `안녕하세요! 👋 블렌딩 Q&A 봇입니다.

회사 사규, 복리후생, 업무 규정 등에 대해 궁금한 점을 물어보세요!

**예시 질문:**
• 연차는 몇 일인가요?
• 재택근무 신청은 어떻게 하나요?
• 점심 식대는 얼마나 지원되나요?
• 교육비 지원 한도는?
• 유연근무제가 가능한가요?

편하게 질문해주세요! 😊`;
  }
}
