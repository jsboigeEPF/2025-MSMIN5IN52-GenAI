#!/usr/bin/env pwsh
"""
Script de résolution pour la PR #14 - Dev thomas
Auteur: Roo AI Assistant
Date: 2025-11-03
Objectif: Fusionner la PR en gardant le gitignore mais en évitant la suppression du README
"""

Write-Host "=== RÉSOLUTION PR #14 - Dev thomas ===" -ForegroundColor Green
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green

# Configuration
$PR_NUMBER = 14
$PR_BRANCH = "dev_thomas"
$MAIN_BRANCH = "main"
$FORK_OWNER = "Thomas-G27"
$FORK_REPO = "2025-MSMIN5IN52-GenAI-DEHARO-CRISTEA-GOMBERT"
$FORK_REMOTE = "thomas-fork"

# Fonction pour exécuter une commande Git
function Run-GitCommand {
    param(
        [string]$Command
    )
    
    Write-Host "Exécution: git $Command" -ForegroundColor Yellow
    $result = git $Command.Split(" ")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: La commande a échoué" -ForegroundColor Red
        return $false
    }
    return $true
}

# 1. Vérifier l'état actuel du dépôt
Write-Host "`n=== 1. VÉRIFICATION DE L'ÉTAT ACTUEL ===" -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    Write-Host "Le dépôt n'est pas propre. Nettoyage..." -ForegroundColor Yellow
    git stash push -m "Stash temporaire avant résolution PR #$PR_NUMBER"
} else {
    Write-Host "Le dépôt est propre." -ForegroundColor Green
}

# 2. Ajouter le remote du fork et récupérer la branche
Write-Host "`n=== 2. CONFIGURATION DU FORK ET RÉCUPÉRATION ===" -ForegroundColor Cyan
Write-Host "Branche cible: $PR_BRANCH" -ForegroundColor Yellow
Write-Host "Fork: $FORK_OWNER/$FORK_REPO" -ForegroundColor Yellow

# Vérifier si le remote du fork existe déjà
$existing_remotes = git remote -v
$remote_exists = $existing_remotes | Select-String $FORK_REMOTE

if (-not $remote_exists) {
    Write-Host "Ajout du remote $FORK_REMOTE..." -ForegroundColor Yellow
    $fork_url = "https://github.com/$FORK_OWNER/$FORK_REPO.git"
    if (-not (Run-GitCommand "remote add $FORK_REMOTE $fork_url")) {
        Write-Host "Impossible d'ajouter le remote $FORK_REMOTE" -ForegroundColor Red
        exit 1
    }
    Write-Host "Remote $FORK_REMOTE ajouté avec succès." -ForegroundColor Green
} else {
    Write-Host "Remote $FORK_REMOTE existe déjà." -ForegroundColor Green
}

# Récupérer la branche depuis le fork
if (-not (git branch --list | Select-String $PR_BRANCH)) {
    Write-Host "La branche $PR_BRANCH n'existe pas localement. Récupération depuis le fork..." -ForegroundColor Yellow
    if (-not (Run-GitCommand "fetch $FORK_REMOTE $PR_BRANCH")) {
        Write-Host "Impossible de récupérer la branche $PR_BRANCH depuis le fork" -ForegroundColor Red
        exit 1
    }
    if (-not (Run-GitCommand "checkout -b $PR_BRANCH $FORK_REMOTE/$PR_BRANCH")) {
        Write-Host "Impossible de créer la branche locale $PR_BRANCH" -ForegroundColor Red
        exit 1
    }
} else {
    if (-not (Run-GitCommand "checkout $PR_BRANCH")) {
        Write-Host "Impossible de basculer sur la branche $PR_BRANCH" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Branche $PR_BRANCH récupérée avec succès depuis le fork." -ForegroundColor Green

# 3. Analyse des modifications de la PR
Write-Host "`n=== 3. ANALYSE DES MODIFICATIONS ===" -ForegroundColor Cyan
$diff_output = git diff --name-only $MAIN_BRANCH...$PR_BRANCH
$files_changed = $diff_output -split "`n"

Write-Host "Fichiers modifiés dans cette PR:" -ForegroundColor Yellow
foreach ($file in $files_changed) {
    if ($file.Trim()) {
        Write-Host "  - $file" -ForegroundColor White
    }
}

# 4. Fusion avec protection du README
Write-Host "`n=== 4. FUSION AVEC PROTECTION DU README ===" -ForegroundColor Cyan

# Basculer sur la branche principale
if (-not (Run-GitCommand "checkout $MAIN_BRANCH")) {
    Write-Host "Impossible de basculer sur $MAIN_BRANCH" -ForegroundColor Red
    exit 1
}

# Vérifier si README.md existe
$readme_exists = Test-Path "README.md"
if ($readme_exists) {
    Write-Host "README.md trouvé, protection activée." -ForegroundColor Green
    # Sauvegarder temporairement le README
    Copy-Item "README.md" "README.md.backup" -Force
    Write-Host "README.md sauvegardé dans README.md.backup" -ForegroundColor Yellow
} else {
    Write-Host "README.md non trouvé, création d'un README par défaut." -ForegroundColor Yellow
    @"
# Projet 2025-MSMIN5IN52-GenAI

Ce dépôt contient les travaux des groupes d'étudiants du cours de GenAI.

## Structure
- Chaque groupe a son propre répertoire
- Les projets sont fusionnés via des Pull Requests
- Le README principal doit être conservé

## PR Récentes
- PR #14: Dev thomas (en cours de résolution)
"@ | Out-File -FilePath "README.md" -Encoding UTF8
    Write-Host "README.md par défaut créé." -ForegroundColor Green
}

# Tenter la fusion
Write-Host "Tentative de fusion avec $PR_BRANCH..." -ForegroundColor Yellow
$merge_result = git merge $PR_BRANCH --no-ff

if ($LASTEXITCODE -eq 0) {
    Write-Host "Fusion réussie !" -ForegroundColor Green
    
    # Vérifier si le README a été affecté par la fusion
    if ($readme_exists -and (Test-Path "README.md")) {
        $readme_changed = git diff --name-only HEAD~1 HEAD | Select-String "README.md"
        if ($readme_changed) {
            Write-Host "Le README a été modifié pendant la fusion. Restauration..." -ForegroundColor Yellow
            Copy-Item "README.md.backup" "README.md" -Force
            if (-not (Run-GitCommand "add README.md")) {
                Write-Host "Impossible d'ajouter le README restauré" -ForegroundColor Red
                exit 1
            }
            Write-Host "README restauré avec succès." -ForegroundColor Green
        }
    }
    
    # Nettoyer le fichier de sauvegarde
    if (Test-Path "README.md.backup") {
        Remove-Item "README.md.backup" -Force
        Write-Host "Fichier de sauvegarde nettoyé." -ForegroundColor Gray
    }
    
} else {
    Write-Host "La fusion a échoué. Tentative de résolution manuelle..." -ForegroundColor Red
    
    # En cas de conflit, restaurer le README
    if ($readme_exists -and (Test-Path "README.md.backup")) {
        Copy-Item "README.md.backup" "README.md" -Force
        Write-Host "README restauré après échec de fusion." -ForegroundColor Yellow
    }
    
    exit 1
}

# 5. Commit et push
Write-Host "`n=== 5. COMMIT ET PUSH ===" -ForegroundColor Cyan

$commit_message = "Merge pull request #$PR_NUMBER - Dev thomas

- Fusion de la branche $PR_BRANCH
- Conservation du README principal
- Acceptation des modifications du .gitignore

Résolution automatique via script PowerShell"

if (-not (Run-GitCommand "add -A")) {
    Write-Host "Impossible d'ajouter les fichiers modifiés" -ForegroundColor Red
    exit 1
}

if (-not (Run-GitCommand "commit -m `"$commit_message`"")) {
    Write-Host "Impossible de créer le commit" -ForegroundColor Red
    exit 1
}

Write-Host "Push vers le dépôt principal..." -ForegroundColor Yellow
if (-not (Run-GitCommand "push origin $MAIN_BRANCH")) {
    Write-Host "Impossible de pousser les modifications" -ForegroundColor Red
    exit 1
}

# Supprimer le remote du fork après utilisation
Write-Host "Nettoyage du remote $FORK_REMOTE..." -ForegroundColor Gray
Run-GitCommand "remote remove $FORK_REMOTE"

Write-Host "`n=== OPÉRATION TERMINÉE AVEC SUCCÈS ===" -ForegroundColor Green
Write-Host "PR #$PR_NUMBER résolue et fusionnée !" -ForegroundColor Green
Write-Host "URL: https://github.com/jsboigeEPF/2025-MSMIN5IN52-GenAI/pull/$PR_NUMBER" -ForegroundColor Cyan

# 6. Nettoyage final
Write-Host "`n=== 6. NETTOYAGE FINAL ===" -ForegroundColor Cyan
if (-not (Run-GitCommand "checkout $MAIN_BRANCH")) {
    Write-Host "Impossible de revenir sur $MAIN_BRANCH" -ForegroundColor Red
    exit 1
}

# Supprimer la branche locale si elle existe
if (git branch --list | Select-String $PR_BRANCH) {
    Write-Host "Suppression de la branche locale $PR_BRANCH..." -ForegroundColor Gray
    Run-GitCommand "branch -D $PR_BRANCH"
}

Write-Host "Retour sur la branche principale: $MAIN_BRANCH" -ForegroundColor Green
Write-Host "Script terminé avec succès !" -ForegroundColor Green