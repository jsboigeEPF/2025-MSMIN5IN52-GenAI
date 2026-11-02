/**
 * Composant Card réutilisable
 * Respecte le principe SRP - responsable uniquement du rendu d'un conteneur stylisé
 */

import { clsx } from 'clsx';

const Card = ({
  children,
  variant = 'default',
  padding = 'md',
  className = '',
  ...props
}) => {
  const variants = {
    default: 'glass-effect',
    solid: 'bg-slate-800 border border-slate-700',
    transparent: 'bg-transparent',
    gradient: 'bg-gradient-to-br from-blue-900/30 to-purple-900/30 border border-white/10 backdrop-blur-sm',
  };
  
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  return (
    <div
      className={clsx(
        'rounded-xl shadow-lg',
        variants[variant],
        paddings[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
