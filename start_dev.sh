#!/bin/bash

# 종료 시 자식 프로세스도 함께 종료
trap 'kill $(jobs -p)' SIGINT

echo "🚀 로또 번호 추천 시스템 개발 서버를 시작합니다..."

# 1. 백엔드 실행 (포트 8000)
echo "backend 서버 실행 중..."
cd backend
PYTHONPATH=.. uv run uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 2. 프론트엔드 실행 (포트 5173)
echo "frontend 서버 실행 중..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 서버가 시작되었습니다!"
echo "- Frontend: http://localhost:5173"
echo "- Backend: http://localhost:8000/docs"
echo "종료하려면 Ctrl+C를 누르세요."

wait
