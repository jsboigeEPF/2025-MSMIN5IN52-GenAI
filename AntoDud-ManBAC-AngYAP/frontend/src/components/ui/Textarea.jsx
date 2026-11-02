/**
 * Composant Textarea réutilisable
 * Respecte le principe SRP - responsable uniquement du rendu d'une zone de texte multiligne
 */

import { clsx } from 'clsx';

const Textarea = ({
  value,
  onChange,
  placeholder = '',
  disabled = false,
  error = null,
  label = null,
  rows = 4,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-white/80 mb-2">
          {label}
        </label>
      )}
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        className={clsx(
          'w-full px-4 py-3 rounded-lg',
          'bg-white/10 border border-white/20',
          'text-white placeholder-white/40',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'transition-all duration-200',
          'resize-none scrollbar-thin',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
    </div>
  );
};

export default Textarea;
