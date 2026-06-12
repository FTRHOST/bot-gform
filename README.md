# 🤖 Google Forms Bot - Quantum Respondent

Bot otomatis untuk mengisi kuesioner Google Forms dengan identitas yang sangat realistis dan pola jawaban yang terlihat manusiawi (menggunakan konsep probabilitas "Quantum Uncertainty").

## 🌟 Fitur Utama

- **Generator Nama Unik**: Membuat ribuan kombinasi nama asli Indonesia (pria/wanita).
- **Sinkronisasi Gender**: Otomatis memilih jenis kelamin berdasarkan nama depan.
- **Quantum Uncertainty**: Jawaban kuesioner tidak acak buta, tapi mengikuti distribusi bobot (misal: mayoritas 'Setuju') agar data riset terlihat organik.
- **Multi-Page Support**: Mampu melewati halaman identitas, mengisi teks, dan lanjut ke halaman kuesioner.
- **Multi-Threading**: Bisa menjalankan beberapa browser sekaligus untuk mempercepat proses.

---

## 🚀 Panduan Penggunaan (Untuk Pemula)

### Langkah 1: Membuat Google Form Otomatis

Sebelum menjalankan bot, Anda bisa membuat formulir yang identik menggunakan script yang sudah disediakan.

1. Buka [Google Forms](https://forms.google.com/).
2. Buat formulir kosong baru.
3. Klik ikon titik tiga (⋮) di pojok kanan atas, lalu pilih **Script Editor**.
4. Hapus semua kode yang ada di sana, lalu salin dan tempel isi dari file `create_form_fixed.js`.
5. Klik tombol **Run** (Jalankan).
6. Google akan meminta izin, klik **Allow** (Izinkan).
7. Cek [Google Drive](https://drive.google.com/) Anda, formulir baru berjudul "Salinan Kuesioner Pondok Pesantren..." telah berhasil dibuat.
8. Buka formulir tersebut, klik tombol **Send** (Kirim), lalu ambil **Link Preview**-nya.

### Langkah 2: Persiapan Lingkungan (Python)

Pastikan Anda sudah menginstal Python di komputer Anda.

1. **Clone/Download** repositori ini.
2. Buka terminal atau Command Prompt di folder projek.
3. Buat virtual environment (opsional tapi disarankan):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Untuk Linux/Mac
   .venv\Scripts\activate     # Untuk Windows
   ```

4. Instal library yang dibutuhkan:

   ```bash
   pip install selenium flask
   ```

5. Pastikan Anda memiliki browser **Firefox** terinstal.

### Langkah 3: Konfigurasi Bot

Buka file `main.py` menggunakan text editor (Notepad++, VS Code, dll) dan sesuaikan bagian ini:

```python
# Ganti dengan link Google Form Anda
LINK = 'https://docs.google.com/forms/d/e/PASTE_YOUR_LINK_HERE/viewform'

# Tentukan jumlah responden yang diinginkan
RESPONSE_COUNT = 30

# Jumlah browser yang berjalan bersamaan (sesuaikan dengan RAM komputer)
THREADS_MAX = 3
```

Anda juga bisa mengatur "Quantum Uncertainty" (bobot jawaban) di bagian:

```python
# [Sangat Tidak Setuju, Tidak Setuju, Netral, Setuju, Sangat Setuju]
LIKERT_WEIGHTS = [2, 8, 25, 40, 25]
```

_Artinya: Peluang menjawab 'Setuju' adalah 40%, sedangkan 'Sangat Tidak Setuju' hanya 2%._

### Langkah 4: Menjalankan Bot

Kembali ke terminal, lalu ketik:

```bash
python main.py
```

Bot akan mulai bekerja. Anda akan melihat log di terminal seperti:

- `Resp 1 - Memulai sesi: Ahmad Saputra (Salatiga)`
- `Resp 1 - Mengisi Halaman 1 (10 pertanyaan)`
- `Resp 1 - FORM BERHASIL DISUBMIT!`

---

## ⚠️ Catatan Penting

- **Headless Mode**: Secara default bot berjalan di latar belakang (tanpa memunculkan jendela browser). Jika ingin melihat prosesnya, hapus/beri komentar pada baris `firefox_options.add_argument("--headless")` di `main.py`.
- **Keamanan**: Gunakan bot ini dengan bijak untuk tujuan edukasi atau pengujian sistem. Jangan gunakan untuk manipulasi data yang merugikan pihak lain.

## 🛠️ Teknologi

- **Python 3**
- **Selenium WebDriver**
- **Google Apps Script** (untuk pembuatan form)
- **Firefox Engine** (Geckodriver)
