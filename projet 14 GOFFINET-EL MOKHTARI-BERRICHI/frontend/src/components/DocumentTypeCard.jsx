import React from "react";

export default function DocumentTypeCard({ icon: Icon, title, description, onClick }) {
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer p-8 rounded-2xl border border-border bg-card/70 
                 backdrop-blur-md shadow-lg hover:shadow-accent/40 transition-all 
                 hover:-translate-y-2 duration-300 hover:bg-accent/10"
    >
      <div className="flex flex-col items-center text-center space-y-4">
        <div className="p-4 rounded-full bg-accent/20 group-hover:bg-accent/30 transition">
          <Icon className="w-8 h-8 text-accent" />
        </div>
        <h3 className="text-xl font-semibold text-foreground">{title}</h3>
        <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
