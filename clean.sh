#!/bin/bash
# Script de nettoyage de l'arborescence

echo "🧹 Nettoyage de l'arborescence du projet..."

# Supprimer les fichiers cache Python
echo "Suppression des dossiers __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Supprimer les fichiers bytecode Python
echo "Suppression des fichiers .pyc..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Supprimer les fichiers temporaires
echo "Suppression des fichiers temporaires..."
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Supprimer les fichiers de log
echo "Suppression des fichiers de log..."
find . -name "*.log" -delete 2>/dev/null || true

echo "✅ Nettoyage terminé!"