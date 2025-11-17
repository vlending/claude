import { App, LogLevel } from '@slack/bolt';
import dotenv from 'dotenv';
import path from 'path';
import { DocumentLoader } from './documentLoader';
import { ClaudeClient } from './claudeClient';

// 환경 변수 로드
dotenv.config();

// 필수 환경 변수 확인
const requiredEnvVars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'ANTHROPIC_API_KEY'];
const missingEnvVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingEnvVars.length > 0) {
  console.error('❌ Missing required environment variables:', missingEnvVars.join(', '));
  process.exit(1);
}

// Slack 앱 초기화
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  appToken: process.env.SLACK_APP_TOKEN,
  socketMode: true,
  logLevel: LogLevel.INFO
});

// 문서 로더 및 Claude 클라이언트 초기화
const docsPath = path.join(__dirname, '..', 'docs');
const documentLoader = new DocumentLoader(docsPath);
const claudeClient = new ClaudeClient(process.env.ANTHROPIC_API_KEY!, documentLoader);

// 앱 멘션 이벤트 처리
app.event('app_mention', async ({ event, client, say }) => {
  try {
    // 사용자 질문 추출 (멘션 제거)
    const question = event.text.replace(/<@[A-Z0-9]+>/g, '').trim();

    // 인사말 요청 처리
    if (!question || question === '안녕' || question === 'hi' || question === 'hello' || question === '도움말') {
      const greeting = await claudeClient.getGreeting();
      await say({
        text: greeting,
        thread_ts: event.ts
      });
      return;
    }

    // 로딩 메시지 표시
    const loadingMsg = await say({
      text: '생각 중입니다... 🤔',
      thread_ts: event.ts
    });

    // Claude API를 통해 답변 생성
    const answer = await claudeClient.answerQuestion(question);

    // 로딩 메시지 업데이트
    await client.chat.update({
      channel: event.channel,
      ts: loadingMsg.ts!,
      text: answer
    });

  } catch (error) {
    console.error('Error handling app mention:', error);
    await say({
      text: '죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 😢',
      thread_ts: event.ts
    });
  }
});

// DM 메시지 처리
app.message(async ({ message, say }) => {
  // 봇 자신의 메시지는 무시 (무한 루프 방지)
  if (message.subtype === 'bot_message') {
    return;
  }

  const answer = await claudeClient.answerQuestion((message as any).text);
  await say(answer);
});

// 슬래시 커맨드: /handbook
app.command('/handbook', async ({ command, ack, respond }) => {
  await ack();

  try {
    const query = command.text.trim();

    if (!query) {
      const greeting = await claudeClient.getGreeting();
      await respond(greeting);
      return;
    }

    // Claude API를 통해 답변 생성
    const answer = await claudeClient.answerQuestion(query);
    await respond({
      response_type: 'ephemeral',
      text: answer
    });

  } catch (error) {
    console.error('Error handling /handbook command:', error);
    await respond({
      response_type: 'ephemeral',
      text: '죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 😢'
    });
  }
});

// 앱 시작
(async () => {
  const port = process.env.PORT || 3000;
  await app.start(port);

  console.log('⚡️ Blending Q&A Bot is running!');
  console.log(`📚 Loaded ${documentLoader.getAllDocuments().length} documents`);
  console.log(`🤖 Bot is ready to answer questions!`);
})();
