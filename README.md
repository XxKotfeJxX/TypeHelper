# 🧩 TypeHelper

### Intelligent Speech-Bubble & Typography Assistant for Adobe Photoshop

---

## 🌟 Overview
**TypeHelper** — це розширення для Photoshop, яке автоматично аналізує комікс-/манґа-файли (`.psd`) і допомагає розміщувати текст у баблах:

- 🔍 Автоматичне визначення меж і типу баблів  
- 🧠 Підбір шрифту та розміру  
- 🪄 Компонування тексту всередині баблу  
- ✍️ Ручний режим редагування  
- 💾 Автозбереження та метадані в PSD  

---

## 🏗️ Architecture
TypeHelper складається з двох частин:

1. **UXP-панель** у Photoshop  
   - UI на HTML / JS / Spectrum UI  
   - Використовує `batchPlay` для керування шарами  
   - Підключається до локального сервера через `http://localhost:10854`

2. **BubbleServer (Python FastAPI)**  
   - Аналізує PSD-файли (`psd_tools`, OpenCV, Pillow)  
   - Розпізнає текст (OCR ja/ko/en)  
   - Обчислює оптимальне компонування  
   - Повертає JSON-результат панелі

Докладніше див. у [docs/architecture.md](docs/architecture.md).

---

## 🧭 Roadmap
| Phase | Version |                    Description                   |
|:-----:|:-------:|:------------------------------------------------:|
|   0   |  0.0.1  | Project specification (архітектура, формати, UX) |
|   1   |  1.0.0  | Core skeleton – зв’язок UXP ↔ Python             |
|   2   |    –    | PSD аналіз (межі, контури, типи)                 |
|   3   |    –    | OCR + класифікація типів баблів                  |
|   4   |    –    | Компонування тексту + реліз v1.0.0               |
|  5–6  |    –    | Ручний режим + збереження → v2.0.0               |
|  7 +  |    –    | UI / ML / релізи далі                            |

---

## ⚙️ Installation (після релізу)
1. Завантаж `.ccx` з [Releases](https://github.com/xxkotfejxx/TypeHelper/releases).  
2. Встанови через Adobe Creative Cloud Installer.  
3. У Photoshop: **Вікно → Розширення → TypeHelper**.  

---

## 📜 License
MIT License © 2025 XxKotofeJxX
