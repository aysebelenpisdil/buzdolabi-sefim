#!/bin/bash

# Smart Fridge Chef - Start Script
# Bu script hem backend hem frontend'i başlatır

echo "🚀 Smart Fridge Chef Başlatılıyor..."

# Port 3001 ve 3000 kullanımdaysa önceki process'leri sonlandır
if lsof -ti:3001 >/dev/null 2>&1; then
    echo "⚠️  Port 3001 kullanımda, önceki backend sonlandırılıyor..."
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi
if lsof -ti:3000 >/dev/null 2>&1; then
    echo "⚠️  Port 3000 kullanımda, önceki frontend sonlandırılıyor..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Backend'i arka planda başlat
echo "📦 Backend başlatılıyor..."
cd backend
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 3001 &
BACKEND_PID=$!
cd ..

# Kısa bir bekleme
sleep 3

# Frontend'i arka planda başlat
echo "⚛️  Frontend başlatılıyor..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Servisler başlatıldı!"
echo "📡 Backend: http://localhost:3001"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Durdurmak için: kill $BACKEND_PID $FRONTEND_PID"
echo "veya Ctrl+C"

# Process'leri bekle
wait $BACKEND_PID $FRONTEND_PID

