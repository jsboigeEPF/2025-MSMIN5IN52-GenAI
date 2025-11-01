import React from 'react'

export default function ResultDownload({ pdfUrl, loading }) {
  if (loading) {
    return (
      <p className="mt-8 text-indigo-600 font-medium flex items-center gap-2">
        ⏳ Génération du document en cours...
      </p>
    )
  }

  if (!pdfUrl) return null

  return (
    <div className="mt-8 text-center">
      <a
        href={pdfUrl}
        download
        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition-all"
      >
        📥 Télécharger le PDF
      </a>
    </div>
  )
}