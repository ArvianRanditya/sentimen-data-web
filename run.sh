#!/usr/bin/env bash
# SentimenAI - Runner Script untuk macOS + OrbStack / Docker

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Buat backend/.env dari .env.example jika belum ada
if [ ! -f backend/.env ] && [ -f backend/.env.example ]; then
  echo "📄 Membuat backend/.env dari backend/.env.example..."
  cp backend/.env.example backend/.env
fi

ACTION="${1:-up}"

case "$ACTION" in
  start|up)
    echo "🚀 Menjalankan SentimenAI dengan Docker (OrbStack)..."
    docker compose up -d
    echo ""
    echo "✅ Aplikasi berhasil dijalankan!"
    echo "👉 Frontend: http://localhost:5173  (atau http://sentimen-frontend.orb.local)"
    echo "👉 Backend API: http://localhost:8000 (Docs: http://localhost:8000/docs)"
    echo ""
    echo "💡 Jalankan './run.sh logs' untuk melihat log, atau './run.sh stop' untuk menghentikan."
    ;;
  build)
    echo "🔨 Membangun ulang dan menyalakan container..."
    docker compose up --build -d
    echo "✅ Build selesai & container menyala!"
    ;;
  stop|down)
    echo "🛑 Menghentikan container SentimenAI..."
    docker compose down
    echo "✅ Semua container telah dihentikan."
    ;;
  restart)
    echo "🔄 Merestart container..."
    docker compose restart
    echo "✅ Selesai direstart."
    ;;
  logs)
    docker compose logs -f
    ;;
  status|ps)
    docker compose ps
    ;;
  *)
    echo "Gunakan: $0 {start|stop|restart|build|logs|status}"
    exit 1
    ;;
esac
