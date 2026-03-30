## Intent: API Documentation Synchronization
Tugas Anda adalah menyinkronkan dokumentasi API dengan kondisi kode backend terbaru.

## Langkah Eksekusi:
1. **Analisis Rute:** Baca struktur router dan endpoint yang ada di dalam direktori `backend/app/routers/` atau file utama FastAPI. Pahami method (GET, POST, dll) dan path-nya.
2. **Perbarui Dokumentasi:** Buka file `docs/API.md` (buat jika belum ada). Perbarui isinya agar mencerminkan daftar lengkap semua endpoint API yang aktif saat ini beserta deskripsi singkat fungsinya. Format dalam Markdown table.
3. **Cek Drift:** Bandingkan daftar endpoint yang Anda temukan dengan daftar test yang ada di `backend/tests/`.
4. **Output Laporan:** Berikan ringkasan di chat (diff-like summary) yang berisi:
   - Rute baru yang ditambahkan ke `API.md`.
   - Rute yang dihapus/tidak valid.
   - Daftar TODO (rute mana saja yang belum memiliki file test yang sesuai).