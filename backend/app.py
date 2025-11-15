from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modules.psd_reader import analyze_psd
from modules.text_detector import detect_text   # ← додаємо
from modules.psd_bottom_preview import export_bottom_layer_png
import cv2
import numpy as np

app = FastAPI(title="TypeHelper BubbleServer", version="0.0.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "file://", "http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PSDRequest(BaseModel):
    file_path: str

class ImageRequest(BaseModel):
    file_path: str

@app.get("/health")
def health():
    return {"ok": True, "version": app.version, "status": "running"}


# -------------------------------
# 🔹 PSD ANALYZE
# -------------------------------
@app.post("/analyze-psd")
def analyze(req: PSDRequest):
    try:
        data = analyze_psd(req.file_path)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


# -------------------------------
# 🔹 DETECT TEXT (PNG/JPG/PSD PREVIEW)
# -------------------------------
@app.post("/detect-text")
def detect_text_api(req: ImageRequest):
    try:
        path = req.file_path

        # Якщо PSD — конвертуємо лише нижній шар
        if path.lower().endswith(".psd"):
            path = export_bottom_layer_png(path)

        img = cv2.imread(path)
        if img is None:
            return {
                "success": False,
                "error": f"Cannot read image: {path}"
            }

        blocks = detect_text(img)

        result = []
        for b in blocks:
            result.append({
                "id": b.id,
                "bbox": list(b.bbox),
                "center": list(b.center),
                "mser_count": b.mser_count,
                "type": b.type,
                "confidence": b.confidence,
            })

        return {"success": True, "text_blocks": result}

    except Exception as e:
        return {"success": False, "error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=10854)

