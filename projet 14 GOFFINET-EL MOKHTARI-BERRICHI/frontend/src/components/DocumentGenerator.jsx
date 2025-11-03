import React, { useState } from "react";
import axios from "axios";
import { ArrowLeft, Loader2, Upload, Download, Rocket, CheckCircle2 } from "lucide-react";

export default function DocumentGenerator({ documentType, onBack }) {
  const [prompt, setPrompt] = useState("");
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPdfUrl(null);

    try {
      let res;
      if (documentType === "cv") {
        const formData = new FormData();
        formData.append("prompt", prompt);
        if (photo) formData.append("photo", photo);
        res = await axios.post(
          `http://127.0.0.1:8000/api/semantic/${documentType}`,
          formData,
          { responseType: "blob" }
        );
      } else {
        res = await axios.post(
          `http://127.0.0.1:8000/api/semantic/${documentType}`,
          { prompt },
          { responseType: "blob" }
        );
      }

      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error("Erreur Axios :", err);
      alert("❌ Erreur lors de la génération du document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-[calc(100vh-6rem)] px-6 pt-24 pb-8 bg-background text-foreground">
      {/* Bouton retour */}
      <button
        onClick={onBack}
        className="group self-start mb-8 flex items-center gap-2 px-4 py-2 rounded-lg 
             text-muted-foreground hover:text-foreground 
             hover:bg-accent/10 dark:hover:bg-accent/20 
             transition-all duration-300 shadow-sm"
      >
        <ArrowLeft
          size={18}
          className="transition-transform duration-300 group-hover:-translate-x-1"
        />
        Retour
      </button>

      {/* Carte principale */}
      <div className="w-full max-w-3xl bg-card shadow-xl border border-border rounded-2xl p-10 space-y-6">
        <div className="space-y-3 text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Générateur de {documentType.toUpperCase()}
          </h1>
          <p className="text-muted-foreground text-base">
            Décrivez votre contenu en langage naturel et laissez l’IA structurer
            votre document.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <textarea
            className="w-full p-4 rounded-xl border border-input bg-muted/30 text-foreground 
             focus:ring-4 focus:ring-primary/50 focus:border-primary outline-none 
             min-h-[180px] resize-none transition placeholder:text-muted-foreground"
            placeholder={
              documentType === "cv"
                ? `Décrivez votre profil ici…\nExemple : Je m'appelle John Doe, j'ai 30 ans et je suis développeur web avec 5 ans d'expérience dans le développement front-end et back-end…`
                : documentType === "invoice"
                ? `Décrivez les éléments de votre facture…\nExemple : Voici la facture concernant la prestation réalisée pour la société X le 15 mars 2025, incluant les services suivants…`
                : `Décrivez le contenu de votre rapport…\nExemple : Rédige un rapport technique sur les performances du système XYZ, incluant une analyse des données collectées entre janvier et mars 2025…`
            }
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            required
          />

          {/* Upload photo */}
          {documentType === "cv" && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-muted-foreground">
                Photo de profil (optionnelle)
              </label>
              <label className="flex items-center gap-2 px-4 py-2 border border-accent bg-accent/10 hover:bg-accent/20 rounded-lg cursor-pointer w-fit transition">
                <Upload size={18} className="text-accent" />
                <span className="text-accent font-medium text-sm">
                  Choisir un fichier
                </span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setPhoto(e.target.files[0])}
                  className="hidden"
                />
              </label>
              {photo && (
                <img
                  src={URL.createObjectURL(photo)}
                  alt="Aperçu"
                  className="w-20 h-20 rounded-full object-cover border shadow"
                />
              )}
            </div>
          )}

          {/* Bouton générer */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-lg text-white font-semibold bg-gradient-to-r from-primary to-accent hover:opacity-90 transition flex items-center justify-center gap-2 shadow-lg"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin w-5 h-5" /> Génération en
                cours...
              </>
            ) : (
              <>
                <Rocket className="w-5 h-5" /> Générer le document
              </>
            )}
          </button>
        </form>
      </div>

      {/* Bloc PDF généré */}
      {pdfUrl && (
        <div className="mt-10 w-full max-w-3xl bg-card border border-border shadow-lg rounded-2xl p-8 text-center space-y-3 fade-in">
          <div className="flex flex-col items-center gap-2">
            <CheckCircle2 className="w-10 h-10 text-green-500 animate-bounce" />
            <p className="text-foreground font-medium text-lg">
              Document généré avec succès !
            </p>
          </div>
          <a
            href={pdfUrl}
            download
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-accent text-white rounded-lg font-semibold shadow hover:opacity-90 transition"
          >
            <Download size={18} /> Télécharger le PDF
          </a>
        </div>
      )}
    </div>
  );
}
