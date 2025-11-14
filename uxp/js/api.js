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
      body: JSON.stringify({ file_path: path })
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
