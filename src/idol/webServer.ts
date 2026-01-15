import express from 'express';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';
import { IdolChatbot } from './idolChatbot';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../../public')));

// 세션 관리 (간단한 인메모리 저장소)
const sessions = new Map<string, IdolChatbot>();

// API 키 확인
const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  console.error('❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.');
  process.exit(1);
}

/**
 * 세션 ID 생성
 */
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
}

/**
 * 세션 가져오기 또는 생성
 */
function getOrCreateSession(sessionId?: string): { sessionId: string; chatbot: IdolChatbot; isNew: boolean } {
  if (sessionId && sessions.has(sessionId)) {
    return {
      sessionId,
      chatbot: sessions.get(sessionId)!,
      isNew: false
    };
  }

  const newSessionId = generateSessionId();
  const chatbot = new IdolChatbot(apiKey!);
  sessions.set(newSessionId, chatbot);

  return {
    sessionId: newSessionId,
    chatbot,
    isNew: true
  };
}

/**
 * GET / - 메인 페이지
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../../public/index.html'));
});

/**
 * POST /api/chat - 채팅 메시지 전송
 */
app.post('/api/chat', async (req, res) => {
  try {
    const { message, sessionId } = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: '메시지가 필요합니다.' });
    }

    const session = getOrCreateSession(sessionId);
    const response = await session.chatbot.chat(message);
    const memoryState = session.chatbot.getMemoryState();

    res.json({
      sessionId: session.sessionId,
      response,
      memory: {
        bond_level: memoryState.bond_level,
        personality: memoryState.personality,
        last_emotion: memoryState.last_emotion,
        interaction_count: memoryState.interaction_count
      }
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: '응답 생성 중 오류가 발생했습니다.' });
  }
});

/**
 * POST /api/session/new - 새 세션 생성
 */
app.post('/api/session/new', (req, res) => {
  const session = getOrCreateSession();
  const firstMessage = session.chatbot.getFirstMessage();

  res.json({
    sessionId: session.sessionId,
    firstMessage
  });
});

/**
 * GET /api/session/:sessionId/memory - 세션 메모리 상태 조회
 */
app.get('/api/session/:sessionId/memory', (req, res) => {
  const { sessionId } = req.params;

  if (!sessions.has(sessionId)) {
    return res.status(404).json({ error: '세션을 찾을 수 없습니다.' });
  }

  const chatbot = sessions.get(sessionId)!;
  const memoryState = chatbot.getMemoryState();

  res.json({
    bond_level: memoryState.bond_level,
    personality: memoryState.personality,
    last_emotion: memoryState.last_emotion,
    interaction_count: memoryState.interaction_count,
    user_name: memoryState.user_name
  });
});

/**
 * DELETE /api/session/:sessionId - 세션 삭제
 */
app.delete('/api/session/:sessionId', (req, res) => {
  const { sessionId } = req.params;

  if (sessions.has(sessionId)) {
    sessions.delete(sessionId);
    res.json({ message: '세션이 삭제되었습니다.' });
  } else {
    res.status(404).json({ error: '세션을 찾을 수 없습니다.' });
  }
});

/**
 * GET /api/health - 헬스체크
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    activeSessions: sessions.size,
    timestamp: new Date().toISOString()
  });
});

// 서버 시작
app.listen(PORT, () => {
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║       🎤 아이돌 챗봇 웹 서버가 시작되었습니다! 🎤      ║');
  console.log('╚════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`🌐 서버 주소: http://localhost:${PORT}`);
  console.log(`🔗 브라우저에서 접속하세요!`);
  console.log('');
  console.log('📊 API 엔드포인트:');
  console.log(`  POST   /api/session/new          - 새 세션 생성`);
  console.log(`  POST   /api/chat                 - 메시지 전송`);
  console.log(`  GET    /api/session/:id/memory   - 메모리 상태 조회`);
  console.log(`  DELETE /api/session/:id          - 세션 삭제`);
  console.log(`  GET    /api/health               - 헬스체크`);
  console.log('');
  console.log('💡 종료하려면 Ctrl+C를 누르세요.');
  console.log('');
});

// 정리 작업
process.on('SIGINT', () => {
  console.log('\n\n👋 서버를 종료합니다...');
  process.exit(0);
});
