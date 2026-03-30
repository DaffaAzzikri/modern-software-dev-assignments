# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Akhmad Daffa Azzikri** \
SUNet ID: **2410817110002** \
Citations: **Anthropic Claude Code best practices (diadaptasi untuk GitHub Copilot), GitHub Copilot Documentation**

This assignment took me about **30 minutes** to do. 


## YOUR RESPONSES
### Automation #1
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Mengadaptasi fungsi CLAUDE.md dari Anthropic untuk memberikan konteks repositori, aturan linter, dan panduan arsitektur (seperti Test-Driven Development) secara otomatis ke AI agent menggunakan fitur Copilot Custom Instructions.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goals:** Memastikan Copilot selalu menggunakan black dan ruff, serta menulis test sebelum membuat rute baru. \
> **Inputs:** Prompt natural language dari user. \
> **Outputs:** Kode yang dihasilkan otomatis mengikuti panduan arsitektur.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> Buat file `copilot-instructions.md` di root direktori. Di VS Code Copilot Chat, file ini bisa dipanggil eksplisit dengan referensi `#file:copilot-instructions.md`. \
> **Expected output:** Copilot menerapkan aturan linter dan TDD dalam setiap respons code generation. \
> **Rollback:** Cukup dengan menghapus file `copilot-instructions.md`.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (Manual):** Developer harus mengetik instruksi linter dan TDD berulang kali di setiap chat session. \
> **After (Automated):** Aturan main otomatis diterapkan sebagai invisible system prompt dalam setiap interaksi Copilot.

e. How you used the automation to enhance the starter application
> Digunakan untuk memaksa Copilot membuat file test kosong terlebih dahulu setiap kali saya memintanya membuat endpoint FastAPI baru, memastikan Test-Driven Development workflow sejak awal development.


### Automation #2
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Mengadaptasi custom slash command (contoh: docs-sync.md) menggunakan sistem Prompt Template berbasis markdown yang dieksekusi oleh `@workspace` di Copilot.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goals:** Sinkronisasi router backend di `backend/app/routers/` dengan dokumentasi `docs/API.md`, dan audit test coverage. \
> **Inputs:** File markdown `.prompts/docs-sync.md`. \
> **Outputs:** Tabel API.md, diff-summary, dan daftar TODO untuk endpoint tanpa test.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> Buka Copilot Chat dan ketik: `@workspace tolong eksekusi alur kerja yang ada di #file:.prompts/docs-sync.md`. \
> **Expected output:** File `docs/API.md` tergenenerasi dengan daftar endpoint lengkap, laporan diff di chat, dan TODO list untuk endpoint tanpa test coverage. \
> **Rollback:** Via Source Control (Git) "Discard changes" atau hapus file `docs/API.md` yang tergenenerasi.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (Manual):** Mencocokkan rute dan test harus dilakukan manual secara visual yang rentan terlewat, memakan waktu dan error-prone. \
> **After (Automated):** Audit selesai dalam hitungan detik dengan output laporan di chat yang comprehensif dan akurat.

e. How you used the automation to enhance the starter application
> Saya mengeksekusinya dan automasi berhasil mendeteksi 8 active endpoints di backend. Automasi ini menemukan 1 drift: rute `GET /notes/{note_id}` tidak memiliki test case. Saya kemudian menggunakan hasil laporan ini untuk membuat test case yang hilang tersebut di `test_notes.py`, sehingga test coverage menjadi 100% untuk modul notes.


### *(Optional) Automation #3*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> TODO

b. Design of each automation, including goals, inputs/outputs, steps
> TODO

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> TODO

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

e. How you used the automation to enhance the starter application
> TODO
