# FKPhone Tracker
Phone Number Intelligence & OSINT (FastAPI + Streamlit) — FKStudio IT Solution, v1.0.0.

## Menjalankan
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # isi API_KEY
uvicorn app.main:app --app-dir backend --reload          # http://localhost:8000/docs
streamlit run frontend/app.py                            # http://localhost:8501
pytest
```
Masukkan API key di halaman **Settings** (atau env `API_KEY`).

## Catatan keamanan & privasi
- Semua endpoint (kecuali submit/revoke lokasi & halaman `/share/{token}`) butuh header `X-API-Key`; ada rate limiting per IP.
- Nomor di log di-masking. Retensi riwayat: `HISTORY_RETENTION_DAYS`.
- Lokasi: hanya via tautan bertoken (hash SHA-256 disimpan), persetujuan eksplisit, kedaluwarsa, dan revoke menghapus koordinat. Tidak ada pelacakan dari nomor HP.
- Operator/wilayah = metadata penomoran; bukan lokasi/operator aktual (portabilitas).
- Produksi: jalankan di belakang HTTPS (reverse proxy); Geolocation API browser mewajibkan HTTPS.
