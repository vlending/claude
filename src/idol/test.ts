import dotenv from 'dotenv';
import { IdolChatbot } from './idolChatbot';

dotenv.config();

/**
 * 자동 테스트 스크립트
 * 프로토타입이 제대로 작동하는지 확인
 */
async function testIdolChatbot() {
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║      🎤 아이돌 챗봇 프로토타입 자동 테스트 🎤        ║');
  console.log('╚════════════════════════════════════════════════════════╝\n');

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.');
    process.exit(1);
  }

  const chatbot = new IdolChatbot(apiKey);

  // 첫 메시지
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📝 테스트 1: 첫 메시지');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  const firstMessage = chatbot.getFirstMessage();
  console.log('\n🎤 아이돌:');
  console.log(firstMessage);
  console.log('\n✅ 첫 메시지 출력 완료\n');

  // 테스트 대화 목록
  const testQuestions = [
    '오늘 연습했어?',
    '실수해도 괜찮아. 너 잘하고 있어!',
    '너 데뷔하면 뭐 하고 싶어?'
  ];

  for (let i = 0; i < testQuestions.length; i++) {
    const question = testQuestions[i];

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`📝 테스트 ${i + 2}: 대화 ${i + 1}회차`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`\n당신: ${question}`);
    console.log('💭 생각 중...\n');

    try {
      const response = await chatbot.chat(question);
      console.log('🎤 아이돌:');
      console.log(response);

      // 메모리 상태 확인
      const memory = chatbot.getMemoryState();
      console.log('\n📊 현재 상태:');
      console.log(`   친밀도: ${memory.bond_level}`);
      console.log(`   성격: ${memory.personality}`);
      console.log(`   감정: ${memory.last_emotion}`);
      console.log(`   대화 횟수: ${memory.interaction_count}회`);

      console.log('\n✅ 응답 생성 완료\n');

      // API 호출 간 딜레이 (Rate limit 방지)
      if (i < testQuestions.length - 1) {
        console.log('⏳ 다음 테스트까지 2초 대기...\n');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    } catch (error) {
      console.error(`\n❌ 오류 발생: ${error}`);
      process.exit(1);
    }
  }

  // 최종 결과
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🎉 테스트 완료!');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  const finalMemory = chatbot.getMemoryState();
  console.log('\n📊 최종 상태:');
  console.log(`   친밀도: ${finalMemory.bond_level} (${getBondLevelEmoji(finalMemory.bond_level)})`);
  console.log(`   성격: ${finalMemory.personality}`);
  console.log(`   감정: ${finalMemory.last_emotion}`);
  console.log(`   총 대화 횟수: ${finalMemory.interaction_count}회`);

  console.log('\n✅ 모든 테스트 통과!');
  console.log('\n💡 실제 대화를 원하시면: npm run idol');
  console.log('');
}

function getBondLevelEmoji(level: string): string {
  switch (level) {
    case 'low': return '💙 낮음';
    case 'medium': return '💚 중간';
    case 'high': return '❤️ 높음';
    default: return '❓';
  }
}

// 실행
testIdolChatbot().catch(error => {
  console.error('❌ 치명적 오류:', error);
  process.exit(1);
});
