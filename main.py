import torch
import numpy as np
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Dictionary untuk menyimpan kedua model di memori
ml_models = {}

# PENTING: Sesuaikan dictionary ini dengan urutan label (id2label) 
# yang kamu gunakan saat proses training model kasus.
LABEL_KASUS = {
    0: "Tumpukan Sampah",
    1: "Jadwal Pengangkutan",
    2: "Sampah Berukuran Besar",
    3: "Fasilitas Rusak",
    4: "Limbah Berbahaya",
    5: "Administrasi",
    6: "Bukan Sampah",
}

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^\w\s.,!?;:\-'\"()/]", " ", text, flags=re.UNICODE)
    text = re.sub(r" {2,}", " ", text).strip()
    return text.lower()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Memuat model Prioritas...")
    # Update path ke dalam folder models
    ml_models["tokenizer_prioritas"] = AutoTokenizer.from_pretrained("./models/model_prioritas")
    ml_models["model_prioritas"] = AutoModelForSequenceClassification.from_pretrained("./models/model_prioritas")
    ml_models["model_prioritas"].eval()
    
    print("Memuat model Kasus...")
    # Update path ke dalam folder models, dan sesuaikan nama foldernya menjadi model_case
    ml_models["tokenizer_kasus"] = AutoTokenizer.from_pretrained("./models/model_case")
    ml_models["model_kasus"] = AutoModelForSequenceClassification.from_pretrained("./models/model_case")
    ml_models["model_kasus"].eval()
    
    print("Semua model siap digunakan!")
    yield
    print("Membersihkan memori...")
    ml_models.clear()

app = FastAPI(lifespan=lifespan, title="API Klasifikasi Laporan Sampah")

@app.get("/")
async def root():
    return {"message": "API Klasifikasi Laporan Sampah Aktif."}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LaporanRequest(BaseModel):
    teks: str

@app.post("/predict")
async def predict_priority(request: LaporanRequest):
    if not request.teks.strip():
        raise HTTPException(status_code=400, detail="Teks laporan tidak boleh kosong")
        
    teks_bersih = clean_text(request.teks)
    
    # --- 1. Prediksi Prioritas ---
    tok_prio = ml_models["tokenizer_prioritas"]
    mod_prio = ml_models["model_prioritas"]
    
    inputs_prio = tok_prio(teks_bersih, return_tensors="pt", truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs_prio = mod_prio(**inputs_prio)
        probs_prio = torch.softmax(outputs_prio.logits, dim=-1)[0].numpy()
        
    label_map_prio = {0: "Rendah", 1: "Sedang", 2: "Tinggi", 3: "Unknown"}
    pred_id_prio = int(np.argmax(probs_prio))
    prioritas_hasil = label_map_prio[pred_id_prio]
    prioritas_confidence = float(probs_prio[pred_id_prio])
    skor_detail_prioritas = {label_map_prio[i]: round(float(p), 4) for i, p in enumerate(probs_prio)}
    
    # --- 2. Prediksi Kategori Kasus (Menggunakan Model Baru) ---
    if prioritas_hasil == "Unknown":
        kasus_hasil = "Bukan Sampah"
        kasus_score = 1.0
    else:
        tok_kasus = ml_models["tokenizer_kasus"]
        mod_kasus = ml_models["model_kasus"]
        
        inputs_kasus = tok_kasus(teks_bersih, return_tensors="pt", truncation=True, max_length=128)
        
        with torch.no_grad():
            outputs_kasus = mod_kasus(**inputs_kasus)
            probs_kasus = torch.softmax(outputs_kasus.logits, dim=-1)[0].numpy()
            
        pred_id_kasus = int(np.argmax(probs_kasus))
        kasus_hasil = LABEL_KASUS.get(pred_id_kasus, "Lainnya")
        kasus_score = round(float(probs_kasus[pred_id_kasus]), 4)
    
    return {
        "status": "sukses",
        "input_asli": request.teks,
        "input_bersih": teks_bersih,
        "hasil_prediksi": {
            "prioritas": {
                "label": prioritas_hasil,
                "confidence": round(prioritas_confidence, 4),
                "detail_skor": skor_detail_prioritas
            },
            "kasus": {
                "kategori": kasus_hasil,
                "confidence": kasus_score
            }
        }
    }