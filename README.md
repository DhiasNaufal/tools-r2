# XYZ Background Remover & R2 Sync Tools

Kumpulan alat untuk memproses folder XYZ Tiles (peta) untuk menghapus background (putih/hitam) dan mensinkronisasikannya dengan penyimpanan Cloudflare R2.

## Fitur Utama

- **Hapus Background Batch**: Menghapus warna putih, hitam, atau keduanya dari ribuan file PNG secara otomatis.
- **Dukungan Struktur XYZ**: Mempertahankan struktur folder `z/x/y.png` selama pemrosesan.
- **GUI Uploader**: Antarmuka grafis modern untuk mengunggah hasil proses ke Cloudflare R2.
- **Secure Credentials**: Penyimpanan kunci akses aman menggunakan file `.env`.
- **Threaded Processing**: Proses upload tidak mengganggu antarmuka (tidak hang).

## Persyaratan Sistem

- Python 3.10 atau lebih baru
- Kredensial Cloudflare R2 (Account ID, Access Key, Secret Key)

## Instalasi

1. Clone atau download repositori ini.
2. Instal dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```

## Konfigurasi

Buat file bernama `.env` di direktori utama (sudah disediakan contohnya) dan isi dengan kredensial R2 Anda:

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
```

## Penggunaan

### 1. Menghapus Background Gambar (`main.py`)

Gunakan script ini untuk mengolah folder XYZ tiles lokal Anda.

- Buka `main.py` dan sesuaikan variabel `TILES_FOLDER` ke lokasi folder Anda.
- Jalankan:
  ```bash
  python main.py
  ```
  Script akan menghasilkan folder baru dengan akhiran `_processed` yang berisi gambar transparan.

### 2. Mengunggah ke Cloud (GUI - Direkomendasikan)

Gunakan aplikasi desktop untuk mengunggah folder hasil proses ke Cloudflare R2.

- Jalankan:
  ```bash
  python uploader_gui.py
  ```
- Pilih folder sumber, tentukan prefix target di R2 (contoh: `ortho/bali/`), lalu klik **Start Upload**.

### 3. Mengunduh dari Cloud (`download_rt.py`)

Jika Anda perlu mengunduh data dari R2 kembali ke komputer lokal:

```bash
python download_rt.py <source_prefix_di_r2> <target_folder_lokal>
# Contoh: python download_rt.py data/tiles/ local_backup/
```

### 4. Mengunggah via CLI (`upload-with-args.py`)

Versi CLI dari uploader jika Anda lebih suka menggunakan command line:

```bash
python upload-with-args.py <folder_sumber> <prefix_target_r2>
```

## Daftar File Penting

- `uploader_gui.py`: Aplikasi GUI utama untuk upload.
- `main.py`: Script utama pemrosesan background.
- `.env`: Penyimpanan rahasia (Jangan dibagikan!).
- `requirements.txt`: Daftar pustaka Python yang diperlukan.

## Lisensi

Proyek ini dikembangkan untuk kebutuhan internal pemrosesan data XYZ tiles.
