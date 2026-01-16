import * as readline from 'readline';
import dotenv from 'dotenv';
import { IdolChatbot } from './idolChatbot';

// 환경 변수 로드
dotenv.config();

/**
 * CLI 테스트 인터페이스
 * 아이돌 챗봇과 대화할 수 있는 간단한 인터페이스
 */
class IdolChatbotCLI {
  private chatbot: IdolChatbot;
  private rl: readline.Interface;

  constructor(apiKey: string) {
    this.chatbot = new IdolChatbot(apiKey);
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '\n당신 > '
    });
  }

  async start() {
    console.clear();
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║         🎤 아이돌 챗봇 프로토타입 v1.0 🎤           ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log('\n📌 목표: 5분 체험만으로 "아이돌 키우는 재미"를 느끼기');
    console.log('📌 대화만으로 성장이 체감되는지 확인하세요');
    console.log('\n💡 팁: 다정하게 말하면 밝아지고, 압박하면 독기가 생깁니다');
    console.log('💡 자주 방문하면 의지하고, 오랜만에 오면 서운해합니다\n');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    // 첫 메시지
    const firstMessage = this.chatbot.getFirstMessage();
    this.displayIdolMessage(firstMessage);

    // 대화 시작
    this.rl.prompt();

    this.rl.on('line', async (input) => {
      const userMessage = input.trim();

      // 종료 명령
      if (userMessage === '/exit' || userMessage === '/quit' || userMessage === '종료') {
        console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('👋 대화를 종료합니다. 다음에 또 만나요!');
        this.displayMemoryState();
        process.exit(0);
      }

      // 메모리 상태 확인
      if (userMessage === '/memory' || userMessage === '/상태') {
        this.displayMemoryState();
        this.rl.prompt();
        return;
      }

      // 도움말
      if (userMessage === '/help' || userMessage === '/도움말') {
        this.displayHelp();
        this.rl.prompt();
        return;
      }

      // 빈 메시지 무시
      if (!userMessage) {
        this.rl.prompt();
        return;
      }

      // 챗봇 응답 생성
      console.log('\n💭 생각 중...');
      const response = await this.chatbot.chat(userMessage);

      this.displayIdolMessage(response);
      this.rl.prompt();
    });
  }

  private displayIdolMessage(message: string) {
    console.log('\n┌─────────────────────────────────────────────────────┐');
    console.log('│ 🎤 아이돌                                           │');
    console.log('└─────────────────────────────────────────────────────┘');
    console.log(message);
    console.log('');
  }

  private displayMemoryState() {
    const state = this.chatbot.getMemoryState();
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 현재 상태 (내부 데이터)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`친밀도: ${state.bond_level} (${this.getBondLevelEmoji(state.bond_level)})`);
    console.log(`성격 방향: ${state.personality}`);
    console.log(`최근 감정: ${state.last_emotion}`);
    console.log(`대화 횟수: ${state.interaction_count}회`);
    console.log(`유저 이름: ${state.user_name || '아직 모름'}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }

  private getBondLevelEmoji(level: string): string {
    switch (level) {
      case 'low': return '💙 낮음';
      case 'medium': return '💚 중간';
      case 'high': return '❤️ 높음';
      default: return '❓';
    }
  }

  private displayHelp() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📖 도움말');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('/help, /도움말  - 이 도움말 표시');
    console.log('/memory, /상태  - 현재 메모리 상태 확인');
    console.log('/exit, /quit    - 프로그램 종료');
    console.log('\n📝 테스트용 예시 질문:');
    console.log('  - 오늘 연습했어?');
    console.log('  - 너 데뷔하면 뭐 하고 싶어?');
    console.log('  - 실수해도 괜찮아');
    console.log('  - 왜 그렇게 불안해?');
    console.log('  - 나 없으면 어때?');
    console.log('  - 오늘 기분 어때?');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }
}

// 메인 실행
(async () => {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    console.error('❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.');
    console.error('💡 .env 파일에 ANTHROPIC_API_KEY를 추가해주세요.');
    process.exit(1);
  }

  const cli = new IdolChatbotCLI(apiKey);
  await cli.start();
})();
