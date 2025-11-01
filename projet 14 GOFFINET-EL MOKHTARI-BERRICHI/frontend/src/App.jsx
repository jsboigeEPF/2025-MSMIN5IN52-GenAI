import React, { useState } from 'react'
import Navbar from './components/Navbar'
import PromptForm from './components/PromptForm'
import ResultDownload from './components/ResultDownload'
import './styles.css'

export default function App() {
  const [pdfUrl, setPdfUrl] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 text-gray-800">
      <Navbar />

      <main className="flex flex-col items-center justify-center py-20 px-6">
        <h1 className="text-4xl font-bold mb-4 text-indigo-900 text-center">
          Semantic Document Generator ✨
        </h1>
        <p className="text-gray-600 mb-10 text-center max-w-xl">
          Générez automatiquement des documents structurés (CV, facture, rapport)
          à partir d’un prompt intelligent alimenté par Semantic Kernel.
        </p>

        <PromptForm
          setPdfUrl={setPdfUrl}
          setLoading={setLoading}
        />

        <ResultDownload pdfUrl={pdfUrl} loading={loading} />
      </main>

      <footer className="text-center text-sm text-gray-500 py-6 border-t">
        © 2025 EPF – Semantic Kernel Frontend
      </footer>
    </div>
  )
}