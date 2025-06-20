# Telegram Domain Checker Bot

Bot Telegram otomatis untuk memeriksa status domain yang terkena Nawala atau diblokir oleh pemerintah Indonesia dengan pembaruan setiap 30 menit.

## Fitur

- ✅ Cek status domain secara real-time menggunakan API Skiddle-ID
- 📋 Kelola daftar domain yang dipantau (maksimal 10 domain per user)
- 🔄 Update otomatis setiap 30 menit
- 🚨 Notifikasi jika status domain berubah
- 🟢 Status hijau untuk domain yang tidak diblokir
- 🔴 Status merah untuk domain yang diblokir

## Perintah Bot

- `/start` - Mulai menggunakan bot
- `/help` - Tampilkan bantuan
- `/add <domain>` - Tambah domain untuk dipantau
- `/list` - Lihat semua domain yang dipantau
- `/remove <domain>` - Hapus domain dari pantauan
- `/check <domain>` - Cek status domain secara manual

## Setup dan Instalasi

### 1. Buat Bot Telegram

1. Buka Telegram dan cari @BotFather
2. Kirim perintah `/newbot`
3. Ikuti instruksi untuk membuat bot baru
4. Salin token bot yang diberikan

### 2. Setup Environment

```bash
# Clone atau download project ini
cd telegram-domain-checker

# Aktifkan virtual environment
source venv/bin/activate

# Set bot token sebagai environment variable
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
```

### 3. Jalankan Bot

```bash
# Menggunakan script yang disediakan
./start_bot.sh

# Atau jalankan langsung
python src/main.py
```

## Struktur Project

```
telegram-domain-checker/
├── src/
│   ├── main.py              # Entry point aplikasi
│   ├── telegram_bot.py      # Implementasi bot Telegram
│   ├── models/
│   │   └── domain.py        # Model database untuk domain
│   └── database/
│       └── app.db           # Database SQLite
├── venv/                    # Virtual environment
├── requirements.txt         # Dependencies Python
├── start_bot.sh            # Script untuk menjalankan bot
└── README.md               # Dokumentasi ini
```

## Cara Kerja

1. **Pengecekan Domain**: Bot menggunakan API dari Skiddle-ID (https://check.skiddle.id/) untuk mengecek status pemblokiran domain
2. **Penyimpanan Data**: Domain yang dipantau disimpan dalam database SQLite dengan informasi user, status, dan waktu pengecekan terakhir
3. **Scheduler**: Sistem menggunakan library `schedule` untuk menjalankan pengecekan otomatis setiap 30 menit
4. **Notifikasi**: Jika status domain berubah, bot akan mengirim notifikasi ke user yang memantau domain tersebut

## API yang Digunakan

Bot ini menggunakan API tidak resmi dari Skiddle-ID untuk mengecek status pemblokiran domain:
- Endpoint: `https://check.skiddle.id/?domain=<domain>&json=true`
- Response: `{"domain.com": {"blocked": true/false}}`

## Batasan

- Maksimal 10 domain per user
- Pengecekan otomatis setiap 30 menit
- Bergantung pada ketersediaan API Skiddle-ID
- Database SQLite (cocok untuk penggunaan kecil hingga menengah)

## Deployment

Untuk deployment production, Anda dapat:

1. **Deploy ke VPS/Server**:
   - Upload project ke server
   - Install dependencies
   - Set environment variable
   - Jalankan dengan process manager seperti PM2 atau systemd

2. **Deploy ke Cloud Platform**:
   - Heroku, Railway, atau platform cloud lainnya
   - Set environment variable di dashboard platform
   - Deploy menggunakan Git atau Docker

## Troubleshooting

### Bot tidak merespons
- Pastikan token bot sudah benar
- Cek koneksi internet
- Lihat log error di console

### Pengecekan domain gagal
- Cek apakah API Skiddle-ID masih aktif
- Pastikan format domain benar (contoh: google.com)
- Cek log error untuk detail masalah

### Database error
- Pastikan folder `src/database/` ada dan writable
- Restart bot untuk membuat ulang database jika perlu

## Kontribusi

Silakan buat issue atau pull request jika Anda menemukan bug atau ingin menambah fitur.

## Lisensi

Project ini menggunakan lisensi MIT.

