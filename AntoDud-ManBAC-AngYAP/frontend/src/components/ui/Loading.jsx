/**
 * Composant Loading réutilisable
 * Respecte le principe SRP - responsable uniquement de l'affichage des états de chargement
 */

import { Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

const Loading = ({ 
  size = 'md', 
  text = null,
  fullScreen = false,
  className = '' 
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };
  
  const content = (
    <div className={clsx('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={clsx('animate-spin text-blue-400', sizes[size])} />
      {text && (
        <p className="text-white/70 text-sm animate-pulse">{text}</p>
      )}
    </div>
  );
  
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }
  
  return content;
};

export default Loading;
