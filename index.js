// ================================
// 🧩 TypeHelper — index.js (оновлено)
// ================================


// Лог для перевірки підключення скрипта
console.log("📦 index.js завантажено");

const resultEl = document.getElementById("result");

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM готовий, ініціалізація UI...");
  initUI();

  const healthBtn = document.getElementById("healthBtn");
  const analyzeBtn = document.getElementById("analyzeBtn");

  if (!healthBtn || !analyzeBtn || !resultEl) {
    console.error("❌ Не знайдено один або кілька елементів UI");
    return;
  }

  console.log("🎯 Кнопки знайдено, додаємо слухачі подій...");

  // ----------------------------------------
  // 🔹 Перевірка з'єднання
  // ----------------------------------------
  healthBtn.addEventListener("click", async () => {
    console.log("💡 Клік по healthBtn");
    try {
      const res = await checkHealth();
      resultEl.textContent = res;
    } catch (err) {
      console.error("❌ Помилка при перевірці з'єднання:", err);
      resultEl.textContent = "❌ Помилка при перевірці зв’язку з сервером.";
    }
  });

  // ----------------------------------------
  // 🔹 Аналіз PSD
  // ----------------------------------------
  analyzeBtn.addEventListener("click", async () => {
    console.log("💡 Клік по analyzeBtn");

    const { storage } = require("uxp");
    const { localFileSystem } = storage;
    const psApp = require("photoshop").app;

    let filePath = null;

    try {
      // 1️⃣ Якщо є активний документ у Photoshop
      if (psApp?.activeDocument) {
        try {
          const doc = psApp.activeDocument;

          if (doc.fullName) {
            filePath =
              doc.fullName.nativePath || // основний варіант
              doc.fullName.fsName || // запасний
              null;
          }

          if (filePath) {
            console.log("📄 Активний документ PSD:", filePath);
          } else {
            console.warn("⚠️ fullName недоступне — документ не збережено");
          }
        } catch (docErr) {
          console.warn("⚠️ Помилка при доступі до документа:", docErr);
        }
      }

      // 2️⃣ Якщо активного або збереженого нема — fallback на вибір теки
      // 2️⃣ Якщо активного або збереженого нема — fallback на вибір PSD-файлу
      if (!filePath) {
        console.log("📁 Активного документа нема — вибір PSD вручну...");
        try {
          const psdFile = await localFileSystem.getFileForOpening({
            types: ["psd"],
          });

          if (!psdFile) {
            resultEl.textContent = "🚫 Файл не вибрано.";
            return;
          }

          filePath = psdFile.nativePath;
          console.log("📄 Обраний PSD:", filePath);
        } catch (fileErr) {
          console.error("❌ Помилка при виборі PSD:", fileErr);
          resultEl.textContent =
            "❌ Не вдалося відкрити файловий провідник або доступ заборонено.";
          return;
        }
      }

      // 3️⃣ Надсилаємо шлях до бекенду
      if (filePath) {
        const res = await analyzePSD(filePath);
        resultEl.textContent = res;
      } else {
        resultEl.textContent =
          "🚫 Не вдалося визначити шлях до PSD. Відкрий файл у Photoshop.";
      }
    } catch (err) {
      console.error("❌ Помилка при аналізі PSD:", err);
      resultEl.textContent = "❌ Не вдалося проаналізувати PSD.";
    }
  });

  console.log("🚀 Слухачі подій успішно ініціалізовано");
});


// ----------------------------------------
// 🔹 Детекція тексту + DEBUG LAYERS
// ----------------------------------------
const textBtn = document.getElementById("textBtn");

if (textBtn) {
  textBtn.addEventListener("click", async () => {
    console.log("💡 Клік по textBtn");

    const { storage } = require("uxp");
    const { localFileSystem } = storage;
    const psApp = require("photoshop").app;

    let filePath = null;

    try {
      // 1️⃣ Якщо відкрито документ у Photoshop
      if (psApp?.activeDocument) {
        try {
          const doc = psApp.activeDocument;
          if (doc.fullName) {
            filePath =
              doc.fullName.nativePath ||
              doc.fullName.fsName ||
              null;
          }
          if (filePath) {
            console.log("📄 Активний документ:", filePath);
          }
        } catch (docErr) {
          console.warn("⚠️ fullName недоступне:", docErr);
        }
      }

      // 2️⃣ Якщо нема збереженого документа — обираємо вручну
      if (!filePath) {
        console.log("📁 Активного документа нема — вибір файлу вручну...");
        const file = await localFileSystem.getFileForOpening({
          types: ["psd", "png", "jpg", "jpeg"],
        });

        if (!file) {
          resultEl.textContent = "🚫 Файл не вибрано.";
          return;
        }

        filePath = file.nativePath;
        console.log("📄 Обраний файл:", filePath);
      }

      // 3️⃣ Виклик RAW JSON API
      const apiResult = await detectTextRaw(filePath);

      if (!apiResult.success) {
        console.error("❌ Backend error:", apiResult.error);
        resultEl.textContent = "❌ " + apiResult.error;
        return;
      }

      const blocks = apiResult.text_blocks || [];
      console.log("🔎 Детектовано блоків:", blocks.length);

      // 4️⃣ Створюємо debug-шари у Photoshop
      await createDebugTextLayers(blocks);

      // 5️⃣ Виводимо результат у панель для користувача
      resultEl.textContent =
        `✔️ Створено ${blocks.length} debug-шарів у Photoshop`;

    } catch (err) {
      console.error("❌ Помилка при детекції тексту:", err);
      resultEl.textContent = "❌ Не вдалося виконати детекцію тексту.";
    }
  });
}

