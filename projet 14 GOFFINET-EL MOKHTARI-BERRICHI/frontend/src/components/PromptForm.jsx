import React, { useState } from "react";
import axios from "axios";

export default function PromptForm({ setPdfUrl, loading, setLoading }) {
  const [prompt, setPrompt] = useState("");
  const [docType, setDocType] = useState("cv");
  const [photo, setPhoto] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPdfUrl(null);

    try {
      let res;

      if (docType === "cv") {
        // 📸 Envoi multipart/form-data (CV avec photo)
        const formData = new FormData();
        formData.append("prompt", prompt);
        if (photo) formData.append("photo", photo);

        console.log("📤 [DEBUG FRONT] Type:", docType);
        console.log("📤 [DEBUG FRONT] FormData envoyé:", prompt, photo?.name);

        res = await axios.post(
          `http://127.0.0.1:8000/api/semantic/${docType}`,
          formData,
          { responseType: "blob" }
        );
      } else {
        // 🧾 Envoi JSON simple pour report / invoice
        console.log("📤 [DEBUG FRONT] Type:", docType);
        console.log("📤 [DEBUG FRONT] Payload envoyé:", JSON.stringify({ prompt }));
      
        // ⚠️ Forcer la sérialisation JSON (important pour éviter un body vide)
        const body = JSON.stringify({ prompt });
      
        res = await axios.post(
          `http://127.0.0.1:8000/api/semantic/${docType}`,
          body, // ✅ corps JSON bien formé
          {
            headers: { "Content-Type": "application/json" },
            responseType: "blob",
          }
        );
      }

      // ✅ Génération du lien PDF
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error("❌ Erreur Axios :", err.response?.data || err.message);
      alert(
        "❌ Erreur : " + (err.response?.data?.detail || "Erreur de génération")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-2xl flex flex-col gap-4"
    >
      <label className="block font-semibold text-gray-700">
        🧠 Entrez votre prompt :
      </label>
      <textarea
        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400"
        rows={5}
        placeholder="Ex : Rédige une facture pour le client Thomas Dupont..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        required
      />

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          📄 Type de document :
        </label>
        <select
          className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-400 w-full"
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
        >
          <option value="cv">CV</option>
          <option value="report">Rapport</option>
          <option value="invoice">Facture</option>
        </select>
      </div>

      {docType === "cv" && (
        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700">
            📷 Photo de profil (optionnelle)
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setPhoto(e.target.files[0])}
            className="border p-2 rounded-md w-full"
          />
          {photo && (
            <div className="mt-3 flex justify-center">
              <img
                src={URL.createObjectURL(photo)}
                alt="Prévisualisation"
                className="w-24 h-24 object-cover rounded-full border shadow-md"
              />
            </div>
          )}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="bg-violet-600 hover:bg-violet-700 text-white font-semibold px-6 py-2 rounded-lg shadow-md disabled:opacity-50 flex items-center gap-2 justify-center"
      >
        {loading ? "⏳ Génération en cours..." : "🚀 Générer le document"}
      </button>
    </form>
  );
}
