// ================================
// 🧠 TypeHelper — api.js
// ================================

async function checkHealth() {
  try {
    const res = await fetch("http://localhost:10854/health");
    const data = await res.json();
    if (data.ok) {
      return `✅ Сервер працює (v${data.version})`;
    }
    return "⚠️ Сервер не відповідає.";
  } catch (err) {
    console.error("❌ checkHealth error:", err);
    return "❌ Помилка зв’язку із сервером.";
  }
}

async function analyzePSD(path) {
  try {
    const res = await fetch("http://localhost:10854/analyze-psd", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: path }),
    });

    const json = await res.json();
    const data = json.data || json;

    if (!data || !data.layers) {
      throw new Error("Некоректна відповідь сервера");
    }

    return (
      `📄 PSD: ${data.width}x${data.height}\n` +
      `🧩 ${data.layers.length} шарів\n` +
      data.layers
        .map((l) => `- ${l.name} (${l.visible ? "👁️" : "🚫"})`)
        .join("\n")
    );
  } catch (err) {
    console.error("❌ analyzePSD error:", err);
    return "❌ Не вдалося прочитати PSD.";
  }
}

// =====================================================
// 🔍 1) RAW JSON (для debug-шарів)
// =====================================================
async function detectTextRaw(path) {
  try {
    const res = await fetch("http://localhost:10854/detect-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: path }),
    });

    return await res.json();
  } catch (err) {
    console.error("❌ detectTextRaw error:", err);
    return { success: false, error: "Помилка зв’язку з сервером." };
  }
}

// =====================================================
// 🔍 2) Людська версія detect-text
// =====================================================
async function detectText(path) {
  const json = await detectTextRaw(path);

  if (!json.success) {
    return "❌ " + (json.error || "Помилка сервера");
  }

  const blocks = json.text_blocks || [];
  if (blocks.length === 0) return "⚠️ Текст не знайдено.";

  let out = `🔎 Знайдено ${blocks.length} текстових блоків:\n\n`;

  for (const b of blocks) {
    out +=
      `📝 Блок #${b.id}\n` +
      `   Тип: ${b.type} (${Math.round(b.confidence * 100)}%)\n` +
      `   bbox: [${b.bbox.join(", ")}]\n\n`;
  }

  return out;
}
