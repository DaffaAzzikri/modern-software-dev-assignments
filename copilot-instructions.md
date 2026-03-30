# Project Context
Aplikasi ini adalah "developer's command center" full-stack minimalis yang berada di direktori `week4/`.
- Backend: FastAPI dengan SQLite (menggunakan SQLAlchemy). Kode utama ada di `week4/backend/`.
- Frontend: UI Statis yang dilayani langsung oleh FastAPI. Kode ada di `week4/frontend/`.
- Database: SQLite dengan script seeding di `week4/data/seed.sql`.

# Coding Guidelines
- **Python Formatting:** Selalu gunakan `black` dan `ruff` style.
- **TDD (Test-Driven Development):** Saat diminta menambahkan endpoint API baru, Anda HARUS menulis failing test terlebih dahulu di direktori `week4/backend/tests/` sebelum mengimplementasikan rute di `week4/backend/app/routers/`.
- **Imports:** Pastikan import menggunakan path absolute dari root `backend` (contoh: `from backend.app.models import ...`).

# Running Commands
- Menjalankan server lokal: `uvicorn backend.app.main:app --reload` (jalankan dari dalam direktori `week4/`).
- Menjalankan test: `pytest backend/tests/` (jalankan dari dalam direktori `week4/`).