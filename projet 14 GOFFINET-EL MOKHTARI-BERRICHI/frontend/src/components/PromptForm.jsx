import React, { useState } from 'react'
import axios from 'axios'

export default function PromptForm({ setPdfUrl, setLoading }) {
  const [prompt, setPrompt] = useState('')
  const [docType, setDocType] = useState('cv')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setPdfUrl(null)

    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/api/semantic/${docType}`,
        { prompt },
        { responseType: 'blob' }
      )

      const blob = new Blob([res.data], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      setPdfUrl(url)
    } catch (err) {
      alert('❌ Erreur : ' + (err.response?.data?.detail || 'Erreur de génération'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-2xl">
      <label className="block mb-2 font-semibold text-gray-700">🧠 Entrez votre prompt :</label>
      <textarea
        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400"
        rows={5}
        placeholder="Ex: Rédige un rapport technique sur le projet IMSA Forever Shop..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        required
      />

      <div className="flex justify-between items-center mt-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">📄 Type de document :</label>
          <select
            className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-400"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            <option value="cv">CV</option>
            <option value="invoice">Invoice</option>
            <option value="report">Report</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={setLoading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2 rounded-lg shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          {setLoading ? '⏳ Génération...' : '🚀 Générer'}
        </button>
      </div>
    </form>
  )
}