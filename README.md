# R2 Helper — Cloudflare R2 Uploader

Aplikasi desktop GUI untuk mengunggah folder lokal ke bucket Cloudflare R2, dilengkapi progress bar dan log upload real-time.

## Fitur

- Pilih folder sumber lewat dialog file browser
- Tentukan prefix target di R2 (contoh: `data/tiles/bali/`)
- Progress bar dan log berwarna per file
- Upload berjalan di background thread — UI tidak hang
- Membaca kredensial dari file `.env`

## Persyaratan

- Python 3.10+
- Kredensial Cloudflare R2 (Account ID, Access Key, Secret Key, Bucket Name)

## Instalasi

```bash
pip install -r requirements.txt
```

## Konfigurasi

Buat file `.env` di direktori project:

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
```

## Penggunaan

```bash
python uploader_gui.py
```

1. Klik **Browse** untuk memilih folder yang ingin diunggah.
2. Isi **R2 Target Prefix** — jalur tujuan di dalam bucket (contoh: `ortho/bali/`).
3. Klik **Start Upload** dan pantau log.
