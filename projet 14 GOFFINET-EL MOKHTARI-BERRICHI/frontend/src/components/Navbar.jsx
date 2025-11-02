import React from "react";
import ThemeToggle from "./ThemeToggle";

export default function Navbar({ onHomeClick }) {
  return (
    <nav className="fixed top-0 left-0 w-full z-50 backdrop-blur-2xl border-b border-border/40 
                    bg-gradient-to-r from-background/95 via-background/80 to-background/95 
                    shadow-lg transition-all duration-500">
      <div className="max-w-6xl mx-auto px-8 py-6 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={onHomeClick}
          className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent hover:opacity-80 transition"
        >
          SemanticGen
        </button>

        {/* Menu + Switch */}
        <div className="flex items-center gap-10">
          <a
            href="#home"
            onClick={onHomeClick}
            className="text-base text-muted-foreground hover:text-foreground transition-colors"
          >
            Accueil
          </a>
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}
