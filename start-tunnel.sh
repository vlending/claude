#!/bin/bash

echo "🌐 아이돌 챗봇 외부 접속 URL 생성 중..."
echo ""

# 서버가 실행 중인지 확인
if ! curl -s http://localhost:3000/api/health > /dev/null; then
  echo "❌ 서버가 실행되고 있지 않습니다."
  echo "먼저 서버를 실행하세요: npm run idol:web"
  exit 1
fi

echo "✅ 서버가 실행 중입니다."
echo ""
echo "터널링 시작..."
echo ""

# localtunnel 실행
npx localtunnel --port 3000
