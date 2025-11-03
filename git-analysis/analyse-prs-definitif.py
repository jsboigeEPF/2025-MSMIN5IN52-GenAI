#!/usr/bin/env python3
"""
Script d'analyse des Pull Requests avec GitHub CLI - Version définitive et fonctionnelle
Auteur: Roo AI Assistant
Date: 2025-11-03
Utilise gh CLI pour récupérer les métadonnées réelles des PR
"""

import subprocess
import re
import sys
import json
from datetime import datetime

# Configuration du chemin GitHub CLI
GH_PATH = r"C:\Program Files\GitHub CLI\gh.exe"

def run_command(cmd):
    """Execute une commande et retourne le stdout"""
    try:
        # Utiliser PowerShell directement pour une meilleure compatibilité
        result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, encoding='utf-8')
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def clean_json_output(output):
    """Nettoie la sortie pour extraire uniquement le JSON"""
    if not output:
        return ""
    
    # Diviser par lignes et chercher la première ligne contenant '{'
    lines = output.split('\n')
    json_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('{') or (json_lines and line):
            json_lines.append(line)
        elif line.startswith('[') or (json_lines and line):
            json_lines.append(line)
    
    # Reconstituer le JSON
    json_str = '\n'.join(json_lines)
    
    # Si toujours vide, essayer la méthode simple
    if not json_str:
        json_start = output.find('{')
        if json_start == -1:
            json_start = output.find('[')
        if json_start == -1:
            return ""
        
        json_end = output.rfind('}') if output.find('{') != -1 else output.rfind(']')
        if json_end == -1:
            return ""
        
        json_str = output[json_start:json_end + 1]
    
    return json_str

def get_git_status():
    """Recupere l'etat actuel du depot Git"""
    status, stdout, stderr = run_command("git status --porcelain")
    branch_status, branch_stdout, _ = run_command("git branch --show-current")
    log_status, log_stdout, _ = run_command("git log --oneline -5")
    
    # Nettoyer les sorties pour enlever les messages de configuration
    stdout_str = clean_git_output(stdout) if isinstance(stdout, str) else str(stdout)
    branch_str = clean_git_output(branch_stdout) if isinstance(branch_stdout, str) else str(branch_stdout)
    log_str = clean_git_output(log_stdout) if isinstance(log_stdout, str) else str(log_stdout)
    
    return {
        'is_clean': len(stdout_str.strip()) == 0,
        'branch': branch_str.strip() if branch_str.strip() else "main",
        'recent_commits': log_str.strip().split('\n') if log_str.strip() else []
    }

def clean_git_output(output):
    """Nettoie la sortie des commandes Git pour enlever les messages de configuration"""
    if not output:
        return ""
    
    lines = output.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        # Ignorer les lignes de configuration PowerShell
        if not line.startswith('Configuration') and not line.startswith('PS'):
            clean_lines.append(line)
    
    return '\n'.join(clean_lines)

def fetch_pr_data_gh():
    """Récupère les données des PR via GitHub CLI"""
    print("Récupération des données des PR via GitHub CLI...")
    
    # Détecter le nom du dépôt depuis git remote
    repo_status, repo_stdout, _ = run_command("git remote get-url origin")
    if repo_status != 0:
        print("Impossible de détecter le dépôt")
        return []
    
    # Extraire owner/repo depuis l'URL GitHub
    repo_match = re.search(r'github\.com[:/]+(.+?)(\.git)?$', repo_stdout.strip())
    if not repo_match:
        print("Format de dépôt non reconnu")
        return []
    
    repo = repo_match.group(1)
    print(f"Dépôt détecté: {repo}")
    
    # Lister les PR ouvertes avec les champs nécessaires
    cmd = f'gh pr list --repo "{repo}" --state open --json number,title,author,createdAt,headRefName,headRefOid'
    status, stdout, stderr = run_command(cmd)
    
    if status != 0:
        print(f"Erreur lors de la liste des PR: {stderr}")
        return []
    
    try:
        # Nettoyer la sortie pour extraire uniquement le JSON
        clean_stdout = clean_json_output(stdout)
        prs_data = json.loads(clean_stdout) if clean_stdout else []
        print(f"Parsing JSON réussi : {len(prs_data)} PR trouvées")
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        print(f"Sortie brute: {stdout[:200]}...")  # Afficher les 200 premiers caractères pour debug
        return []
    
    prs = []
    
    for i, pr in enumerate(prs_data):
        # Ignorer les éléments qui ne sont pas des dictionnaires
        if not isinstance(pr, dict):
            print(f"PR #{i}: Ignoré (type: {type(pr)})")
            continue
            
        pr_number = pr.get('number', 0)
        title = pr.get('title', 'Sans titre')
        author_info = pr.get('author', {})
        author = author_info.get('login', 'Inconnu') if isinstance(author_info, dict) else str(author_info)
        created_at = pr.get('createdAt', '')
        date = created_at.split('T')[0] if created_at else 'Inconnue'
        head_ref = pr.get('headRefName', '')
        commit_hash = pr.get('headRefOid', '')
            
        # Récupérer les fichiers modifiés via gh avec une commande plus robuste
        files_cmd = f'gh pr diff {pr_number} --repo "{repo}" --name-only'
        files_status, files_stdout, files_stderr = run_command(files_cmd)
            
        files = []
        readme_affected = False
        gitignore_affected = False
        directories_added = []
        files_deleted = []
            
        if files_status == 0 and files_stdout.strip():
            try:
                # Nettoyer la sortie pour enlever les messages de configuration
                clean_output = clean_git_output(files_stdout)
                
                # Parser la sortie de git diff --name-only
                file_list = clean_output.strip().split('\n')
                
                for file_path in file_list:
                    file_path = file_path.strip()
                    if not file_path or file_path.startswith('Configuration'):
                        continue
                    
                    # Pour git diff --name-only, tous les fichiers sont considérés comme modifiés
                    status = 'M'
                    
                    files.append({
                        'path': file_path,
                        'status': status
                    })
                   
                    # Détecter les impacts critiques
                    if re.match(r'^README\.md$', file_path) or re.match(r'.*/README\.md$', file_path):
                        readme_affected = True
                   
                    if re.match(r'^\.gitignore$', file_path) or re.match(r'.*/\.gitignore$', file_path):
                        gitignore_affected = True
                   
                    # Détecter les nouveaux répertoires (fichiers sans extension dans des sous-répertoires)
                    if '/' in file_path:
                        filename = file_path.split('/')[-1]
                        if '.' not in filename:  # Pas d'extension = probablement un répertoire
                            directories_added.append(file_path)
               
            except Exception as e:
                print(f"Erreur parsing fichiers pour PR #{pr_number}: {e}")
            
            prs.append({
                'number': pr_number,
                'title': title,
                'author': author,
                'date': date,
                'branch': head_ref,
                'commit_hash': commit_hash,
                'files': files,
                'readme_affected': readme_affected,
                'gitignore_affected': gitignore_affected,
                'directories_added': directories_added,
                'files_deleted': files_deleted,
                'mergeable': True,  # Par défaut, considérer comme mergeable
                'url': f"https://github.com/{repo}/pull/{pr_number}"
            })
    
    return prs

def fetch_merged_prs():
    """Récupère les PR fusionnées"""
    print("Récupération des PR fusionnées...")
    
    # Détecter le nom du dépôt depuis git remote
    repo_status, repo_stdout, _ = run_command("git remote get-url origin")
    if repo_status != 0:
        print("Impossible de détecter le dépôt")
        return []
    
    # Extraire owner/repo depuis l'URL GitHub
    repo_match = re.search(r'github\.com[:/]+(.+?)(\.git)?$', repo_stdout.strip())
    if not repo_match:
        print("Format de dépôt non reconnu")
        return []
    
    repo = repo_match.group(1)
    
    # Lister les PR fusionnées
    cmd = f'gh pr list --repo "{repo}" --state merged --json number,title,author,mergedAt,headRefName'
    status, stdout, stderr = run_command(cmd)
    
    if status != 0:
        print(f"Erreur lors de la liste des PR fusionnées: {stderr}")
        return []
    
    try:
        # Nettoyer la sortie pour extraire uniquement le JSON
        clean_stdout = clean_json_output(stdout)
        merged_data = json.loads(clean_stdout) if clean_stdout else []
        print(f"Parsing JSON fusionnées réussi : {len(merged_data)} PR trouvées")
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON fusionnées: {e}")
        print(f"Sortie brute: {stdout[:200]}...")  # Afficher les 200 premiers caractères pour debug
        return []
    
    merged_prs = []
    for pr in merged_data:
        # Ignorer les éléments qui ne sont pas des dictionnaires
        if not isinstance(pr, dict):
            continue
            
        pr_number = pr.get('number', 0)
        title = pr.get('title', 'Sans titre')
        author_info = pr.get('author', {})
        author = author_info.get('login', 'Inconnu') if isinstance(author_info, dict) else str(author_info)
        merged_at = pr.get('mergedAt', '')
        date = merged_at.split('T')[0] if merged_at else 'Inconnue'
        head_ref = pr.get('headRefName', '')
            
        merged_prs.append({
            'number': pr_number,
            'title': title,
            'author': author,
            'date': date,
            'branch': head_ref,
            'url': f"https://github.com/{repo}/pull/{pr_number}"
            })
    
    return merged_prs

def analyze_conflicts(prs):
    """Analyse les conflits potentiels"""
    print("Analyse des conflits potentiels...")
    
    conflicts = []
    for pr in prs:
        pr_conflicts = []
        
        # Vérifier si le README est affecté
        if pr['readme_affected']:
            pr_conflicts.append("Modification du README principal")
        
        # Vérifier si .gitignore est affecté
        if pr['gitignore_affected']:
            pr_conflicts.append("Modification du .gitignore")
        
        # Vérifier les suppressions de fichiers
        if pr['files_deleted']:
            pr_conflicts.append(f"Suppression de {len(pr['files_deleted'])} fichier(s)")
        
        # Vérifier les ajouts de répertoires au niveau racine
        if pr['directories_added']:
            pr_conflicts.append(f"Ajout de {len(pr['directories_added'])} répertoire(s)")
        
        if pr_conflicts:
            conflicts.append({
                'pr_number': pr['number'],
                'pr_title': pr['title'],
                'conflicts': pr_conflicts
            })
    
    return conflicts

def generate_report(git_status, open_prs, merged_prs, conflicts):
    """Génère le rapport d'analyse"""
    print("\n" + "="*60)
    print("RAPPORT D'ANALYSE DES PULL REQUESTS")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n=== ÉTAT ACTUEL DU DÉPÔT ===")
    print(f"Branche actuelle: {git_status['branch']}")
    print(f"Statut working directory: {'Propre' if git_status['is_clean'] else 'Modifié'}")
    print(f"Derniers commits:")
    for commit in git_status['recent_commits'][:3]:
        print(f"  - {commit}")
    
    print(f"\n=== PULL REQUESTS OUVERTES ({len(open_prs)}) ===")
    if open_prs:
        for pr in open_prs:
            print(f"\nPR #{pr['number']}: {pr['title']}")
            print(f"  Auteur: {pr['author']}")
            print(f"  Date: {pr['date']}")
            print(f"  Branche: {pr['branch']}")
            print(f"  Fichiers modifiés: {len(pr['files'])}")
            for file in pr['files'][:5]:  # Limiter l'affichage
                print(f"    - {file['status']} {file['path']}")
            if len(pr['files']) > 5:
                print(f"    ... et {len(pr['files']) - 5} autres fichiers")
            print(f"  URL: {pr['url']}")
    else:
        print("Aucune PR ouverte trouvée")
    
    print(f"\n=== PULL REQUESTS FUSIONNÉES ({len(merged_prs)}) ===")
    if merged_prs:
        for pr in merged_prs:
            print(f"\nPR #{pr['number']}: {pr['title']}")
            print(f"  Auteur: {pr['author']}")
            print(f"  Date: {pr['date']}")
            print(f"  Branche: {pr['branch']}")
            print(f"  URL: {pr['url']}")
    else:
        print("Aucune PR fusionnée trouvée")
    
    print(f"\n=== CONFLITS POTENTIELS ({len(conflicts)}) ===")
    if conflicts:
        for conflict in conflicts:
            print(f"\nPR #{conflict['pr_number']}: {conflict['pr_title']}")
            for issue in conflict['conflicts']:
                print(f"  ⚠️  {issue}")
    else:
        print("Aucun conflit détecté")
    
    print("\n" + "="*60)
    print("FIN DU RAPPORT")
    print("="*60)

def main():
    """Fonction principale"""
    print("=== ETAT DES LIEUX - DEPOT 2025-MSMIN5IN52-GenAI ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. État actuel du dépôt
    git_status = get_git_status()
    
    # 2. Récupérer les PR ouvertes
    open_prs = fetch_pr_data_gh()
    
    # 3. Récupérer les PR fusionnées
    merged_prs = fetch_merged_prs()
    
    # 4. Analyser les conflits
    conflicts = analyze_conflicts(open_prs)
    
    # 5. Générer le rapport
    generate_report(git_status, open_prs, merged_prs, conflicts)

if __name__ == "__main__":
    main()