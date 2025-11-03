import React, { useState, useEffect } from "react";
import { FileText, Receipt, BarChart3 } from "lucide-react";
import DocumentTypeCard from "./components/DocumentTypeCard";
import DocumentGenerator from "./components/DocumentGenerator";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

export default function App() {
  const [selectedType, setSelectedType] = useState(null);
  const handleHomeClick = () => setSelectedType(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [selectedType]);

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-background to-muted text-foreground transition-colors duration-500 overflow-x-hidden">
      {/* Halo lumineux */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-accent/20 rounded-full blur-3xl pointer-events-none"></div>

      {/* Navbar */}
      <Navbar onHomeClick={handleHomeClick} />

      {/* Contenu principal */}
      <main className="flex-1 flex items-center justify-center px-6 pt-32 pb-12">
        {!selectedType ? (
          <div className="text-center fade-in w-full max-w-6xl">
            {/* Titre */}
            <div className="space-y-3 mb-14">
              <h1 className="relative text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent leading-tight">
                Générateur de Documents IA
                <span className="absolute inset-0 blur-3xl bg-gradient-to-r from-primary/20 to-accent/20 opacity-30"></span>
              </h1>
              <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Transformez vos idées en documents structurés, modernes et
                professionnels en quelques secondes.
              </p>
            </div>

            {/* Cartes */}
            <div className="grid sm:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <DocumentTypeCard
                icon={FileText}
                title="CV"
                description="Créez un CV professionnel à partir de votre parcours"
                onClick={() => setSelectedType("cv")}
              />
              <DocumentTypeCard
                icon={Receipt}
                title="Facture"
                description="Générez des factures détaillées et conformes"
                onClick={() => setSelectedType("invoice")}
              />
              <DocumentTypeCard
                icon={BarChart3}
                title="Rapport"
                description="Structurez vos rapports d’analyse et de synthèse"
                onClick={() => setSelectedType("report")}
              />
            </div>
          </div>
        ) : (
          <DocumentGenerator
            documentType={selectedType}
            onBack={() => setSelectedType(null)}
          />
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
