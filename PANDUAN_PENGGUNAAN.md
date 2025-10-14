# Panduan Penggunaan Aplikasi "The Senticon"

## 1. Pendahuluan
The Senticon adalah alat cerdas yang dirancang untuk membantu Anda mengekstrak, menganalisis, dan meringkas artikel berita dari berbagai sumber online. Fungsi utamanya meliputi ekstraksi konten berita, analisis sentimen, deteksi nama jurnalis, dan pembuatan ringkasan otomatis.

---

## 2. Panduan Penggunaan (Step-by-Step)

Berikut adalah langkah-langkah untuk menggunakan aplikasi ini secara efektif.

### Langkah 1: Konfigurasi Analisis di Sidebar

Sebelum memproses data, atur terlebih dahulu fungsi analisis apa saja yang ingin Anda aktifkan melalui menu di sidebar kiri.

 <!-- Anda bisa menambahkan link gambar screenshot di sini -->

#### Penjelasan Detail Fungsi Konfigurasi:

- **📄 Tarik Full Teks Berita**
  - **Fungsi:** Mengambil seluruh isi teks dari artikel di URL yang diberikan. Ini adalah fungsi dasar yang diperlukan untuk analisis konten mendalam.
  - **Kapan Digunakan:** Aktifkan selalu jika Anda butuh ringkasan (summarize) atau analisis sentimen dari isi berita.

- **📅 Deteksi Tanggal Rilis**
  - **Fungsi:** Mencari dan mencatat tanggal publikasi artikel.
  - **Kapan Digunakan:** Aktifkan jika data tanggal rilis berita penting untuk analisis Anda.

- **😊 Analisis Sentimen**
  - **Fungsi:** Menganalisis sentimen (positif, negatif, netral) dari teks berita terhadap suatu topik.
  - **Penting:** Fungsi ini **wajib** diisi dengan **Konteks Sentimen**. Tanpa konteks, AI tidak tahu harus menganalisis sentimen terhadap apa.
  - **Contoh Konteks:** `Harga BBM`, `Produk Mobil Listrik`, `Kebijakan Pemerintah`.

- **👤 Deteksi Jurnalis**
  - **Fungsi:** Mencoba menemukan nama penulis/jurnalis dari artikel. Keberhasilannya bergantung pada format situs media.

- **📝 Summarize Artikel**
  - **Fungsi:** Membuat ringkasan otomatis dari konten artikel menggunakan AI. Opsi **"Tarik Full Teks Berita"** harus aktif agar fungsi ini berjalan.
  - **Opsi Lanjutan:**
    - **Tipe Ringkasan:** Pilih format (Ringkas, Detail, Poin-poin).
    - **Panjang Maksimal:** Atur batas jumlah kata pada ringkasan.
    - **Bahasa & Aspek Fokus:** Tentukan bahasa output dan topik spesifik yang ingin ditekankan dalam ringkasan.

- **🔧 Opsi Scraping (Timeout)**
  - **Fungsi:** Mengatur batas waktu tunggu (detik) saat mengambil data dari sebuah situs. Naikkan nilainya jika Anda sering gagal mengambil data dari situs yang lambat.

---

### Langkah 2: Input Data

Anda memiliki dua cara untuk memasukkan data berita:

#### Opsi 1: URL Manual
- Gunakan tab **"🔗 URL Manual"**.
- Masukkan satu URL per baris.
- **Format Khusus:** Anda bisa menambahkan judul manual untuk setiap URL dengan format `URL[tekan Tab]Judul Artikel`.
  - Contoh: `https://www.media.com/news1.html	Ini adalah judul manual saya`
- Pastikan mencentang **"Gunakan Judul dari Input Manual"** jika Anda menggunakan format di atas.

#### Opsi 2: Upload File Excel
- Gunakan tab **"📁 Upload File Excel"**.
- Unggah file `.xlsx` atau `.xls` Anda.
- **Penting:** Setelah mengunggah, lakukan **Mapping Kolom**. Pilih kolom mana di file Excel Anda yang berisi **URL** berita. Ini sangat penting agar aplikasi dapat membaca data dengan benar.

---

### Langkah 3: Memulai Proses Analisis
- Setelah konfigurasi dan input data selesai, klik tombol **"🚀 Mulai Analisis"**.
- Aplikasi akan mulai memproses setiap URL satu per satu. Anda dapat melihat progress bar di bawah tombol.

---

### Langkah 4: Memahami dan Mengekspor Hasil

Hasil analisis akan ditampilkan dalam tiga tab:

1.  **📊 Ringkasan & Metrik**
    - Menampilkan statistik ringkas dari proses yang berjalan, seperti jumlah data yang diproses dan tingkat keberhasilan scraping.

2.  **📋 Data Lengkap**
    - Menampilkan tabel pratinjau dari data hasil analisis. Anda bisa melihat beberapa baris pertama dari hasil untuk memastikan proses berjalan sesuai harapan.

3.  **📤 Export**
    - Di tab ini, Anda dapat mengunduh laporan lengkap hasil analisis.
    - Klik tombol **"📥 Download Laporan Excel"** untuk menyimpan semua data dalam format file Excel.

---

## 3. Tips dan Catatan Penting
- **Konteks Sentimen yang Efektif:** Gunakan konteks yang spesifik (contoh: `kinerja saham Telkom`) untuk mendapatkan hasil analisis sentimen yang lebih akurat daripada konteks yang terlalu umum (contoh: `saham`).
- **Hasil Scraping Gagal?:** Beberapa situs berita memiliki perlindungan yang kuat sehingga kontennya tidak bisa diambil secara otomatis. Jika sering terjadi, coba naikkan nilai **Timeout** di Opsi Scraping.
- **Ringkasan Terbaik:** Ringkasan akan lebih fokus dan relevan jika Anda mengisi bagian **"Aspek yang Difokuskan"** pada konfigurasi summarize.
