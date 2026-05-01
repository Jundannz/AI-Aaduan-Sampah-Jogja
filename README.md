---
title: AI Aduan Sampah Jogja
emoji: ♻️
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---

# Sistem Klasifikasi Otomatis Laporan Pengaduan Sampah Wilayah Yogyakarta
**Live API (Hugging Face Spaces):** [Buka Dokumentasi Swagger UI](https://jundannz-ai-aduan-sampah-jogja.hf.space)

Proyek ini merupakan sistem backend berbasis kecerdasan buatan yang dirancang untuk mengolah laporan pengaduan warga terkait masalah kebersihan dan sampah di wilayah Yogyakarta. Sistem menggunakan pendekatan pemrosesan bahasa alami (Natural Language Processing) untuk menentukan prioritas penanganan dan kategori kasus secara otomatis melalui API.

## Latar Belakang
Laporan warga yang masuk dalam volume besar membutuhkan proses triase yang cepat. Sistem ini mengintegrasikan dua model pembelajaran mendalam untuk membantu pihak pengelola melakukan verifikasi laporan tanpa perlu melakukan klasifikasi manual satu per satu.

## Arsitektur Model
Sistem ini menggunakan dua mesin inferensi yang berjalan secara paralel dalam satu endpoint API:

1. Klasifikasi Prioritas (IndoBERT):
Menggunakan model IndoBERT base-p1 yang telah melalui tahap fine tuning menggunakan dataset laporan lokal. Model ini mengklasifikasikan teks ke dalam empat label: Rendah, Sedang, Tinggi, dan Unknown.

2. Klasifikasi Kategori Kasus (Zero Shot Classification):
Menggunakan model mDeBERTa-v3-base-mnli-xnli. Pendekatan ini memungkinkan sistem mendeteksi berbagai kategori kasus (seperti Tumpukan Sampah Liar, Limbah B3, atau Kerusakan Fasilitas) tanpa memerlukan data pelatihan spesifik untuk label tersebut.

## Spesifikasi Teknologi
* Framework API: FastAPI
* Library Deep Learning: PyTorch dan Transformers (Hugging Face)
* Server ASGI: Uvicorn
* Containerization: Docker
* Platform Deployment: Hugging Face Spaces

## Struktur Direktori
* main.py: Logika utama API dan pemuatan model ke dalam memori.
* requirements.txt: Daftar dependensi library Python.
* Dockerfile: Instruksi konfigurasi container untuk deployment server.
* models/: Direktori penyimpanan file biner model IndoBERT (lokal).
* README.md: Dokumentasi teknis proyek.

## Instruksi Penggunaan Lokal

1. Pastikan folder models sudah berisi file config.json dan pytorch_model.bin.
2. Pasang semua dependensi yang diperlukan:
   pip install -r requirements.txt
3. Jalankan server melalui terminal:
   uvicorn main:app --reload
4. Akses dokumentasi interaktif (Swagger UI) pada alamat: http://localhost:8000/docs

## Dokumentasi API

Endpoint: /predict
Metode: POST
Format Request:
{
  "teks": "tolong di bersihkan sampah menumpuk jalan bau gak enak bgt sangat mengganggu"
}

Format Response:
{
  "status": "sukses",
  "input_asli": "tolong di bersihkan sampah menumpuk jalan bau gak enak bgt sangat mengganggu",
  "input_bersih": "tolong di bersihkan sampah menumpuk jalan bau gak enak bgt sangat mengganggu",
  "hasil_prediksi": {
    "prioritas": {
      "label": "Tinggi",
      "confidence": 0.8512,
      "detail_skor": {
        "Rendah": 0.002,
        "Sedang": 0.1461,
        "Tinggi": 0.8512,
        "Unknown": 0.0007
      }
    },
    "kasus": {
      "kategori": "Tumpukan Sampah",
      "confidence": 0.9832
    }
  }
}

## Informasi Deployment
Sistem ini di-deploy menggunakan infrastruktur Docker pada Hugging Face Spaces. Karena ukuran file model biner yang besar, repositori GitHub ini hanya menyimpan kode sumber utama. File model dikelola secara terpisah pada lingkungan produksi untuk efisiensi penyimpanan Git.

Link API Aktif: https://jundannz-ai-aduan-sampah-jogja.hf.space

## Pengembang
Jundan Saiful Haq 