import React from 'react'

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md py-4 px-8 flex justify-between items-center fixed top-0 left-0 right-0 z-50">
      <h1 className="text-xl font-bold text-indigo-700">SemanticGen</h1>
      <ul className="flex gap-6 text-gray-700 font-medium">
        <li className="hover:text-indigo-600 cursor-pointer">Accueil</li>
        <li className="hover:text-indigo-600 cursor-pointer">Fonctionnalités</li>
        <li className="hover:text-indigo-600 cursor-pointer">Contact</li>
      </ul>
    </nav>
  )
}