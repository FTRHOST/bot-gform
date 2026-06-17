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

### Langkah 3: Konfigurasi Bot & Mode Pengisian

Buka file `main.py` menggunakan text editor (Notepad++, VS Code, dll) dan sesuaikan bagian tautan form:

```python
# Ganti dengan link Google Form Anda
LINK = 'https://docs.google.com/forms/d/e/PASTE_YOUR_LINK_HERE/viewform'
```

Bot ini memiliki **2 Mode Pengisian**:
1. **Mode Random (Acak)**: Mengisi form secara acak menggunakan data buatan yang realistis (sesuai daftar di dalam kode).
2. **Mode File (CSV / Excel)**: Mengisi form menggunakan data responden asli dari file `.csv` atau `.xlsx` / `.xls` (Excel).

#### Cara Memilih Mode saat Menjalankan Bot:
Anda dapat memilih mode pengisian dengan beberapa cara:
- **Input Interaktif**: Cukup ketik `python main.py` di terminal. Bot akan memunculkan menu interaktif untuk memilih mode dan memasukkan nama file data Anda.
- **Argumen Command Line**:
  - Untuk langsung menjalankan Mode Random:
    ```bash
    python main.py --random
    ```
  - Untuk langsung menjalankan Mode File:
    ```bash
    python main.py data_dummy.xlsx
    # atau
    python main.py data_dummy.csv
    ```

#### Format File CSV / Excel (Mode 2):
File data Anda dapat memiliki kolom-kolom berikut (tidak wajib diisi semua):
- **Nama Lengkap / Nama / Name**: Kolom nama responden.
- **Usia / Umur / Age**: Usia (misal: `20`).
- **Jenis Kelamin / Gender**: Pilihan gender (misal: `Pria` atau `Wanita`).
- **Fakultas / Prodi / Program Studi / Jurusan**: Fakultas dan prodi.
- **Semester**: Semester saat ini.
- **Asal Kota / Kabupaten / Kota**: Asal kota.
- **Jarak / Jarak Tempuh**: Jarak ke pesantren.
- **Uang Saku / Pengeluaran**: Uang saku per bulan.
- **Status / Status Saat Ini**: Status kepengurusan/santri biasa.
- **Lama Menyantri / Lama Tinggal**: Lama tinggal di pesantren.
- **Q1 s/d Q15 (atau P1 s/d P15 / Pertanyaan 1 s/d 15)**: Jawaban untuk kuesioner skala Likert 1-15. Anda dapat mengisi dengan angka `1` s/d `5` (atau teks pilihan seperti `Sangat Setuju`).

> [!TIP]
> **Fitur Fallback Pintar**: Jika ada baris data atau kolom kuesioner yang kosong (bernilai kosong/NaN) di file CSV/Excel Anda, bot akan otomatis mengisi bagian yang kosong tersebut menggunakan generator acak realistis (Quantum Uncertainty) agar proses pengisian form tidak terhenti.


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
