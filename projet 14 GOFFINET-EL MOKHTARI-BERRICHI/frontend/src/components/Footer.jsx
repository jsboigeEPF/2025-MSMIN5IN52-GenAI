import React from "react";
import { Github, Linkedin } from "lucide-react";

export default function Footer() {
  return (
    <footer className="mt-auto w-full py-6 border-t border-border/30 
                       bg-gradient-to-t from-background/95 via-background/90 to-transparent 
                       backdrop-blur-lg text-sm text-muted-foreground transition-all duration-500">
      <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center gap-3">
        <p>
          © 2025 <span className="font-semibold text-foreground">SemanticGen</span> — EPF Ingénierie Numérique
        </p>

        <div className="flex gap-4">
        </div>
      </div>
    </footer>
  );
}
