# PDF Chat Assistant dengan Bootstrap dan Flask

> Chat dengan dokumen PDF Anda dengan antarmuka modern

## Cara Menggunakan

1. **Persiapan Lingkungan**
   ```
   pip install -r requirements.txt
   ```

2. **Siapkan API Key**
   Buat file `.env` dan tambahkan API key OpenAI Anda:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Jalankan Aplikasi**
   ```
   python server.py
   ```

4. **Buka Aplikasi di Browser**
   Buka `http://127.0.0.1:5000` di browser Anda

## Fitur Utama

- **Antarmuka Modern**: Dibangun dengan Bootstrap, tampilan menarik dan responsif
- **PDF Viewer**: Lihat dokumen PDF langsung di aplikasi
- **Chat dengan AI**: Tanyakan pertanyaan tentang konten dokumen
- **Split Screen**: Baca dokumen sambil berinteraksi dengan AI

## Cara Kerja

1. **Upload PDF**: User mengupload dokumen PDF
2. **Proses Dokumen**: Sistem mengekstrak teks dan membuat vector embeddings
3. **Tampilkan PDF**: Dokumen dibuka di PDF viewer
4. **Interaksi**: User dapat bertanya tentang isi dokumen dan mendapatkan jawaban relevan

## Teknologi yang Digunakan

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Flask (Python)
- **PDF Processing**: PyPDF2, PDF.js
- **AI & Natural Language Processing**: LangChain, OpenAI

## Keamanan

- Semua pemrosesan dokumen dilakukan di server lokal
- Dokumen tidak dikirim ke pihak ketiga kecuali untuk pemrosesan oleh OpenAI API
