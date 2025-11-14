from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modules.psd_reader import analyze_psd

app = FastAPI(title="TypeHelper BubbleServer", version="0.0.2")

# ----------------------------------------
# 🔹 CORS для UXP-панелі (дуже важливо!)
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "file://", 
        "http://localhost",
        "http://127.0.0.1",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# 🔹 Модель запиту
# --------------------------
class PSDRequest(BaseModel):
    file_path: str

# --------------------------
# 🔹 Перевірка
# --------------------------
@app.get("/health")
def health():
    return {"ok": True, "version": app.version, "status": "running"}

# --------------------------
# 🔹 Аналіз PSD
# --------------------------
@app.post("/analyze-psd")
def analyze(req: PSDRequest):
    print("📨 analyze-psd called with:", req.file_path)
    try:
        data = analyze_psd(req.file_path)
        print("✅ PSD analyzed successfully")
        return {"success": True, "data": data}
    except Exception as e:
        print("❌ PSD analysis failed:", e)
        return {"success": False, "error": str(e)}

# --------------------------
# 🔹 Запуск сервера
# --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10854)
