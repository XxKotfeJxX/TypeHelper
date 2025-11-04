# 🧠 Architecture — TypeHelper

## Components
- **UXP Panel (Photoshop)**
  - HTML / JS / Spectrum UI
  - Використовує `batchPlay` для керування шарами
  - Надсилає HTTP-/WebSocket-запити на локальний сервер

- **BubbleServer (Python FastAPI)**
  - Обробляє запити:
    - `/health`
    - `/analyze-psd`
    - `/layout`
    - `/suggest-fonts`
    - `/save`
  - Модулі: `psd_reader`, `analyzer`, `ocr_engine`, `layout_engine`, `fonts`

- **Storage**
  - Sidecar JSON (`page.psd.bubbles.json`)
  - PSD-група `__BubbleMeta__` із метаданими

## Data Model — Bubble
```jsonc
{
  "id": "bubble_0001",
  "bbox": {"x":1420,"y":980,"w":640,"h":410},
  "type": "speech",
  "textOriginal": {"lang":"ja","value":"……！"},
  "textComposed": {"lang":"ru","variants":[]},
  "flags": {"manualOverride": false}
}
